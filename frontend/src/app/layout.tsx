import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MediCopilot Nexus - Asistente Clínico Inteligente",
  description: "AI-powered medical assistant for clinical consultations",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
