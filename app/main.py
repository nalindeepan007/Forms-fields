from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.db.database import createDbSchema, shutdownDatabase

from app.router import forms
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logger import getLogger



logger = getLogger()

@asynccontextmanager
async def lifespanPlan(app: FastAPI):
    try:
        # Startup: Create database schema if not present

        logger.info("app starting up - creating database schema...")
        await createDbSchema()
        yield
        # Shutdown: Close database connections, byebye
        await shutdownDatabase()
        logger.info("Application shutdown completed")
    except Exception as e:
        logger.critical(f"Application lifecycle error: {str(e)}")
        logger.critical(traceback.format_exc())
        raise



app = FastAPI(title="Forms Service", lifespan=lifespanPlan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(forms.router, tags=["Form operations"])

@app.get("/")
def read_root():
    return {"message": "🚀 Forms service 📃 ⚙  Nalin Deepan"}
