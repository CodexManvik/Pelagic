from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from schemas.query import QueryRequest, QueryResponse
from services.query import run_query


router = APIRouter(prefix="/api/v1", tags=["query"])


@router.post("/query", response_model=QueryResponse, status_code=status.HTTP_200_OK)
async def query(
    payload: QueryRequest,
    session: AsyncSession = Depends(get_db_session),
) -> QueryResponse:
    try:
        return await run_query(payload, session=session)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
