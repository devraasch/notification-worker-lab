import logging

from fastapi import FastAPI

from app.presentation.api.routes.notifications import router as notifications_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="Notification Worker Lab",
    description="API para criação e consulta de notificações com processamento assíncrono via RabbitMQ",
    version="0.1.0",
)

app.include_router(notifications_router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
