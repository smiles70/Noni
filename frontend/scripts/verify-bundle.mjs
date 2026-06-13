#!/usr/bin/env node
/**
 * Bundle Verification Script
 * 
 * Sprint: G3 Prevention â€” Post-build verification
 * Purpose: Verify production bundle doesn't contain localhost references
 * 
 * This script runs after `npm run build` and checks:
 * 1. Built JS files don't contain 'localhost:8000' or '127.0.0.1:8000'
 * 2. API_BASE_URL is correctly set to production URL
 */

import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { env, exit } from 'node:process';

const DIST_DIR = './dist';
const PROD_API_URL = 'https://noni-api.fly.dev';

console.log('ðŸ” Verifying production bundle...');

// Check if dist exists
try {
  readdirSync(DIST_DIR);
} catch (err) {
  console.error(`âŒ Bundle verification failed: ${DIST_DIR} not found`);
  console.error('   Run npm run build first.');
  exit(1);
}

// Find all JS files in dist/assets
const assetsDir = join(DIST_DIR, 'assets');
let jsFiles;
try {
  jsFiles = readdirSync(assetsDir).filter(f => f.endsWith('.js'));
} catch (err) {
  console.error(`âŒ Bundle verification failed: ${assetsDir} not found`);
  exit(1);
}

console.log(`   Found ${jsFiles.length} JS bundle files`);

// Check each JS file for localhost references
const forbiddenPatterns = [
  'localhost:8000',
  '127.0.0.1:8000',
  'http://localhost',
  'http://127.0.0.1',
];

let hasErrors = false;

for (const file of jsFiles) {
  const filePath = join(assetsDir, file);
  const content = readFileSync(filePath, 'utf-8');
  
  for (const pattern of forbiddenPatterns) {
    if (content.includes(pattern)) {
      console.error(`\nâŒ BUNDLE VERIFICATION FAILED`);
      console.error(`   File: ${file}`);
      console.error(`   Found forbidden pattern: "${pattern}"`);
      console.error('\n   This indicates the bundle was built with localhost API URL.');
      console.error('   See docs/gotchas.md G3 for details.');
      console.error('\n   To fix:');
      console.error('   1. Delete dist/ directory');
      console.error('   2. Set VITE_API_BASE_URL=https://noni-api.fly.dev');
      console.error('   3. Run npm run build again');
      hasErrors = true;
    }
  }
  
  // Verify production API URL is present (for production builds)
  const isCI = env.CI === 'true' || env.GITHUB_ACTIONS === 'true';
  if (isCI && !content.includes(PROD_API_URL)) {
    console.error(`\nâŒ BUNDLE VERIFICATION FAILED`);
    console.error(`   File: ${file}`);
    console.error(`   Production API URL (${PROD_API_URL}) not found in bundle.`);
    console.error('   This may indicate VITE_API_BASE_URL was not set correctly.');
    hasErrors = true;
  }
}

if (hasErrors) {
  exit(1);
}

console.log('\nâœ“ Bundle verification: PASSED');
console.log(`   No localhost references found`);
console.log(`   Production API URL verified: ${PROD_API_URL}`);
exit(0);
