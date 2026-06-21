from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

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
    allow_origins=[settings.frontend_origin] if settings.frontend_origin != "*" else ["*"],
    allow_credentials=settings.frontend_origin != "*",
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "ok"}


# All application routers live under /api so the SPA can call them same-origin.
app.include_router(auth.router, prefix="/api")
app.include_router(clients.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")
app.include_router(approvals.router, prefix="/api")


# ---- Serve the built React app in production (single public URL) ----
def _resolve_static_dir() -> Path | None:
    if settings.static_dir:
        candidate = Path(settings.static_dir)
        return candidate if candidate.is_dir() else None
    # Fallback: repo-relative frontend/dist (backend/app/main.py -> repo root).
    candidate = Path(__file__).resolve().parents[2] / "frontend" / "dist"
    return candidate if candidate.is_dir() else None


_static_dir = _resolve_static_dir()
if _static_dir is not None:
    assets = _static_dir / "assets"
    if assets.is_dir():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    index_file = _static_dir / "index.html"

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa_fallback(full_path: str) -> FileResponse:
        # Serve real files (favicon, etc.) directly; otherwise SPA index.html.
        requested = _static_dir / full_path
        if full_path and requested.is_file():
            return FileResponse(requested)
        return FileResponse(index_file)
