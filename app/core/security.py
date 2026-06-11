

from datetime import UTC, datetime, timedelta

from app.core.config import settings
from jose import jwt

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    print(f"expire-- {expire}")
    to_encode.update({"exp": expire})
    encoded_jw_token = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jw_token