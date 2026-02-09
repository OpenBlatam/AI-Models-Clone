/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: ['i.scdn.co', 'mosaic.scdn.co'],
  },
  env: {
    NEXT_PUBLIC_MUSIC_API_URL: process.env.NEXT_PUBLIC_MUSIC_API_URL || 'http://localhost:8010',
    NEXT_PUBLIC_ROBOT_API_URL: process.env.NEXT_PUBLIC_ROBOT_API_URL || 'http://localhost:8010',
  },
}

module.exports = nextConfig

