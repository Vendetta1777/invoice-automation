# invoice-automation

Automated invoice generation, approval workflow, and delivery system. Built initially for a single small business, designed to extend to multi-tenant SaaS.

## What it does

- **Generates PDF invoices** from client + line-item data
- **Routes invoices for approval** before they go out — a superior signs off before any invoice is sent
- **Emails invoices** to clients automatically once approved
- **Stores everything** (clients, invoices, approvals, payment status) in PostgreSQL
- **Web dashboard** to manage clients, draft invoices, see approval queue, and track payment status

## Stack

- **Backend:** Python 3.11+ · FastAPI · SQLAlchemy · PostgreSQL · Alembic
- **Frontend:** React · Vite · TypeScript
- **Infra:** Docker Compose for local Postgres
- **PDF:** ReportLab
- **Email:** SMTP via `aiosmtplib`

## Repo layout

```
invoice-automation/
├── backend/          FastAPI app
│   ├── app/
│   │   ├── models/       SQLAlchemy ORM models
│   │   ├── schemas/      Pydantic request/response schemas
│   │   ├── routers/      API endpoints (auth, clients, invoices, approvals)
│   │   ├── services/     PDF generation, email sending, approval workflow
│   │   └── core/         Security helpers (JWT, password hashing)
│   └── tests/
├── frontend/         React + Vite + TypeScript dashboard
│   └── src/
│       ├── api/          API client
│       └── pages/        Dashboard, Invoices, Clients, Approvals
├── docker-compose.yml    Local Postgres
└── .env.example          Copy to .env and fill in
```

## Getting started

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker Desktop (for local Postgres)

### 1. Start the database
```bash
docker compose up -d
```

### 2. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env       # edit DB + SMTP creds
uvicorn app.main:app --reload
```
Backend runs at http://localhost:8000 · interactive docs at http://localhost:8000/docs

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at http://localhost:5173

## Roadmap

**v0.1 — Core workflow (in progress)**
- [ ] Auth + roles (admin, accountant, approver)
- [ ] CRUD: clients, invoices, line items
- [ ] PDF generation
- [ ] Approval queue + email-on-approval
- [ ] Email delivery to client

**v0.2 — Production hardening**
- [ ] Multi-tenant data isolation
- [ ] Audit log
- [ ] Payment status tracking + reminders
- [ ] CSV/Excel export

**v0.3 — Intelligence layer** *(planned post-validation)*
- [ ] Smart line-item extraction from existing documents
- [ ] Anomaly detection on invoice amounts
- [ ] Cashflow forecasting

## License

MIT
