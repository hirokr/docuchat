import type { Metadata } from "next";
import { Inter } from "next/font/google";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "600", "700"],
});

export const metadata: Metadata = {
  title: "DocuChat | Research Assistant",
  description: "Chat with your documents using AI-powered analysis and citations.",
};

export default function ChatLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div
      className={`${inter.variable} chat-theme flex h-dvh min-h-0 flex-col overflow-hidden`}
    >
      {children}
    </div>
  );
}
