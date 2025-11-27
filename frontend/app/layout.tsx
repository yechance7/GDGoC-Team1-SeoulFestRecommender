import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "행사 캘린더",
  description: "서울시 행사들을 확인해보세요!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="stylesheet"
          as="style"
          crossOrigin="anonymous"
          href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300&display=swap"
        />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}

