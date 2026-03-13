import type { Metadata } from "next";
import { GeistSans } from "geist/font/sans";
import { GeistMono } from "geist/font/mono";
import "./globals.css";
import { Toaster } from "sonner";
import Sidebar from "@/components/Sidebar";
import { CommandMenu } from "@/components/CommandMenu";

export const metadata: Metadata = {
  title: "AutoApply Dashboard",
  description: "AI-powered job application & outreach platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${GeistSans.variable} ${GeistMono.variable} font-sans antialiased bg-black text-white h-screen overflow-hidden flex`}>
        <CommandMenu />
        <Sidebar />
        <main className="flex-1 h-full overflow-y-auto bg-black border-l border-white/[0.06]">
          {children}
          <Toaster 
            theme="dark" 
            position="bottom-right" 
            toastOptions={{
              style: {
                background: "rgba(10, 10, 10, 0.8)",
                backdropFilter: "blur(12px)",
                border: "1px solid rgba(255, 255, 255, 0.1)",
                color: "#fff",
              },
            }}
          />
        </main>
      </body>
    </html>
  );
}
