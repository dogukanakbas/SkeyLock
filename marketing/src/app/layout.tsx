import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SkeyLock by Udar Soft - Secure Your IoT Infrastructure",
  description: "SkeyLock by Udar Soft - Enterprise IoT Security Platform. Discover, Analyze, and Protect your IoT devices with automated vulnerability assessment and real-time monitoring.",
  keywords: "SkeyLock, Udar Soft, IoT security, vulnerability assessment, network security, device monitoring, cybersecurity",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="scroll-smooth">
      <body className={`${inter.className} antialiased`}>
        {children}
      </body>
    </html>
  );
}
