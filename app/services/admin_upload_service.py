import re
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from app.core.config import settings


ALLOWED_IMAGE_TYPES = {
    "image/jpeg": {".jpg", ".jpeg"},
    "image/png": {".png"},
    "image/webp": {".webp"},
    "image/gif": {".gif"},
    "image/avif": {".avif"},
}


def _has_valid_signature(content: bytes, content_type: str) -> bool:
    if content_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/gif":
        return content.startswith((b"GIF87a", b"GIF89a"))
    if content_type == "image/webp":
        return content.startswith(b"RIFF") and content[8:12] == b"WEBP"
    if content_type == "image/avif":
        return len(content) > 12 and content[4:12] in {b"ftypavif", b"ftypavis"}
    return False


def _public_url(key: str) -> str:
    if settings.AWS_S3_PUBLIC_BASE_URL:
        return f"{settings.AWS_S3_PUBLIC_BASE_URL.rstrip('/')}/{key}"
    bucket = settings.AWS_S3_BUCKET
    if settings.AWS_S3_REGION == "us-east-1":
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    return f"https://{bucket}.s3.{settings.AWS_S3_REGION}.amazonaws.com/{key}"


async def upload_admin_image(file: UploadFile, scope: str) -> dict:
    if not settings.AWS_S3_BUCKET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AWS_S3_BUCKET is not configured for admin uploads",
        )
    content_type = (file.content_type or "").lower()
    extension = Path(file.filename or "").suffix.lower()
    if content_type not in ALLOWED_IMAGE_TYPES or extension not in ALLOWED_IMAGE_TYPES[content_type]:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a JPG, PNG, WebP, GIF, or AVIF image",
        )
    content = await file.read(settings.ADMIN_IMAGE_MAX_BYTES + 1)
    await file.close()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded image is empty")
    if len(content) > settings.ADMIN_IMAGE_MAX_BYTES:
        max_mb = settings.ADMIN_IMAGE_MAX_BYTES // (1024 * 1024)
        raise HTTPException(status_code=413, detail=f"Image exceeds the {max_mb} MB limit")
    if not _has_valid_signature(content, content_type):
        raise HTTPException(status_code=400, detail="File content does not match its image type")

    safe_scope = re.sub(r"[^a-z0-9-]+", "-", scope.lower()).strip("-") or "general"
    safe_stem = re.sub(r"[^a-z0-9-]+", "-", Path(file.filename or "image").stem.lower()).strip("-")[:60] or "image"
    date_path = datetime.now(UTC).strftime("%Y/%m/%d")
    key = f"{settings.AWS_S3_UPLOAD_PREFIX.strip('/')}/{safe_scope}/{date_path}/{uuid4().hex}-{safe_stem}{extension}"
    try:
        client = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        )
        await run_in_threadpool(
            client.put_object,
            Bucket=settings.AWS_S3_BUCKET,
            Key=key,
            Body=content,
            ContentType=content_type,
            CacheControl="public, max-age=31536000, immutable",
            Metadata={"uploaded-by": "gse-admin"},
        )
    except (BotoCoreError, ClientError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AWS S3 rejected the image upload; check bucket credentials and permissions",
        ) from error
    return {
        "url": _public_url(key),
        "key": key,
        "content_type": content_type,
        "size": len(content),
    }
