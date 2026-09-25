/** @type {import('next').NextConfig} */
const isGithubPages = process.env.DEPLOY_TARGET === 'gh-pages';

const nextConfig = {
  reactStrictMode: true,
  output: 'export', // Static Site Generation (SSG) for ultra-fast deployment and zero server cost
  images: {
    unoptimized: true
  },
  basePath: isGithubPages ? '/ptit-focus-dmf' : '',
  assetPrefix: isGithubPages ? '/ptit-focus-dmf/' : '',
  trailingSlash: true
};

export default nextConfig;
