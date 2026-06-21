# syntax=docker/dockerfile:1

# ---- Stage 1: build the React frontend ----
FROM node:20-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: backend + built frontend, single server ----
FROM python:3.11-slim AS app
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STATIC_DIR=/app/frontend/dist

WORKDIR /app/backend

# Install backend (copy source first so the package builds, then install).
COPY backend/ ./
RUN pip install --upgrade pip && pip install .

# Bring in the compiled SPA produced in stage 1.
COPY --from=frontend /frontend/dist /app/frontend/dist

EXPOSE 8000

# Apply migrations, then serve the API + SPA on the platform-provided $PORT.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
