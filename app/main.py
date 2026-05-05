from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

from app.database import create_pool, close_pool
from app.api import api_router

BASE_DIR = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_pool()  # open connection pool on startup
    yield
    await close_pool()  # close pool on shutdown


app = FastAPI(
    title="GodaamX",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS — allow your frontend origin(s) to reach the API ────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://godaamx.vercel.app/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    if errors:
        first_error = errors[0]
        field_name = first_error["loc"][-1] if first_error["loc"] else "field"
        return JSONResponse(
            status_code=422, content={"detail": f"{field_name} is required"}
        )
    return JSONResponse(status_code=422, content={"detail": "Validation error"})


@app.middleware("http")
async def auth_cookie_to_header(request: Request, call_next):
    # If Authorization header missing but cookie exists, copy cookie into header
    if "authorization" not in request.headers:
        token = request.cookies.get("access_token")
        if token:
            request.scope.setdefault("headers", [])
            request.scope["headers"].append(
                (b"authorization", f"Bearer {token}".encode())
            )
    return await call_next(request)


@app.get("/", tags=["Health"])
async def root():
    return {"message": "Warehouse ERP API is running"}


@app.get("/chat", include_in_schema=False)
async def chat_ui():
    return FileResponse(BASE_DIR / "chat_ui.html")
