# invoice-automation

Automated invoice generation, approval workflow, and delivery for a real small business — designed
to extend to multi-tenant SaaS later.

## 🔗 Live demo

**https://invoice-automation-qyo2.onrender.com** — live on Render, no login required. _(Free tier: first load after idle can take ~50s to wake up.)_

Open the app → **Invoices** → upload a logo, fill in your business + client details and line items → watch the live preview → **Download PDF**.

## ✅ What works now (v0.1 core flow)

The end-to-end invoice builder is implemented:

- **In-app branding & details** — enter your business identity, upload a logo (embedded in the PDF), and enter client details inline (no pre-created client record needed).
- **Dynamic line items** with live per-line and invoice totals; tax rate and currency.
- **Server-side math** — subtotal, tax, and grand total are computed on the backend.
- **Live preview** that mirrors the PDF layout as you type.
- **Professional PDF** via ReportLab (logo header, Bill-To block, zebra-striped line-items table, emphasised total, notes footer).
- **Persisted invoices** in PostgreSQL (Alembic-managed schema); Dashboard lists saved invoices with one-click PDF re-download.
- **No login wall** on the demo flow.

Endpoints: `POST /api/invoices/`, `GET /api/invoices/`, `GET /api/invoices/{id}`, `GET /api/invoices/{id}/pdf`, and stateless `POST /api/invoices/preview-pdf`.

Approval workflow, email delivery, and auth remain stubbed (see [Roadmap](#roadmap)).

## 🧭 What's next: grounding v0.1 in the real business

v0.1 is a **generic** invoice builder. The product it needs to become is defined by the real
business it's for — so the current milestone is **discovery** ([`MILESTONES.md`](MILESTONES.md),
`CURRENT-MILESTONE.txt`): interview the owner, capture a real invoice as the reference sample,
measure the manual baseline, then make the builder reproduce that invoice exactly — including the
mandatory UAE FTA tax-invoice fields ("Tax Invoice" title, supplier/customer TRN and address,
per-line VAT in AED, discounts shown) that a generic tax-rate field doesn't cover.

Two standing rules:

- **E-invoicing-ready by design** — invoices live as structured data first, and the PDF is just one
  renderer of it. UAE e-invoicing (Peppol PINT AE via an Accredited Service Provider) becomes
  mandatory for B2B/B2G businesses of every size by **1 July 2027**, so the data model maps to
  that; an ASP integration later is a small step, not a rewrite.
- **Real business data never enters this public repo** — the filled discovery doc, sample invoices,
  and invoice data are gitignored.

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
│   │   ├── services/     PDF generation, invoice math, email sending, approval workflow
│   │   └── core/         Security helpers (JWT, password hashing)
│   ├── migrations/   Alembic schema migrations
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
- PostgreSQL 16 — either Docker Desktop **or** a local install (e.g. `brew install postgresql@16`)

### 1. Start the database

With Docker:
```bash
docker compose up -d
```

Or, without Docker (Homebrew):
```bash
brew install postgresql@16 && brew services start postgresql@16
createuser -s invoice_admin
psql -d postgres -c "ALTER ROLE invoice_admin WITH PASSWORD 'dev_password_change_me';"
createdb -O invoice_admin invoice_automation
```

### 2. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env       # default DATABASE_URL matches the setup above
alembic upgrade head       # create the schema
uvicorn app.main:app --reload
```
Backend runs at http://localhost:8000 · interactive docs at http://localhost:8000/docs · API under `/api`.

### 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at http://localhost:5173 (Vite proxies `/api` → `localhost:8000`).

## Deploy

The app deploys as a **single web service** (FastAPI serves both the `/api` and the built React SPA) plus a managed Postgres. A multi-stage `Dockerfile` builds the frontend and backend into one image; migrations run on startup.

### Render (one-click Blueprint)
1. Push this repo to GitHub.
2. In [Render](https://render.com): **New → Blueprint**, connect the repo. `render.yaml` provisions the web service + free Postgres and wires `DATABASE_URL` automatically.
3. Click **Apply**, wait for the build, then open the service URL. Update the [Live demo](#-live-demo) link above with it.

### Railway (alternative)
New Project → Deploy from GitHub repo (uses the `Dockerfile`) → add a **PostgreSQL** plugin → set the service variable `DATABASE_URL` to `${{Postgres.DATABASE_URL}}` → deploy.

## Roadmap

Business-validation milestones (discovery → real invoice → real use → SaaS) live in
[`MILESTONES.md`](MILESTONES.md); the feature roadmap below tracks the software side.

**v0.1 — Core workflow (in progress)**
- [x] Invoice builder: in-app branding/logo, inline client, line items, tax, currency
- [x] Server-side totals + PDF generation (ReportLab)
- [x] Persist invoices to Postgres + list on dashboard
- [x] Deployable single-service build (Docker) for a public demo
- [ ] FTA-compliant UAE tax-invoice layout (after M0 discovery: "Tax Invoice" title, TRNs, per-line VAT in AED)
- [ ] Auth + roles (admin, accountant, approver)
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
