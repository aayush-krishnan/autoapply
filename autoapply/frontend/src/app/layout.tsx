import type { Metadata } from "next";
import { Outfit } from "next/font/google";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
});

export const metadata: Metadata = {
  title: "AutoApply Dashboard",
  description: "AI-powered job application & outreach platform",
};

import Sidebar from "@/components/Sidebar";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${outfit.variable} font-sans antialiased bg-black text-white h-screen overflow-hidden flex`}>
        <Sidebar />
        <main className="flex-1 h-full overflow-y-auto bg-[#0a0a0a]">
          {children}
        </main>
      </body>
    </html>
  );
}
