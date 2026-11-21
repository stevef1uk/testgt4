/// <reference types="next" />
/// <reference types="next/image-types/global" />
/// <reference types="next/legacy/image-types/global" />

// Next.js environment types
declare module '*.module.css' {
  const classes: Record<string, string>;
  export default classes;
}

// Environment variables type declarations
interface ProcessEnv {
  NODE_ENV: string;
  NEXT_PUBLIC_APP_URL: string;
}

// NOTE: This file should not be edited
// see https://nextjs.org/docs/basic-features/typescript for more information.
