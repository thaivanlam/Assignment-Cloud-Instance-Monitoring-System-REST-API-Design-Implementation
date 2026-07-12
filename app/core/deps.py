import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models import Client, Member, Role

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_member(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Member:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    member = db.get(Member, int(payload["sub"]))
    if member is None:
        raise HTTPException(status_code=401, detail="Member no longer exists")
    return member


def require_admin(member: Member = Depends(get_current_member)) -> Member:
    if member.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="ADMIN role required")
    return member


def assert_client_access(member: Member, client: Client) -> None:
    """ADMIN can access every client; CLIENT_MANAGER only their assigned clients."""
    if member.role == Role.ADMIN:
        return
    if client.managerId != member.id:
        raise HTTPException(
            status_code=403,
            detail="CLIENT_MANAGER can only access clients assigned to them",
        )


def accessible_client_ids(member: Member, db: Session) -> list[int] | None:
    """Returns None for ADMIN (no filter), otherwise the manager's client id list."""
    if member.role == Role.ADMIN:
        return None
    rows = db.query(Client.id).filter(Client.managerId == member.id).all()
    return [r[0] for r in rows]
