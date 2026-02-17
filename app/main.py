import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session, engine, get_session
from app.models import Base, Message
from app.schemas import HealthResponse, ProcessRequest, ProcessResponse, MessageOut

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
    yield


app = FastAPI(title="Observability Demo", version="0.1.0", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse()


@app.post("/process", response_model=ProcessResponse)
async def process(payload: ProcessRequest):
    request_id = str(uuid.uuid4())
    return ProcessResponse(
        request_id=request_id,
        status="completed",
        result=f"processed-{payload.priority}",
        data_length=len(payload.data),
    )


@app.get("/message/{message_id}", response_model=MessageOut)
async def get_message(message_id: int, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Message).where(Message.id == message_id))
    msg = result.scalar_one_or_none()
    if msg is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg
