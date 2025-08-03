/** @type {import('next').NextConfig} */
const nextConfig = {
  // Image optimization
  images: {
    unoptimized: false,
    domains: ['localhost'],
    formats: ['image/webp', 'image/avif'],
  },
  
  // Performance optimizations
  experimental: {
    scrollRestoration: true,
  },
  
  // Compression
  compress: true,
  
  // Environment-specific optimizations
  env: {
    CUSTOM_BUILD_ID: process.env.CUSTOM_BUILD_ID || 'production',
  },
  
  // Bundle analyzer (enabled via environment variable)
  ...(process.env.ANALYZE === 'true' && {
    experimental: {
      ...nextConfig.experimental,
    },
  }),
  
  // Output optimization for Docker deployments
  output: 'standalone',
  
  // Webpack optimizations
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Production optimizations
    if (!dev) {
      // Tree shaking improvements
      config.optimization.usedExports = true
      config.optimization.sideEffects = false
      
      // Minification improvements
      config.optimization.minimize = true
    }
    
    return config
  },
  
  // Headers for better caching
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Cache-Control', value: 'no-cache, no-store, must-revalidate' },
        ],
      },
      {
        source: '/_next/static/:path*',
        headers: [
          { key: 'Cache-Control', value: 'public, max-age=31536000, immutable' },
        ],
      },
    ]
  },
  
  // API proxy rewrites
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://backend:8000/api/:path*',
      },
    ]
  },

  // Redirects for better SEO
  async redirects() {
    return [
      {
        source: '/dashboard',
        destination: '/',
        permanent: true,
      },
    ]
  },

}

export default nextConfig
