/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  // Keep `next dev` artifacts isolated from `next build`. Running verification
  // builds while the demo server is open must not invalidate live route/CSS manifests.
  distDir: process.env.NODE_ENV === 'development' ? '.next-dev' : '.next',
  // FastAPI exposes some collection routes with a trailing slash. Preserve it
  // so Next does not redirect and strip the bearer token before proxying.
  skipTrailingSlashRedirect: true,
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
