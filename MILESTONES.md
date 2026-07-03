# Milestones

The v0.1 invoice builder is live ([demo](https://invoice-automation-qyo2.onrender.com)) — but
software isn't the finish line; **validation with the real business is**. These milestones track
that: each one is a visible, finished thing proven with the business owner.
**`CURRENT-MILESTONE.txt` says where we are; work outside the current milestone gets parked.**

| # | Milestone | Deliverable — a visible, finished thing | Status |
|---|-----------|------------------------------------------|--------|
| M0 | **Discovery** | Discovery questionnaire answered with the business owner + one real invoice captured as the reference sample + manual time-per-invoice baseline measured. No coding needed. | 🔨 In progress |
| M1 | **The real invoice, reproduced** | The builder reproduces the business's actual invoice faithfully — layout, numbering, and every FTA-mandatory tax-invoice field ticked against the reference sample. | ⏳ Not started |
| M2 | **Ten varied invoices** | Ten real, varied invoices generated and visually approved — edge cases (discounts, mixed VAT rates, credit notes) proven. | ⏳ Not started |
| M3 | **Real use** | Real invoices sent to real customers (3+); time saved measured against the M0 manual baseline. | ⏳ Not started |
| M4 | **Multi-tenant SaaS** | Auth + roles, tenant isolation, approval workflow, email delivery — productized for other businesses. | ⏳ Not started |

## Operating rules

1. **One milestone at a time.** Anything out of scope is answered with "that's M[X] — parked."
   (v0.1 was built ahead of discovery — useful demo, but the lesson stands: from here, product
   decisions get grounded in discovery, not guesses.)
2. **A milestone isn't done until it's been seen working** by the developer and the business owner.
3. **No AI features until the core product is validated in production.** AI (line-item extraction,
   anomaly detection, payment prediction) slots in only after M3 proves the workflow.
4. **Private data stays out of this public repo.** The filled discovery doc, real invoices
   (`samples/`), generated output (`outputs/`), and invoice data (`data/`) are gitignored.

## Regulatory context (why the architecture is data-first)

The business operates in the UAE, where e-invoicing becomes mandatory for B2B/B2G businesses of
every size: businesses under AED 50M revenue must appoint an Accredited Service Provider by
**31 March 2027** and exchange structured e-invoices (Peppol PINT AE) from **1 July 2027**.
A PDF will then be a human-readable courtesy copy — the legal invoice is structured data.
So every invoice lives as structured data first (parties, TRNs, line items, per-line VAT), and
the PDF is just one renderer of it. When the mandate lands, adding an ASP integration is a small
step instead of a rewrite.
