from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import approvals, auth, clients, invoices

settings = get_settings()

app = FastAPI(
    title="Invoice Automation API",
    description="Generate, approve, and deliver invoices.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(clients.router)
app.include_router(invoices.router)
app.include_router(approvals.router)
