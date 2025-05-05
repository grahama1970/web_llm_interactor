#!/usr/bin/env node

/**
 * BrightData quick launcher for Perplexity.ai stealth automation
 * Uses the API key from .env file automatically
 */

const { spawn } = require('child_process');
const path = require('path');
const dotenv = require('dotenv');
const readline = require('readline');

// Load environment variables
dotenv.config();

// Check if we have the BrightData API key
const apiKey = process.env.BRIGHT_DATA_API_KEY;
if (!apiKey) {
  console.error('Error: BRIGHT_DATA_API_KEY not found in .env file');
  console.error('Please add your BrightData API key to the .env file:');
  console.error('BRIGHT_DATA_API_KEY=your_api_key_here');
  process.exit(1);
}

// Parse command line args
const args = process.argv.slice(2);
const promptArg = args.find(arg => !arg.startsWith('-'));
const headless = args.includes('--headless') || args.includes('-h');

// Interactive or direct mode
const interactive = args.includes('--interactive') || args.includes('-i');

async function getCustomerId() {
  if (process.env.BRD_CUSTOMER_ID) {
    return process.env.BRD_CUSTOMER_ID;
  }
  
  if (!interactive) {
    console.error('Error: BRD_CUSTOMER_ID not found in .env file');
    console.error('Either add it to .env or use --interactive flag');
    process.exit(1);
  }
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  return new Promise(resolve => {
    rl.question('Enter your BrightData Customer ID: ', (answer) => {
      rl.close();
      resolve(answer);
    });
  });
}

async function main() {
  // Get customer ID from env or user input
  const customerId = await getCustomerId();
  
  // Set environment variables for the child process
  const env = {
    ...process.env,
    BRD_CUSTOMER_ID: customerId,
    NODE_ENV: headless ? 'production' : 'development'
  };
  
  // Options for the run script
  const runOptions = [
    'run.js',
    '--proxy=brightdata',
    ...(headless ? ['--headless'] : []),
    ...(promptArg ? [`--prompt=${promptArg}`] : [])
  ];
  
  console.log('\nStarting Perplexity.ai automation with BrightData proxy...');
  console.log(`Headless mode: ${headless ? 'enabled' : 'disabled'}`);
  console.log(`Using BrightData API key from .env file and Customer ID: ${customerId}`);
  
  // Spawn the process
  const child = spawn('node', runOptions, {
    stdio: 'inherit',
    env
  });
  
  child.on('close', (code) => {
    console.log(`\nProcess exited with code ${code}`);
  });
}

main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});