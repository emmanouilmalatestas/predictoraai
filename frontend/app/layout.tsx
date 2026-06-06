import "./../styles/globals.css";
import type { ReactNode } from "react";

export const metadata = {
  title: "PredictoraAI",
  description: "WARZONE Trading Intelligence Platform"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-slate-950 text-slate-50">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <header className="flex items-center justify-between mb-8">
            <div className="font-bold text-xl">PredictoraAI</div>
            <nav className="flex gap-4 text-sm text-slate-300">
              <a href="/" className="hover:text-white">Home</a>
              <a href="/pricing" className="hover:text-white">Pricing</a>
              <a href="/docs" className="hover:text-white">Docs</a>
              <a href="/dashboard" className="hover:text-white">Dashboard</a>
            </nav>
          </header>
          {children}
          <footer className="mt-12 text-xs text-slate-500 border-t border-slate-800 pt-4">
            © {new Date().getFullYear()} PredictoraAI — WARZONE Architecture.
          </footer>
        </div>
      </body>
    </html>
  );
}
