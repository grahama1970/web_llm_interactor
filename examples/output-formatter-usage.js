/**
 * Output Formatter Usage Examples
 * 
 * This file provides examples of how to use the output formatter in your own code.
 */

const { formatOutput, formatAsTable, formatAsJson } = require('../output-formatter');
const fs = require('fs');
const path = require('path');

// Example 1: Basic Usage - Format a response from Perplexity
async function example1() {
  console.log("\n=== Example 1: Basic Usage ===\n");
  
  // Load a sample response
  const sampleResponsePath = path.join(__dirname, '..', 'responses', 'sample_response.json');
  const sampleResponse = JSON.parse(fs.readFileSync(sampleResponsePath, 'utf8'));
  
  // Format as table (human-friendly)
  console.log("Table Format (human-friendly):");
  console.log(formatOutput(sampleResponse, 'table'));
  
  // Format as JSON (agent-friendly)
  console.log("\nJSON Format (agent-friendly):");
  console.log(formatOutput(sampleResponse, 'json'));
}

// Example 2: Customizing Table Format
async function example2() {
  console.log("\n=== Example 2: Customizing Table Format ===\n");
  
  // Load a sample response
  const sampleResponsePath = path.join(__dirname, '..', 'responses', 'sample_response.json');
  const sampleResponse = JSON.parse(fs.readFileSync(sampleResponsePath, 'utf8'));
  
  // Format with custom table options
  console.log("Custom Table Format (narrow width, no metadata):");
  console.log(formatOutput(sampleResponse, 'table', {
    color: true,
    maxWidth: 60,
    includeMetadata: false,
    includeLinks: true
  }));
  
  // Format with no colors (terminal friendly)
  console.log("\nNo Colors (terminal friendly):");
  console.log(formatOutput(sampleResponse, 'table', {
    color: false,
    maxWidth: 80,
    includeMetadata: true,
    includeLinks: true
  }));
}

// Example 3: Customizing JSON Format
async function example3() {
  console.log("\n=== Example 3: Customizing JSON Format ===\n");
  
  // Load a sample response
  const sampleResponsePath = path.join(__dirname, '..', 'responses', 'sample_response.json');
  const sampleResponse = JSON.parse(fs.readFileSync(sampleResponsePath, 'utf8'));
  
  // Format with pretty printing (default)
  console.log("Pretty JSON (default):");
  console.log(formatOutput(sampleResponse, 'json', { pretty: true }));
  
  // Format with compact JSON
  console.log("\nCompact JSON:");
  console.log(formatOutput(sampleResponse, 'json', { pretty: false }));
  
  // Format with raw HTML included
  console.log("\nJSON with raw HTML included:");
  console.log(formatOutput(sampleResponse, 'json', { 
    pretty: true,
    includeRaw: true
  }));
}

// Example 4: Integration with CLI Applications
async function example4() {
  console.log("\n=== Example 4: Integration with CLI Applications ===\n");
  
  // Simulating CLI application flow
  console.log("CLI Integration Example (pseudo-code):");
  console.log(`
// In a CLI application:
const { program } = require('commander');
const { formatOutput } = require('./output-formatter');

program
  .command('query')
  .description('Query Perplexity.ai')
  .argument('<prompt>', 'Prompt to send')
  .option('-f, --format <type>', 'Output format (table, json)', 'table')
  .option('--agent', 'Enable agent mode (same as --format=json)', false)
  .action(async (prompt, options) => {
    // Get format option (with agent mode override)
    const format = options.agent ? 'json' : options.format;
    
    // Get response data from API
    const responseData = await queryPerplexity(prompt);
    
    // Format and display output
    const formattedOutput = formatOutput(responseData, format, {
      color: true,
      maxWidth: process.stdout.columns || 100
    });
    
    console.log(formattedOutput);
  });
  `);
}

// Example 5: Using Raw Formatter Functions
async function example5() {
  console.log("\n=== Example 5: Using Raw Formatter Functions ===\n");
  
  // Load a sample response
  const sampleResponsePath = path.join(__dirname, '..', 'responses', 'sample_response.json');
  const sampleResponse = JSON.parse(fs.readFileSync(sampleResponsePath, 'utf8'));
  
  console.log("Using formatAsTable directly:");
  console.log(formatAsTable(sampleResponse, {
    color: true,
    maxWidth: 90,
    includeMetadata: true,
    includeLinks: true
  }));
  
  console.log("\nUsing formatAsJson directly:");
  console.log(formatAsJson(sampleResponse, {
    pretty: true,
    includeRaw: false
  }));
}

// Run the examples
async function runExamples() {
  await example1();
  await example2();
  await example3();
  await example4();
  await example5();
}

runExamples().catch(error => {
  console.error('Error running examples:', error);
});