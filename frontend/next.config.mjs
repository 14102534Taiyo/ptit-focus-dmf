/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'export', // Static Site Generation (SSG) for ultra-fast deployment and zero server cost
  images: {
    unoptimized: true
  }
};

export default nextConfig;
