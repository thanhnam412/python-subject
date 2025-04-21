import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import ContainerWrapper from "@/components/layouts/ContainerWrapper";
import Providers from "./providers";
import { cookies } from "next/headers";
import { Toaster } from "sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "revenue and expenditure",
  description: "mini app integrated with ai",
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const signature = (await cookies()).get("csrf_token_cookie")?.value ?? null;
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-[#F4F5F7]`}
      >
        <ContainerWrapper>
          <Providers signature={signature}>{children}</Providers>
        </ContainerWrapper>
        <Toaster />
      </body>
    </html>
  );
}
