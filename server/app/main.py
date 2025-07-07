from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api import vocabulary, quiz, auth
from app.scripts.import_words import import_words_if_empty
from app.db.mongodb import db
from app.db.init import create_indexes

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 FastAPI startup: checking database...")
    await import_words_if_empty()
    await create_indexes(db)
    yield
    print("🛑 FastAPI shutdown (optional)")

app = FastAPI(
    title="Te Reo Māori Learning API",
    description="RESTful API for Māori vocabulary and culture learning",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(
    vocabulary.router,
    prefix="/vocabulary",
    tags=["Vocabulary"]
)

app.include_router(
    quiz.router,
    prefix="/quiz",
    tags=["Quiz"]
)

app.include_router(
    auth.router,
    tags=["Authentication"]
)
