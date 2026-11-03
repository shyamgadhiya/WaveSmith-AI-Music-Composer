import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Music Compositor | Agentic Music Generation",
  description: "Next.js frontend with Tailwind CSS and SSE real-time streaming for AI Music Compositor.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090A0F] text-slate-100 min-h-screen antialiased selection:bg-indigo-500/30 selection:text-indigo-200">
        {children}
      </body>
    </html>
  );
}

