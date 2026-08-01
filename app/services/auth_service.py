import re
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.session import get_db
from app.models.country import Country
from app.models.revoked_token import RevokedToken
from app.models.user import User
from app.schemas.auth_schema import LoginRequest, RefreshTokenRequest, RegisterRequest


password_hash = PasswordHash.recommended()
bearer_scheme = HTTPBearer(auto_error=False)


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "user"


def _create_token(user: User, token_type: str, expires_delta: timedelta) -> str:
    issued_at = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(user.id),
            "email": user.email,
            "type": token_type,
            "iat": issued_at,
            "exp": issued_at + expires_delta,
            "jti": uuid4().hex,
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def _create_token_pair(user: User) -> tuple[str, str]:
    return (
        _create_token(
            user,
            token_type="access",
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        ),
        _create_token(
            user,
            token_type="refresh",
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ),
    )


def _get_token_user(token: str, expected_type: str, db: Session) -> tuple[User, dict]:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid or expired {expected_type} token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        # Tokens issued before token types were introduced remain valid as access
        # tokens until their original short expiry time.
        token_type = payload.get("type", "access")
        user_id = int(payload.get("sub", ""))
    except (jwt.InvalidTokenError, TypeError, ValueError):
        raise unauthorized
    if token_type != expected_type:
        raise unauthorized
    token_id = payload.get("jti")
    if token_id and db.query(RevokedToken.jti).filter(RevokedToken.jti == token_id).first():
        raise unauthorized

    user = db.query(User).filter(User.id == user_id, User.deleted_at.is_(None)).first()
    if user is None or not user.is_active:
        raise unauthorized
    return user, payload


def _revoke_token(payload: dict, db: Session) -> None:
    token_id = payload.get("jti")
    expires_at = payload.get("exp")
    token_type = payload.get("type")
    if not token_id or not expires_at or not token_type:
        return
    if db.get(RevokedToken, token_id) is None:
        db.add(
            RevokedToken(
                jti=token_id,
                token_type=token_type,
                expires_at=datetime.fromtimestamp(expires_at, tz=UTC).replace(tzinfo=None),
            )
        )
        db.commit()


def register_user(payload: RegisterRequest, db: Session) -> tuple[User, str, str]:
    email = payload.email.lower()
    if db.query(User.id).filter(User.email == email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email address is already registered")
    slug = _slugify(payload.username)
    if db.query(User.id).filter(User.slug == slug).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username is already registered")

    country = db.query(Country).filter(Country.deleted_at.is_(None)).order_by(Country.id).first()
    if country is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Registration is temporarily unavailable")

    user = User(
        slug=slug,
        first_name=payload.username,
        email=email,
        country_id=country.id,
        password=password_hash.hash(payload.password),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    access_token, refresh_token = _create_token_pair(user)
    return user, access_token, refresh_token


def authenticate_user(payload: LoginRequest, db: Session) -> tuple[User, str, str]:
    identifier = payload.identifier
    username_slug = _slugify(identifier)
    user = (
        db.query(User)
        .filter(
            User.deleted_at.is_(None),
            or_(User.email == identifier, User.slug == username_slug),
        )
        .first()
    )
    if user is None or not password_hash.verify(payload.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username/email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive")
    access_token, refresh_token = _create_token_pair(user)
    return user, access_token, refresh_token


def refresh_user_tokens(payload: RefreshTokenRequest, db: Session) -> tuple[User, str, str]:
    user, token_payload = _get_token_user(payload.refresh_token, expected_type="refresh", db=db)
    _revoke_token(token_payload, db)
    access_token, refresh_token = _create_token_pair(user)
    return user, access_token, refresh_token


def logout_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user, token_payload = _get_token_user(
        credentials.credentials,
        expected_type="access",
        db=db,
    )
    _revoke_token(token_payload, db)
    return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user, _payload = _get_token_user(credentials.credentials, expected_type="access", db=db)
    return user
