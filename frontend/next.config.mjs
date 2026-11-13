/** @type {import('next').NextConfig} */
const isGithubPages = process.env.DEPLOY_TARGET === 'gh-pages';
const basePath = isGithubPages ? '/ptit-focus-dmf' : '';

const nextConfig = {
  reactStrictMode: true,
  output: 'export', // Static Site Generation (SSG) for ultra-fast deployment and zero server cost
  images: {
    unoptimized: true
  },
  // Exposed so runtime fetch() of per-year data files resolves under the Pages sub-path
  env: {
    NEXT_PUBLIC_BASE_PATH: basePath
  },
  basePath,
  assetPrefix: isGithubPages ? '/ptit-focus-dmf/' : '',
  trailingSlash: true
};

export default nextConfig;
