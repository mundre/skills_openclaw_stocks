import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Waifu Room",
  description:
    "Fullstack waifu chatroom with VRM avatars, openai-compatible chat, Whisper STT, and Kokoro TTS.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="min-h-full bg-[var(--bg)] text-[var(--fg)]">
        {children}
      </body>
    </html>
  );
}
