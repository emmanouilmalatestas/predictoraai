"use client";

import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [status, setStatus] = useState("Checking...");

  useEffect(() => {
    fetch("https://api.predictoraai.com/v1/health")
      .then(r => r.json())
      .then(d => setStatus(d.status))
      .catch(() => setStatus("unreachable"));
  }, []);

  return (
    <main className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="border border-slate-800 p-4 rounded">
        Backend status: {status}
      </div>
    </main>
  );
}
