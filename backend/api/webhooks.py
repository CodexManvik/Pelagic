from __future__ import annotations

import json
import logging
import os

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError
from qstash import Receiver
from sqlalchemy.exc import SQLAlchemyError

from core.config import get_settings
from db.session import AsyncSessionLocal
from services.ingestion import decode_payload, persist_events


logger = logging.getLogger("argo-webhook")
router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
settings = get_settings()


def _build_receiver() -> Receiver:
    current_signing_key = settings.qstash_current_signing_key or os.getenv(
        "QSTASH_CURRENT_SIGNING_KEY"
    )
    next_signing_key = settings.qstash_next_signing_key or os.getenv(
        "QSTASH_NEXT_SIGNING_KEY"
    )

    if not current_signing_key or not next_signing_key:
        raise RuntimeError(
            "Missing QStash signing keys. Expected environment variables: "
            "QSTASH_CURRENT_SIGNING_KEY and QSTASH_NEXT_SIGNING_KEY."
        )

    return Receiver(
        current_signing_key=current_signing_key,
        next_signing_key=next_signing_key,
    )


@router.post("/argo-ingest", status_code=status.HTTP_200_OK)
async def ingest_argo_webhook(request: Request) -> dict[str, str]:
    signature = request.headers.get("Upstash-Signature")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Upstash-Signature header.",
        )

    raw_body_bytes = await request.body()
    raw_body = raw_body_bytes.decode("utf-8")

    try:
        receiver = _build_receiver()
        expected_url = (
            settings.qstash_target_url
            or os.getenv("QSTASH_TARGET_URL")
            or "http://localhost:8000/api/webhooks/argo-ingest"
        )
        receiver.verify(
            body=raw_body,
            signature=signature,
            url=expected_url,
        )
    except HTTPException:
        raise
    except Exception:
        logger.exception("QStash signature verification failed.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid QStash signature.",
        )

    try:
        events = decode_payload(raw_body)
    except (json.JSONDecodeError, ValidationError, ValueError):
        logger.exception("Invalid webhook payload.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook payload.",
        )

    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await persist_events(session, events)
    except SQLAlchemyError as exc:
        # Returning 500 tells QStash delivery should be retried.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database write failed.",
        ) from exc

    logger.info("Committed %d ARGO webhook events.", len(events))

    return {"status": "ok"}
