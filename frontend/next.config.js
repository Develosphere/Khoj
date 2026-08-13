/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    appDir: true
  },
  images: {
    domains: []
  },
  // Set up rewrites for API calls to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NEXT_PUBLIC_BACKEND_API_URL + '/api/:path*',
      },
    ]
  },
}

module.exports = nextConfig;
