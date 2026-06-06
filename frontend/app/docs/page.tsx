export default function DocsPage() {
  return (
    <main className="space-y-6">
      <h1 className="text-3xl font-bold">API Documentation</h1>
      <pre className="bg-slate-900 p-4 rounded text-xs">
curl -H "x-api-key: YOUR_KEY" https://api.predictoraai.com/v1/signals
      </pre>
    </main>
  );
}
