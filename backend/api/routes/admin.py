from fastapi import APIRouter, status

from worker.cleanup import run_cleanup


router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.post("/cleanup", status_code=status.HTTP_202_ACCEPTED)
async def cleanup() -> dict[str, str]:
    await run_cleanup()
    return {"status": "scheduled"}
