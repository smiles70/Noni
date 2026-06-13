#!/usr/bin/env node
/**
 * Build Environment Verification Script
 * 
 * Sprint: G3 Prevention â€” Fail-fast guard for production builds
 * Purpose: Prevent deployment of builds with localhost API URL
 * 
 * This script runs before `npm run build` and enforces:
 * 1. VITE_API_BASE_URL must be set in production builds
 * 2. VITE_API_BASE_URL must not contain 'localhost'
 * 3. VITE_API_BASE_URL must be a valid HTTPS URL in production
 */

import { env } from 'node:process';
import { exit } from 'node:process';

const isProduction = env.NODE_ENV === 'production' || env.CF_PAGES === '1';
const isCI = env.CI === 'true' || env.GITHUB_ACTIONS === 'true';

// Skip verification in development mode
if (!isProduction && !isCI) {
  console.log('âœ“ Build env verification: SKIPPED (dev mode)');
  exit(0);
}

const apiBaseUrl = env.VITE_API_BASE_URL;

console.log('ðŸ” Verifying build environment...');
console.log(`   NODE_ENV: ${env.NODE_ENV || 'undefined'}`);
console.log(`   CI: ${isCI}`);
console.log(`   VITE_API_BASE_URL: ${apiBaseUrl || 'NOT SET'}`);

// Check 1: VITE_API_BASE_URL must be set
if (!apiBaseUrl) {
  console.error('\nâŒ BUILD FAILED: VITE_API_BASE_URL is not set');
  console.error('   This environment variable is required for production builds.');
  console.error('   See docs/gotchas.md G3 for details.');
  console.error('\n   To fix:');
  console.error('   - In GitHub Actions: Set VITE_API_BASE_URL secret');
  console.error('   - In local build: export VITE_API_BASE_URL=https://noni-api.fly.dev');
  exit(1);
}

// Check 2: Must not contain localhost
if (apiBaseUrl.includes('localhost') || apiBaseUrl.includes('127.0.0.1')) {
  console.error('\nâŒ BUILD FAILED: VITE_API_BASE_URL contains localhost');
  console.error(`   Current value: ${apiBaseUrl}`);
  console.error('   Production builds cannot use localhost as the API URL.');
  console.error('   This causes the login loop (G3 gotcha).');
  console.error('\n   To fix:');
  console.error('   - Set VITE_API_BASE_URL to the production API URL');
  console.error('   - Example: https://noni-api.fly.dev');
  exit(1);
}

// Check 3: Must use HTTPS in production (unless explicitly allowed)
if (!apiBaseUrl.startsWith('https://') && !apiBaseUrl.includes('ngrok')) {
  console.error('\nâŒ BUILD FAILED: VITE_API_BASE_URL must use HTTPS in production');
  console.error(`   Current value: ${apiBaseUrl}`);
  console.error('   HTTP is not allowed for production API URLs.');
  exit(1);
}

// Check 4: Must not end with trailing slash (causes double slashes)
if (apiBaseUrl.endsWith('/')) {
  console.error('\nâš ï¸  WARNING: VITE_API_BASE_URL has trailing slash');
  console.error(`   Current value: ${apiBaseUrl}`);
  console.error('   This may cause API request issues.');
  // Don't fail, just warn
}

console.log('\nâœ“ Build environment verification: PASSED');
console.log(`   API Base URL: ${apiBaseUrl}`);
exit(0);
