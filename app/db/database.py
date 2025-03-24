import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine
from urllib.parse import urlparse
from app.db.dbModel import Base
from app.utils.logger import getLogger




logger = getLogger()


try:
    tmpPostgres = urlparse(os.getenv("DATABASE_URL"))


    syncEngine = create_engine(f"postgresql://{tmpPostgres.username}:{tmpPostgres.password}@{tmpPostgres.hostname}{tmpPostgres.path}", echo=True)
    engineForAsyncDBCreation = create_async_engine(f"postgresql+asyncpg://{tmpPostgres.username}:{tmpPostgres.password}@{tmpPostgres.hostname}{tmpPostgres.path}?ssl=require", echo=True)

    logger.info("Database engine created successfully")
except Exception as e:
    logger.critical(f"Failed to create database engines: {str(e)}")
    raise

async def createDbSchema() -> None:
    """ create the initial db schema postgress"""
    try:
        logger.info("Creating database schema")
        async with engineForAsyncDBCreation.begin() as conn:
            
                await conn.run_sync(Base.metadata.create_all)
        await engineForAsyncDBCreation.dispose()
        logger.info("Database schema created successfully!!!")
    except Exception as e:
        logger.critical(f"Failed to create database schema: {str(e)}")
        raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=syncEngine)


def getDb():
    
    db = SessionLocal()
    try:
        logger.debug("Database session created")
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        logger.debug("Database session closed")
        db.close()

async def shutdownDatabase():
    """Properly close database engine"""
    try:
        logger.info("Shutting down database connections")
        await engineForAsyncDBCreation.dispose()
    except Exception as e:
        logger.error(f"Error duringg databasw shutdown: {str(e)}")
