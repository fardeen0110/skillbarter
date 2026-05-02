from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..auth import get_user_from_token
from ..database import SessionLocal
from ..schemas import MessageResponse
from ..services.realtime import realtime_manager
from ..services.social import are_friends, create_message, get_user_or_none

router = APIRouter(tags=["Chat"])


@router.websocket("/ws/chat")
async def chat_socket(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401, reason="Missing token.")
        return

    db = SessionLocal()
    try:
        current_user = get_user_from_token(token, db)
    except Exception:
        db.close()
        await websocket.close(code=4401, reason="Invalid token.")
        return

    await realtime_manager.connect(current_user.id, websocket)

    try:
        while True:
            payload = await websocket.receive_json()
            recipient_id = int(payload.get("recipient_id", 0))
            content = str(payload.get("content", "")).strip()

            if recipient_id <= 0 or not content:
                await websocket.send_json(
                    {"type": "message:error", "message": "Recipient and content are required."}
                )
                continue

            recipient = get_user_or_none(db, recipient_id)
            if not recipient:
                await websocket.send_json(
                    {"type": "message:error", "message": "Recipient not found."}
                )
                continue

            if not are_friends(db, current_user.id, recipient.id):
                await websocket.send_json(
                    {"type": "message:error", "message": "You can only message accepted connections."}
                )
                continue

            message = create_message(db, current_user, recipient, content)
            outgoing = MessageResponse(
                id=message.id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                content=message.content,
                created_at=message.created_at,
                read_at=message.read_at,
                is_mine=True,
            ).model_dump(mode="json")
            incoming = MessageResponse(
                id=message.id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                content=message.content,
                created_at=message.created_at,
                read_at=message.read_at,
                is_mine=False,
            ).model_dump(mode="json")

            await realtime_manager.send_to_user(
                current_user.id,
                {
                    "type": "message:new",
                    "message": outgoing,
                    "with_user": {"id": recipient.id, "name": recipient.name, "email": recipient.email},
                    "alert": f"Message sent to {recipient.name}.",
                },
            )
            await realtime_manager.send_to_user(
                recipient.id,
                {
                    "type": "message:new",
                    "message": incoming,
                    "with_user": {
                        "id": current_user.id,
                        "name": current_user.name,
                        "email": current_user.email,
                    },
                    "alert": f"New message from {current_user.name}.",
                },
            )
    except WebSocketDisconnect:
        realtime_manager.disconnect(current_user.id, websocket)
    finally:
        db.close()
