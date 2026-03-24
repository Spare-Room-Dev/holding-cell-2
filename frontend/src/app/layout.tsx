import type { Metadata } from "next";
import { DM_Sans, IBM_Plex_Mono } from "next/font/google";
import "./globals.css";
import { SocketProvider } from '@/context/SocketContext';

/**
 * Font configuration per DESIGN.md:
 * - Display: Satoshi (loaded via Fontshare CDN in globals.css)
 * - Body: DM Sans (loaded here via next/font)
 * - Mono: IBM Plex Mono (loaded here via next/font)
 */

const dmSans = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "700"],
});

const ibmPlexMono = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400"],
});

export const metadata: Metadata = {
  title: "The Holding Cell",
  description: "Real-time honeypot attack visualization dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`dark ${dmSans.variable} ${ibmPlexMono.variable}`}
    >
      <body className="min-h-screen bg-background text-text-primary font-body antialiased">
        <SocketProvider>
          {children}
        </SocketProvider>
      </body>
    </html>
  );
}