import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "AscendTech - Autonomous Blockchain Accounting Service",
  description:
    "Transform your financial operations with AscendTech's autonomous blockchain accounting service. Powered by Fetch.ai agents and Sui blockchain for immutable, cryptographically verifiable ledger technology.",
  keywords: [
    "blockchain accounting",
    "autonomous agents",
    "Fetch.ai",
    "Sui blockchain",
    "financial audit",
    "cryptographic verification",
    "AI-powered accounting",
    "immutable ledger",
  ],
  authors: [{ name: "AscendTech" }],
  creator: "AscendTech",
  publisher: "AscendTech",
  robots: {
    index: true,
    follow: true,
  },
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://ascendtech.com",
    title: "AscendTech - Autonomous Blockchain Accounting Service",
    description:
      "Transform your financial operations with autonomous blockchain accounting powered by Fetch.ai agents and Sui blockchain.",
    siteName: "AscendTech",
  },
  twitter: {
    card: "summary_large_image",
    title: "AscendTech - Autonomous Blockchain Accounting Service",
    description:
      "Transform your financial operations with autonomous blockchain accounting powered by Fetch.ai agents and Sui blockchain.",
    creator: "@ascendtech",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
