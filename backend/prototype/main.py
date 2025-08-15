from contextlib import asynccontextmanager
from fastapi import FastAPI
from prototype.core.database import Database
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from prototype.api.v1.endpoints import router as endpoint_router
from prototype.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await Database.init_database()
    
    yield
    await Database.terminate_db()

app = FastAPI(
    title="Stravah Global API",
    description="The first Arkansas Unicorn",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(endpoint_router, prefix="/api/v1/general")

if __name__ == "__main__" :
    print(settings.HOST)

    uvicorn.run(
        "prototype.main:app",
        host=settings.HOST, 
        port=settings.PORT,
        proxy_headers=True,
        reload=True
    )