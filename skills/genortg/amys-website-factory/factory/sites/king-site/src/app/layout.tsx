import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "King Genor — Supreme Ruler of All Things Awesome",
  description: "Behold the domain of King Genor — conqueror of bugs, architect of empires, and sovereign of all things awesome.",
  openGraph: {
    title: "King Genor — The King of Everything",
    description: "Behold the domain of King Genor",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700;900&family=Playfair+Display:wght@400;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
