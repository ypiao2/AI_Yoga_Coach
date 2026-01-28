/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export', // static export for FastAPI to serve (single-port deploy)
  // Local dev: set NEXT_PUBLIC_API_URL=http://localhost:8000 in .env.local so frontend calls the backend.
};

module.exports = nextConfig;
