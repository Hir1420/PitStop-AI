import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'PitStop AI — Autonomous Workshop Operations Platform',
  description: 'AI-assisted service intake, deterministic scheduling, inventory coordination, and human-in-the-loop work order operations.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#080d1a] text-slate-100 antialiased selection:bg-orange-500 selection:text-white">
        <div className="min-h-screen flex flex-col">
          {children}
        </div>
      </body>
    </html>
  );
}
