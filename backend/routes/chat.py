from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..auth import get_user_from_token
from ..database import SessionLocal
from ..services.rate_limit import websocket_limit_for
from ..services.realtime import realtime_manager
from ..services.social import (
    are_friends,
    build_friend_overview,
    create_message,
    get_messages_between_users,
    get_user_or_none,
    mark_messages_as_read,
)
from ..services.users import serialize_user_mini

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

    overview = build_friend_overview(db, current_user)
    peer_ids = [item["id"] for item in overview["friends"]]

    await realtime_manager.connect(current_user.id, websocket)
    await realtime_manager.broadcast_presence(current_user.id, is_online=True, peers=peer_ids)

    try:
        while True:
            payload = await websocket.receive_json()
            websocket_limit_for(f"user:{current_user.id}")
            event_type = payload.get("type", "message")

            if event_type == "typing":
                recipient_id = int(payload.get("recipient_id", 0))
                if recipient_id > 0:
                    await realtime_manager.set_typing(
                        sender_id=current_user.id,
                        recipient_id=recipient_id,
                        is_typing=bool(payload.get("is_typing", True)),
                    )
                continue

            if event_type == "read":
                recipient_id = int(payload.get("recipient_id", 0))
                if recipient_id > 0:
                    read_ids = mark_messages_as_read(db, reader_id=current_user.id, other_user_id=recipient_id)
                    if read_ids:
                        await realtime_manager.send_to_user(
                            recipient_id,
                            {
                                "type": "message:read",
                                "message_ids": read_ids,
                                "user_id": current_user.id,
                            },
                        )
                continue

            recipient_id = int(payload.get("recipient_id", 0))
            content = str(payload.get("content", "")).strip()

            if recipient_id <= 0 or not content:
                await websocket.send_json({"type": "message:error", "message": "Recipient and content are required."})
                continue

            recipient = get_user_or_none(db, recipient_id)
            if not recipient:
                await websocket.send_json({"type": "message:error", "message": "Recipient not found."})
                continue

            if not are_friends(db, current_user.id, recipient.id):
                await websocket.send_json({"type": "message:error", "message": "You can only message accepted connections."})
                continue

            message = create_message(db, current_user, recipient, content)
            outgoing = {
                "id": message.id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "content": message.content,
                "created_at": message.created_at.isoformat(),
                "delivered_at": message.delivered_at.isoformat() if message.delivered_at else None,
                "read_at": message.read_at.isoformat() if message.read_at else None,
                "is_mine": True,
                "message_type": message.message_type,
                "attachment_url": None,
                "attachment_filename": None,
            }
            incoming = {**outgoing, "is_mine": False}

            await realtime_manager.send_to_user(
                current_user.id,
                {
                    "type": "message:new",
                    "message": outgoing,
                    "with_user": serialize_user_mini(recipient).model_dump(mode="json"),
                    "alert": f"Message sent to {recipient.name}.",
                },
            )
            await realtime_manager.send_to_user(
                recipient.id,
                {
                    "type": "message:new",
                    "message": incoming,
                    "with_user": serialize_user_mini(current_user).model_dump(mode="json"),
                    "alert": f"New message from {current_user.name}.",
                },
            )
    except WebSocketDisconnect:
        realtime_manager.disconnect(current_user.id, websocket)
        await realtime_manager.broadcast_presence(current_user.id, is_online=False, peers=peer_ids)
    finally:
        db.close()
