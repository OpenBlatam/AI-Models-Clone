#!/usr/bin/env node
/**
 * Quality Check Script
 * 
 * This script runs various quality checks on the codebase:
 * - TypeScript type checking
 * - ESLint
 * - Prettier formatting
 * - Package.json validation
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function checkCommand(command, description) {
  try {
    log(`\n🔍 ${description}...`, 'blue');
    execSync(command, { stdio: 'inherit' });
    log(`✅ ${description} passed`, 'green');
    return true;
  } catch (error) {
    log(`❌ ${description} failed`, 'red');
    return false;
  }
}

function checkFileExists(filePath, description) {
  if (fs.existsSync(filePath)) {
    log(`✅ ${description} exists`, 'green');
    return true;
  } else {
    log(`⚠️  ${description} not found`, 'yellow');
    return false;
  }
}

function main() {
  log('\n🚀 Starting Quality Checks...\n', 'blue');
  
  const results = {
    passed: 0,
    failed: 0,
    warnings: 0,
  };

  // Check required files
  log('\n📁 Checking required files...', 'blue');
  checkFileExists('package.json', 'package.json') || results.warnings++;
  checkFileExists('tsconfig.json', 'tsconfig.json') || results.warnings++;
  checkFileExists('.gitignore', '.gitignore') || results.warnings++;
  checkFileExists('.prettierrc', '.prettierrc') || results.warnings++;
  checkFileExists('next.config.js', 'next.config.js') || results.warnings++;

  // Type checking
  if (checkCommand('npm run type-check', 'TypeScript type checking')) {
    results.passed++;
  } else {
    results.failed++;
  }

  // Linting
  if (checkCommand('npm run lint', 'ESLint')) {
    results.passed++;
  } else {
    results.failed++;
  }

  // Format checking
  if (checkCommand('npm run format:check', 'Prettier formatting')) {
    results.passed++;
  } else {
    results.failed++;
  }

  // Summary
  log('\n📊 Summary:', 'blue');
  log(`✅ Passed: ${results.passed}`, 'green');
  log(`❌ Failed: ${results.failed}`, results.failed > 0 ? 'red' : 'green');
  log(`⚠️  Warnings: ${results.warnings}`, results.warnings > 0 ? 'yellow' : 'green');

  if (results.failed > 0) {
    log('\n❌ Some checks failed. Please fix the issues above.', 'red');
    process.exit(1);
  } else {
    log('\n✅ All checks passed!', 'green');
    process.exit(0);
  }
}

main();


















