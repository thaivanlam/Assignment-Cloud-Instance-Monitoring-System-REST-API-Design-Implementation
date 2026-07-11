from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.database import get_db
from app.models import Member
from app.schemas.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, summary="Login (JWT token issuance)")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    member = db.query(Member).filter(Member.email == body.email).first()
    if member is None or not verify_password(body.password, member.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(member.id, member.email, member.role.value)
    return TokenResponse(accessToken=token, role=member.role, name=member.name)
