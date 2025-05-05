#!/usr/bin/env node

/**
 * Security evaluation script for Perplexity.ai stealth automation
 * Performs a comprehensive security assessment based on the Hacker methodology
 */

const path = require('path');
const fs = require('fs');
const { generateSecurityReport } = require('./src/security');
const readline = require('readline');

// ANSI color codes for terminal output
const COLORS = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  bold: '\x1b[1m'
};

// Print banner
console.log('\n' + COLORS.magenta + COLORS.bold);
console.log('╔════════════════════════════════════════════════════════════╗');
console.log('║  PERPLEXITY.AI STEALTH SECURITY EVALUATION                 ║');
console.log('║  Powered by Hacker Methodology                             ║');
console.log('╚════════════════════════════════════════════════════════════╝');
console.log(COLORS.reset);

// Parse command line arguments
const args = process.argv.slice(2);
const flags = {};

args.forEach(arg => {
  if (arg.startsWith('--')) {
    const [key, value] = arg.substring(2).split('=');
    flags[key] = value || true;
  } else if (arg.startsWith('-')) {
    flags[arg.substring(1)] = true;
  }
});

// Show help if requested
if (flags.h || flags.help) {
  console.log(`
${COLORS.cyan}${COLORS.bold}Usage:${COLORS.reset}
  node security-eval.js [options]

${COLORS.cyan}${COLORS.bold}Options:${COLORS.reset}
  --help, -h               Show this help message
  --output=<path>          Path to save the security report (default: ./security-report.md)
  --check-deps             Check dependencies for vulnerabilities
  --analyze-code           Analyze code for security issues
  --full                   Run a full security assessment (includes all checks)
  --silent                 Suppress detailed output
  
${COLORS.cyan}${COLORS.bold}Examples:${COLORS.reset}
  node security-eval.js --full                     # Run a full security assessment
  node security-eval.js --check-deps               # Only check dependencies
  node security-eval.js --analyze-code             # Only analyze code
  node security-eval.js --output=./my-report.md    # Save report to custom location
  `);
  process.exit(0);
}

// Main function
async function main() {
  try {
    // Determine options
    const options = {
      checkDependencies: flags['check-deps'] || flags.full || false,
      analyzeCode: flags['analyze-code'] || flags.full || true, // Default to true
      testExploits: false, // Always disabled for safety
      outputPath: flags.output || './security-report.json'
    };
    
    // Determine report path
    const reportPath = flags.output || './security-report.md';
    
    console.log(`${COLORS.cyan}${COLORS.bold}[CONFIGURATION]${COLORS.reset}`);
    console.log(`▶ Check dependencies: ${options.checkDependencies ? COLORS.green + 'enabled' + COLORS.reset : COLORS.yellow + 'disabled' + COLORS.reset}`);
    console.log(`▶ Analyze code: ${options.analyzeCode ? COLORS.green + 'enabled' + COLORS.reset : COLORS.yellow + 'disabled' + COLORS.reset}`);
    console.log(`▶ Test exploits: ${COLORS.red}disabled${COLORS.reset} (for safety)`);
    console.log(`▶ Report path: ${reportPath}`);
    
    // Confirm before proceeding
    await confirmContinue();
    
    console.log(`\n${COLORS.cyan}${COLORS.bold}[STARTING SECURITY ANALYSIS]${COLORS.reset}`);
    console.log(`Evaluating security of Perplexity.ai stealth automation...`);
    
    // Generate the security report
    const outputPath = await generateSecurityReport(reportPath);
    
    console.log(`\n${COLORS.green}${COLORS.bold}[COMPLETE]${COLORS.reset}`);
    console.log(`Security report generated: ${outputPath}`);
    console.log('\nPlease review the report for security recommendations.');
    
  } catch (error) {
    console.error(`\n${COLORS.red}${COLORS.bold}[ERROR]${COLORS.reset}`);
    console.error(`Failed to generate security report: ${error.message}`);
    process.exit(1);
  }
}

/**
 * Prompts the user to confirm before proceeding
 * @returns {Promise<void>}
 */
function confirmContinue() {
  return new Promise(resolve => {
    if (flags.y || flags.yes || flags.silent) {
      return resolve();
    }
    
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
    
    rl.question(`\n${COLORS.yellow}Continue with security evaluation? [Y/n] ${COLORS.reset}`, answer => {
      rl.close();
      
      if (answer.toLowerCase() === 'n' || answer.toLowerCase() === 'no') {
        console.log('Security evaluation cancelled.');
        process.exit(0);
      }
      
      resolve();
    });
  });
}

// Run the main function
main().catch(error => {
  console.error('Unhandled error:', error);
  process.exit(1);
});