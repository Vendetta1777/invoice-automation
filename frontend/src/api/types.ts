export interface LineItemInput {
  description: string;
  quantity: string;
  unit_price: string;
}

export interface InvoicePayload {
  sender_name: string;
  sender_address: string;
  sender_email: string;
  sender_phone: string;
  logo_data_url: string | null;
  client_name: string;
  client_email: string;
  client_address: string;
  client_phone: string;
  invoice_number: string;
  issue_date: string;
  due_date: string;
  tax_rate: string;
  currency: string;
  notes: string;
  line_items: LineItemInput[];
}

export interface LineItemRead {
  id: number;
  description: string;
  quantity: string;
  unit_price: string;
  line_total: string;
}

export interface Invoice {
  id: number;
  invoice_number: string;
  status: string;
  sender_name: string;
  sender_address: string | null;
  sender_email: string | null;
  sender_phone: string | null;
  logo_data_url: string | null;
  client_name: string;
  client_email: string | null;
  client_address: string | null;
  client_phone: string | null;
  issue_date: string;
  due_date: string;
  subtotal: string;
  tax_rate: string;
  tax_amount: string;
  total: string;
  currency: string;
  notes: string | null;
  line_items: LineItemRead[];
  created_at: string;
  updated_at: string;
}
