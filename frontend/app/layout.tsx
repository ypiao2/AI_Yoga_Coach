import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI Yoga Coach',
  description: 'Body-Aware + Rule-Guided + RAG-Enhanced yoga flow',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen">
        {children}
      </body>
    </html>
  );
}
