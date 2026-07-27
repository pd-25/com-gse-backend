from datetime import UTC, datetime, timedelta
import jwt
from app.core.config import settings
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash

password_hase = PasswordHash.recommended()

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/token")