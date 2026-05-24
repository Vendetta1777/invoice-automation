import { useEffect, useState } from "react";

import { apiGet } from "../api/client";

type Client = {
  id: number;
  name: string;
  email: string;
};

export default function Clients() {
  const [clients, setClients] = useState<Client[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Client[]>("/clients/")
      .then(setClients)
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section className="page">
      <h2>Clients</h2>
      {error && <div className="placeholder">Could not load clients: {error}</div>}
      {!error && clients.length === 0 && (
        <div className="placeholder">
          No clients yet. Create one via <code>POST /clients/</code>.
        </div>
      )}
      {clients.length > 0 && (
        <ul>
          {clients.map((c) => (
            <li key={c.id}>
              {c.name} — {c.email}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
