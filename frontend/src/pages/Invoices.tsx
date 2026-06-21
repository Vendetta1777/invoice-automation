import { useMemo, useState } from "react";

import { apiPost, apiPostBlob, downloadBlob } from "../api/client";
import type { Invoice, InvoicePayload, LineItemInput } from "../api/types";

const CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "AED", "SGD"];
const SYMBOLS: Record<string, string> = {
  USD: "$", EUR: "€", GBP: "£", INR: "₹", JPY: "¥",
  AUD: "A$", CAD: "C$", AED: "AED ", SGD: "S$",
};

function todayISO(offsetDays = 0): string {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  return d.toISOString().slice(0, 10);
}

function suggestNumber(): string {
  const year = new Date().getFullYear();
  const rnd = String(Math.floor(1 + Math.random() * 9999)).padStart(4, "0");
  return `INV-${year}-${rnd}`;
}

function money(amount: number, currency: string): string {
  const symbol = SYMBOLS[currency] ?? `${currency} `;
  return `${symbol}${amount.toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

const emptyLine = (): LineItemInput => ({ description: "", quantity: "1", unit_price: "0" });

const initialState: InvoicePayload = {
  sender_name: "",
  sender_address: "",
  sender_email: "",
  sender_phone: "",
  logo_data_url: null,
  client_name: "",
  client_email: "",
  client_address: "",
  client_phone: "",
  invoice_number: suggestNumber(),
  issue_date: todayISO(),
  due_date: todayISO(14),
  tax_rate: "0",
  currency: "USD",
  notes: "Payment due within 14 days. Thank you for your business.",
  line_items: [emptyLine()],
};

export default function Invoices() {
  const [form, setForm] = useState<InvoicePayload>(initialState);
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<{ kind: "ok" | "err"; text: string } | null>(null);

  function set<K extends keyof InvoicePayload>(key: K, value: InvoicePayload[K]) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  function setLine(index: number, key: keyof LineItemInput, value: string) {
    setForm((f) => {
      const items = f.line_items.map((it, i) => (i === index ? { ...it, [key]: value } : it));
      return { ...f, line_items: items };
    });
  }

  function addLine() {
    setForm((f) => ({ ...f, line_items: [...f.line_items, emptyLine()] }));
  }

  function removeLine(index: number) {
    setForm((f) => ({
      ...f,
      line_items: f.line_items.filter((_, i) => i !== index),
    }));
  }

  function onLogoChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) {
      setMessage({ kind: "err", text: "Logo must be an image file." });
      return;
    }
    const reader = new FileReader();
    reader.onload = () => {
      const dataUrl = reader.result as string;
      set("logo_data_url", dataUrl);
      setLogoPreview(dataUrl);
    };
    reader.readAsDataURL(file);
  }

  function clearLogo() {
    set("logo_data_url", null);
    setLogoPreview(null);
  }

  // ---- Live totals (mirror of the server-side math) ----
  const totals = useMemo(() => {
    const lines = form.line_items.map((it) => {
      const qty = parseFloat(it.quantity) || 0;
      const unit = parseFloat(it.unit_price) || 0;
      return Math.round(qty * unit * 100) / 100;
    });
    const subtotal = Math.round(lines.reduce((a, b) => a + b, 0) * 100) / 100;
    const rate = parseFloat(form.tax_rate) || 0;
    const tax = Math.round((subtotal * rate) / 100 * 100) / 100;
    const total = Math.round((subtotal + tax) * 100) / 100;
    return { lines, subtotal, tax, total };
  }, [form.line_items, form.tax_rate]);

  function validate(): string | null {
    const valid = form.line_items.filter(
      (it) => it.description.trim() !== "" || parseFloat(it.unit_price) > 0,
    );
    if (valid.length === 0) return "Add at least one line item with a description.";
    if (!form.sender_name.trim()) return "Enter your business name.";
    if (!form.client_name.trim()) return "Enter the client name.";
    if (!form.issue_date || !form.due_date) return "Set both issue and due dates.";
    return null;
  }

  function payloadForApi(): InvoicePayload {
    return {
      ...form,
      line_items: form.line_items.filter(
        (it) => it.description.trim() !== "" || parseFloat(it.unit_price) > 0,
      ),
    };
  }

  async function handleDownload() {
    const error = validate();
    if (error) {
      setMessage({ kind: "err", text: error });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const payload = payloadForApi();
      // Persist the invoice (so it appears on the dashboard)…
      const saved = await apiPost<Invoice>("/invoices/", payload);
      // …then download the canonical PDF for the saved invoice.
      const blob = await apiPostBlob("/invoices/preview-pdf", {
        ...payload,
        invoice_number: saved.invoice_number,
      });
      const safeClient = (saved.client_name || "client").replace(/[^a-zA-Z0-9-_]/g, "-");
      downloadBlob(blob, `Invoice-${saved.invoice_number}-${safeClient}.pdf`);
      set("invoice_number", saved.invoice_number);
      setMessage({ kind: "ok", text: `Saved & downloaded ${saved.invoice_number}.` });
    } catch (err) {
      setMessage({ kind: "err", text: `Could not generate PDF: ${(err as Error).message}` });
    } finally {
      setBusy(false);
    }
  }

  async function handlePreviewPdf() {
    const error = validate();
    if (error) {
      setMessage({ kind: "err", text: error });
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      const blob = await apiPostBlob("/invoices/preview-pdf", payloadForApi());
      window.open(URL.createObjectURL(blob), "_blank");
    } catch (err) {
      setMessage({ kind: "err", text: `Preview failed: ${(err as Error).message}` });
    } finally {
      setBusy(false);
    }
  }

  const sym = SYMBOLS[form.currency] ?? `${form.currency} `;

  return (
    <section className="invoice-builder">
      <div className="builder-head">
        <div>
          <h2>Invoice Builder</h2>
          <p className="sub">Fill in the details, watch the preview update, then download a PDF.</p>
        </div>
        <div className="actions">
          <button className="btn ghost" onClick={handlePreviewPdf} disabled={busy}>
            Open PDF preview
          </button>
          <button className="btn primary" onClick={handleDownload} disabled={busy}>
            {busy ? "Working…" : "Download PDF"}
          </button>
        </div>
      </div>

      {message && <div className={`banner ${message.kind}`}>{message.text}</div>}

      <div className="two-pane">
        {/* ---------------- LEFT: FORM ---------------- */}
        <div className="form-pane">
          <fieldset>
            <legend>Your business</legend>
            <div className="logo-row">
              <div className="logo-box">
                {logoPreview ? (
                  <img src={logoPreview} alt="logo preview" />
                ) : (
                  <span className="logo-empty">No logo</span>
                )}
              </div>
              <div className="logo-controls">
                <label className="btn small">
                  Upload logo
                  <input type="file" accept="image/*" onChange={onLogoChange} hidden />
                </label>
                {logoPreview && (
                  <button className="btn small ghost" onClick={clearLogo}>
                    Remove
                  </button>
                )}
              </div>
            </div>
            <input className="inp" placeholder="Business name *"
              value={form.sender_name} onChange={(e) => set("sender_name", e.target.value)} />
            <textarea className="inp" placeholder="Business address" rows={2}
              value={form.sender_address} onChange={(e) => set("sender_address", e.target.value)} />
            <div className="grid-2">
              <input className="inp" placeholder="Email"
                value={form.sender_email} onChange={(e) => set("sender_email", e.target.value)} />
              <input className="inp" placeholder="Phone"
                value={form.sender_phone} onChange={(e) => set("sender_phone", e.target.value)} />
            </div>
          </fieldset>

          <fieldset>
            <legend>Bill to</legend>
            <input className="inp" placeholder="Client name *"
              value={form.client_name} onChange={(e) => set("client_name", e.target.value)} />
            <textarea className="inp" placeholder="Client address" rows={2}
              value={form.client_address} onChange={(e) => set("client_address", e.target.value)} />
            <div className="grid-2">
              <input className="inp" placeholder="Client email"
                value={form.client_email} onChange={(e) => set("client_email", e.target.value)} />
              <input className="inp" placeholder="Client phone"
                value={form.client_phone} onChange={(e) => set("client_phone", e.target.value)} />
            </div>
          </fieldset>

          <fieldset>
            <legend>Invoice details</legend>
            <div className="grid-2">
              <label className="field">
                <span>Invoice #</span>
                <input className="inp" value={form.invoice_number}
                  onChange={(e) => set("invoice_number", e.target.value)} />
              </label>
              <label className="field">
                <span>Currency</span>
                <select className="inp" value={form.currency}
                  onChange={(e) => set("currency", e.target.value)}>
                  {CURRENCIES.map((c) => <option key={c} value={c}>{c}</option>)}
                </select>
              </label>
              <label className="field">
                <span>Issue date</span>
                <input className="inp" type="date" value={form.issue_date}
                  onChange={(e) => set("issue_date", e.target.value)} />
              </label>
              <label className="field">
                <span>Due date</span>
                <input className="inp" type="date" value={form.due_date}
                  onChange={(e) => set("due_date", e.target.value)} />
              </label>
            </div>
          </fieldset>

          <fieldset>
            <legend>Line items</legend>
            <div className="items-head">
              <span className="c-desc">Description</span>
              <span className="c-qty">Qty</span>
              <span className="c-price">Unit price</span>
              <span className="c-total">Amount</span>
              <span className="c-rm" />
            </div>
            {form.line_items.map((it, i) => (
              <div className="item-row" key={i}>
                <input className="inp c-desc" placeholder="Item description"
                  value={it.description} onChange={(e) => setLine(i, "description", e.target.value)} />
                <input className="inp c-qty" type="number" min="0" step="any"
                  value={it.quantity} onChange={(e) => setLine(i, "quantity", e.target.value)} />
                <input className="inp c-price" type="number" min="0" step="any"
                  value={it.unit_price} onChange={(e) => setLine(i, "unit_price", e.target.value)} />
                <span className="c-total amount">{money(totals.lines[i] ?? 0, form.currency)}</span>
                <button className="rm-btn c-rm" title="Remove" onClick={() => removeLine(i)}
                  disabled={form.line_items.length === 1}>×</button>
              </div>
            ))}
            <button className="btn small ghost add" onClick={addLine}>+ Add line item</button>
          </fieldset>

          <fieldset>
            <legend>Tax & notes</legend>
            <label className="field">
              <span>Tax rate (%)</span>
              <input className="inp narrow" type="number" min="0" step="any"
                value={form.tax_rate} onChange={(e) => set("tax_rate", e.target.value)} />
            </label>
            <textarea className="inp" placeholder="Notes / payment terms" rows={3}
              value={form.notes} onChange={(e) => set("notes", e.target.value)} />
          </fieldset>
        </div>

        {/* ---------------- RIGHT: LIVE PREVIEW ---------------- */}
        <div className="preview-pane">
          <div className="paper">
            <div className="pv-head">
              <div className="pv-biz">
                {logoPreview && <img className="pv-logo" src={logoPreview} alt="logo" />}
                <div className="pv-biz-name">{form.sender_name || "Your Business"}</div>
                <div className="pv-muted">
                  {form.sender_address && <div>{form.sender_address}</div>}
                  {form.sender_email && <div>{form.sender_email}</div>}
                  {form.sender_phone && <div>{form.sender_phone}</div>}
                </div>
              </div>
              <div className="pv-title-block">
                <div className="pv-title">INVOICE</div>
                <table className="pv-meta">
                  <tbody>
                    <tr><td>Invoice No.</td><td>{form.invoice_number || "—"}</td></tr>
                    <tr><td>Issue Date</td><td>{form.issue_date}</td></tr>
                    <tr><td>Due Date</td><td>{form.due_date}</td></tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div className="pv-rule" />

            <div className="pv-section-label">BILL TO</div>
            <div className="pv-client-name">{form.client_name || "—"}</div>
            <div className="pv-muted">
              {form.client_address && <div>{form.client_address}</div>}
              {form.client_email && <div>{form.client_email}</div>}
              {form.client_phone && <div>{form.client_phone}</div>}
            </div>

            <table className="pv-items">
              <thead>
                <tr>
                  <th className="l">DESCRIPTION</th>
                  <th className="r">QTY</th>
                  <th className="r">UNIT PRICE</th>
                  <th className="r">AMOUNT</th>
                </tr>
              </thead>
              <tbody>
                {form.line_items.filter((it) => it.description || parseFloat(it.unit_price) > 0)
                  .map((it, i) => (
                  <tr key={i}>
                    <td className="l">{it.description || "—"}</td>
                    <td className="r">{it.quantity || "0"}</td>
                    <td className="r">{money(parseFloat(it.unit_price) || 0, form.currency)}</td>
                    <td className="r">
                      {money(
                        Math.round((parseFloat(it.quantity) || 0) * (parseFloat(it.unit_price) || 0) * 100) / 100,
                        form.currency,
                      )}
                    </td>
                  </tr>
                ))}
                {form.line_items.filter((it) => it.description || parseFloat(it.unit_price) > 0).length === 0 && (
                  <tr><td className="l empty" colSpan={4}>No line items yet</td></tr>
                )}
              </tbody>
            </table>

            <div className="pv-totals">
              <div className="pv-totrow"><span>Subtotal</span><span>{money(totals.subtotal, form.currency)}</span></div>
              <div className="pv-totrow"><span>Tax ({form.tax_rate || 0}%)</span><span>{money(totals.tax, form.currency)}</span></div>
              <div className="pv-grand"><span>TOTAL DUE</span><span>{money(totals.total, form.currency)}</span></div>
            </div>

            {form.notes && (
              <div className="pv-notes">
                <div className="pv-section-label">NOTES &amp; PAYMENT TERMS</div>
                <div>{form.notes}</div>
              </div>
            )}
            <div className="pv-foot">
              Thank you for your business{form.sender_name ? ` — ${form.sender_name}` : ""}
            </div>
            <div className="pv-currency-note">All amounts in {form.currency} ({sym.trim()})</div>
          </div>
        </div>
      </div>
    </section>
  );
}
