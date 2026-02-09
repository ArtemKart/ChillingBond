/**
 * next.config.js
 *
 * Dev-time proxy for /api -> backend to make cookies same-site (same origin)
 * and to avoid CORS/cookie issues during local development.
 *
 * This file:
 * - Adds a rewrite so requests to `/api/*` from the Next dev server are proxied
 *   to the backend running on http://localhost:8000 (adjust port if needed).
 * - Sets NEXT_PUBLIC_API_URL to `/api` in development so frontend code will
 *   request relative `/api/...` endpoints (same-origin), avoiding cross-site
 *   cookie restrictions.
 *
 * Usage:
 * - Ensure your backend is reachable at http://localhost:8000 in dev (change below if not).
 * - In production NEXT_PUBLIC_API_URL will be taken from environment or default to existing value.
 */

const DEV_BACKEND_ORIGIN = "http://localhost:8000"; // change if your backend runs on a different host/port

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,

  // Runtime env variables accessible on the client via process.env.NEXT_PUBLIC_API_URL
  // In dev we set it to '/api' so frontend does relative requests -> will be proxied by rewrites.
  env: {
    NEXT_PUBLIC_API_URL:
      process.env.NODE_ENV === "development"
        ? "/api"
        : process.env.NEXT_PUBLIC_API_URL || "/api",
  },

  // Rewrites let us proxy requests from the Next dev server to the backend.
  // This makes the browser treat requests as same-origin and will allow cookies
  // set by the backend to be sent on subsequent fetches (credentials: 'include').
  async rewrites() {
    if (process.env.NODE_ENV === "development") {
      return [
        {
          source: "/api/:path*",
          destination: `${DEV_BACKEND_ORIGIN}/api/:path*`,
        },
      ];
    }
    // No special rewrites in production (expect NEXT_PUBLIC_API_URL to point to real API)
    return [];
  },
};

module.exports = nextConfig;
