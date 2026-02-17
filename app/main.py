import time
import uuid
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine, get_session
from app.logging_config import setup_logging
from app.metrics import REQUESTS_TOTAL, PROCESS_DURATION, DB_QUERY_DURATION
from app.models import Base, Message
from app.schemas import HealthResponse, ProcessRequest, ProcessResponse, MessageOut

setup_logging()
logger = structlog.get_logger()

SEED_MESSAGES = [
    ("Hello world", "alice"),
    ("Testing the API", "bob"),
    ("FastAPI is great", "alice"),
    ("Observability matters", "charlie"),
    ("Logging is important", "bob"),
    ("Metrics help debug", "alice"),
    ("Traces show flow", "charlie"),
    ("Health checks are vital", "bob"),
    ("PostgreSQL rocks", "alice"),
    ("Docker simplifies deployment", "charlie"),
]


@asynccontextmanager
async def lifespan(application: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        result = await session.execute(select(Message).limit(1))
        if result.scalar_one_or_none() is None:
            for text, author in SEED_MESSAGES:
                session.add(Message(text=text, author=author))
            await session.commit()
            logger.info("seeded_messages", count=len(SEED_MESSAGES))
    logger.info("app_started")
    yield
    logger.info("app_shutdown")


app = FastAPI(title="Observability Demo", version="0.1.0", lifespan=lifespan)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    if request.url.path != "/metrics":
        REQUESTS_TOTAL.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code,
        ).inc()
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration=round(duration, 4),
    )
    return response


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/process", response_model=ProcessResponse)
async def process(payload: ProcessRequest):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    result = ProcessResponse(
        request_id=request_id,
        status="completed",
        result=f"processed-{payload.priority}",
        data_length=len(payload.data),
    )
    PROCESS_DURATION.observe(time.perf_counter() - start)
    return result


@app.get("/message/{message_id}", response_model=MessageOut)
async def get_message(message_id: int, session: AsyncSession = Depends(get_session)):
    start = time.perf_counter()
    result = await session.execute(select(Message).where(Message.id == message_id))
    DB_QUERY_DURATION.labels(operation="get_message").observe(
        time.perf_counter() - start
    )
    msg = result.scalar_one_or_none()
    if msg is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


@app.get("/metrics", include_in_schema=False)
async def metrics():
    return PlainTextResponse(
        content=generate_latest(), media_type=CONTENT_TYPE_LATEST
    )
