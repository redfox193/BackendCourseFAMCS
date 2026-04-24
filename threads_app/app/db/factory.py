from app.core.config import Settings
from app.db.base import AbstractDatabaseGateway
from app.db.gateways.asyncpg_gateway.gateway import AsyncpgGateway
from app.db.gateways.sqlalchemy_gateway.gateway import SQLAlchemyGateway


def create_database_gateway(settings: Settings) -> AbstractDatabaseGateway:
    driver = settings.db_driver.lower()
    if driver == "sqlalchemy":
        return SQLAlchemyGateway(database_url=settings.database_url)
    if driver == "asyncpg":
        return AsyncpgGateway(dsn=settings.asyncpg_dsn)
    raise ValueError("Unsupported DB_DRIVER. Use 'sqlalchemy' or 'asyncpg'.")
