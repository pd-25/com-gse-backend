# app/core/config.py
import os
from dotenv import load_dotenv

# as config is not where main.py, so we have to declaer the path
from pathlib import Path

env_path = Path(".") / ".env"
# print(env_path)
load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_TITLE: str = "Pradipta Blog Apis"
    PROJECT_VERSION: str = "0.1.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    RAZORPAY_KEY_ID: str | None = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET: str | None = os.getenv("RAZORPAY_KEY_SECRET")
    RAZORPAY_PAYMENT_CURRENCY: str = os.getenv("RAZORPAY_PAYMENT_CURRENCY", "INR").upper()
    USD_TO_INR_RATE: str = os.getenv("USD_TO_INR_RATE", "83.00")
    AWS_S3_BUCKET: str | None = os.getenv("AWS_S3_BUCKET")
    AWS_S3_REGION: str = os.getenv("AWS_S3_REGION", "ap-south-1")
    AWS_S3_PUBLIC_BASE_URL: str | None = os.getenv("AWS_S3_PUBLIC_BASE_URL")
    AWS_S3_ENDPOINT_URL: str | None = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_UPLOAD_PREFIX: str = os.getenv("AWS_S3_UPLOAD_PREFIX", "admin-uploads")
    ADMIN_IMAGE_MAX_BYTES: int = int(os.getenv("ADMIN_IMAGE_MAX_BYTES", str(10 * 1024 * 1024)))

settings = Settings()
