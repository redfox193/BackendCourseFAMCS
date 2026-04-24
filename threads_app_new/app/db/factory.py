from app.core.config import Settings
from app.db.base import AbstractDatabaseGateway
from app.db.alchemy.gateway import SQLAlchemyGateway


def create_database_gateway(settings: Settings) -> AbstractDatabaseGateway:
    return SQLAlchemyGateway(database_url=settings.database_url)
