import logging

from app.infra.postgres.database import Base, engine

logger = logging.getLogger(__name__)


def run_migrations() -> None:
    import app.infra.postgres.models  # noqa: F401 — registra os models no metadata

    Base.metadata.create_all(bind=engine)
    logger.info("Migrations executadas com sucesso")
