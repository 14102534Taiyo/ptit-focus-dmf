import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PTIT Focus Statistics - Siam Hydrocarbon Intelligence",
  description: "Sovereign Domestic Petroleum Production & Fiscal Sales Analytics Platform | Petroleum Institute of Thailand",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="th" className="scroll-smooth">
      <body className="bg-mesh-pattern selection:bg-sky-500 selection:text-white">
        {children}
      </body>
    </html>
  );
}
