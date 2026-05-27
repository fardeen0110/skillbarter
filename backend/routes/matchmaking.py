from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..schemas import MatchmakingRequest, MatchmakingResponse, SkillCatalogResponse
from ..services.matchmaking import get_supported_skills, get_top_matches

router = APIRouter(tags=["Matchmaking"])


@router.get("/matchmaking/skills", response_model=SkillCatalogResponse)
def matchmaking_skills(_current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return SkillCatalogResponse(skills=get_supported_skills(db))


@router.post("/matchmaking", response_model=MatchmakingResponse)
def matchmaking(
    payload: MatchmakingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        matches = get_top_matches(
            db,
            skill_offer=payload.skill_offer.strip(),
            skill_want=payload.skill_want.strip(),
            current_user_id=current_user.id,
            limit=5,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return MatchmakingResponse(matches=matches)
