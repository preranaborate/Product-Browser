import base64
import json
from datetime import datetime

from fastapi import HTTPException, status


def _encode_payload(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"), default=str).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_payload(cursor: str) -> dict:
    try:
        padded = cursor + ("=" * (-len(cursor) % 4))
        raw = base64.urlsafe_b64decode(padded.encode("ascii"))
        return json.loads(raw)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cursor") from exc


def encode_cursor(created_at: datetime, product_id: str, snapshot_at: datetime, snapshot_id: str) -> str:
    return _encode_payload(
        {
            "created_at": created_at.isoformat(),
            "id": product_id,
            "snapshot_at": snapshot_at.isoformat(),
            "snapshot_id": snapshot_id,
        }
    )


def decode_cursor(cursor: str) -> tuple[datetime, str, datetime, str]:
    payload = _decode_payload(cursor)
    try:
        return (
            datetime.fromisoformat(payload["created_at"]),
            payload["id"],
            datetime.fromisoformat(payload["snapshot_at"]),
            payload["snapshot_id"],
        )
    except (KeyError, ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cursor") from exc
