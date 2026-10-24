
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, tickets, dashboard

app = FastAPI(
    title="Enterprise ITSM API",
    version="1.0.0",
    description="IT incident and service request management",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(tickets.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "message": "Enterprise ITSM API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
