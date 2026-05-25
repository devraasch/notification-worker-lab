import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infra.postgres.connection import run_migrations
from app.presentation.api.routes.notifications import router as notifications_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    yield


app = FastAPI(
    title="Notification Worker Lab",
    description="API para criação e consulta de notificações com processamento assíncrono via RabbitMQ",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(notifications_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
