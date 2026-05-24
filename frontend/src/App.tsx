import { Link, Route, Routes } from "react-router-dom";

import Approvals from "./pages/Approvals";
import Clients from "./pages/Clients";
import Dashboard from "./pages/Dashboard";
import Invoices from "./pages/Invoices";

export default function App() {
  return (
    <div className="app">
      <header className="topbar">
        <h1>Invoice Automation</h1>
        <nav>
          <Link to="/">Dashboard</Link>
          <Link to="/invoices">Invoices</Link>
          <Link to="/clients">Clients</Link>
          <Link to="/approvals">Approvals</Link>
        </nav>
      </header>

      <main className="content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/invoices" element={<Invoices />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/approvals" element={<Approvals />} />
        </Routes>
      </main>
    </div>
  );
}
