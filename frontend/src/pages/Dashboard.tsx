import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { apiGet, apiPostBlob, downloadBlob } from "../api/client";
import type { Invoice } from "../api/types";

const SYMBOLS: Record<string, string> = {
  USD: "$", EUR: "€", GBP: "£", INR: "₹", JPY: "¥",
  AUD: "A$", CAD: "C$", AED: "AED ", SGD: "S$",
};

function money(amount: string, currency: string): string {
  const symbol = SYMBOLS[currency] ?? `${currency} `;
  return `${symbol}${Number(amount).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function Dashboard() {
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Invoice[]>("/invoices/")
      .then(setInvoices)
      .catch((e) => setError((e as Error).message))
      .finally(() => setLoading(false));
  }, []);

  async function download(inv: Invoice) {
    const blob = await apiPostBlob("/invoices/preview-pdf", {
      sender_name: inv.sender_name,
      sender_address: inv.sender_address ?? "",
      sender_email: inv.sender_email ?? "",
      sender_phone: inv.sender_phone ?? "",
      logo_data_url: inv.logo_data_url,
      client_name: inv.client_name,
      client_email: inv.client_email ?? "",
      client_address: inv.client_address ?? "",
      client_phone: inv.client_phone ?? "",
      invoice_number: inv.invoice_number,
      issue_date: inv.issue_date,
      due_date: inv.due_date,
      tax_rate: inv.tax_rate,
      currency: inv.currency,
      notes: inv.notes ?? "",
      line_items: inv.line_items.map((li) => ({
        description: li.description,
        quantity: li.quantity,
        unit_price: li.unit_price,
      })),
    });
    const safeClient = (inv.client_name || "client").replace(/[^a-zA-Z0-9-_]/g, "-");
    downloadBlob(blob, `Invoice-${inv.invoice_number}-${safeClient}.pdf`);
  }

  return (
    <section className="page">
      <div className="builder-head">
        <div>
          <h2>Dashboard</h2>
          <p className="sub">Saved invoices</p>
        </div>
        <Link className="btn primary" to="/invoices">+ New invoice</Link>
      </div>

      {loading && <div className="placeholder">Loading…</div>}
      {error && <div className="banner err">Could not load invoices: {error}</div>}

      {!loading && !error && invoices.length === 0 && (
        <div className="placeholder">
          No invoices yet. <Link to="/invoices">Create your first invoice →</Link>
        </div>
      )}

      {invoices.length > 0 && (
        <table className="data-table">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Client</th>
              <th>Issue date</th>
              <th>Due date</th>
              <th className="r">Total</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {invoices.map((inv) => (
              <tr key={inv.id}>
                <td className="mono">{inv.invoice_number}</td>
                <td>{inv.client_name}</td>
                <td>{inv.issue_date}</td>
                <td>{inv.due_date}</td>
                <td className="r mono">{money(inv.total, inv.currency)}</td>
                <td className="r">
                  <button className="btn small ghost" onClick={() => download(inv)}>PDF</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}
