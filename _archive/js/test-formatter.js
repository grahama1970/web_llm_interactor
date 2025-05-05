#!/usr/bin/env node

/**
 * Test script for the output formatter
 */

const fs = require('fs');
const path = require('path');
const { formatOutput } = require('./output-formatter');

// Load sample response
const sampleResponsePath = path.join(__dirname, 'responses', 'sample_response.json');
const sampleResponse = JSON.parse(fs.readFileSync(sampleResponsePath, 'utf8'));

// Test table format
console.log('\nTABLE FORMAT OUTPUT:');
console.log(formatOutput(sampleResponse, 'table', {
  color: true,
  maxWidth: 100,
  includeMetadata: true,
  includeLinks: true
}));

// Test JSON format
console.log('\nJSON FORMAT OUTPUT:');
console.log(formatOutput(sampleResponse, 'json', {
  pretty: true,
  includeRaw: false
}));

// Test JSON format (compact)
console.log('\nJSON FORMAT OUTPUT (COMPACT):');
console.log(formatOutput(sampleResponse, 'json', {
  pretty: false,
  includeRaw: false
}));