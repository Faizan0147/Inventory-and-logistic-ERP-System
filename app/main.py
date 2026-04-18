from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_pool, close_pool
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()   # open connection pool on startup
    yield
    await close_pool()    # close pool on shutdown


app = FastAPI(
    title="Warehouse ERP API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://godaamx.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Warehouse ERP API is running"}
