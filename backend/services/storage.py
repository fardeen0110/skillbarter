from __future__ import annotations

import os
import uuid
from dataclasses import dataclass

import httpx

from ..config import get_settings

settings = get_settings()


@dataclass(frozen=True)
class StoredAsset:
    storage_path: str
    public_url: str


def storage_enabled() -> bool:
    return False


def _build_public_url(storage_path: str) -> str:
    base = settings.supabase_url.rstrip("/")
    bucket = settings.supabase_storage_bucket
    return f"{base}/storage/v1/object/public/{bucket}/{storage_path}"


def upload_file(*, data: bytes, content_type: str, folder: str, filename: str) -> StoredAsset | None:
    if not storage_enabled():
        return None

    ext = os.path.splitext(filename or "")[1]
    safe_name = f"{folder}/{uuid.uuid4().hex}{ext}"
    upload_url = (
        f"{settings.supabase_url.rstrip('/')}/storage/v1/object/"
        f"{settings.supabase_storage_bucket}/{safe_name}"
    )

    response = httpx.post(
        upload_url,
        content=data,
        headers={
            "Authorization": f"Bearer {settings.supabase_service_role_key}",
            "apikey": settings.supabase_service_role_key,
            "Content-Type": content_type or "application/octet-stream",
            "x-upsert": "true",
        },
        timeout=20,
    )
    response.raise_for_status()
    return StoredAsset(storage_path=safe_name, public_url=_build_public_url(safe_name))
