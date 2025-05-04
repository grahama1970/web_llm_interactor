#!/usr/bin/env node

/**
 * Test script for BrightData proxy connectivity
 */

const http = require('http');
const https = require('https');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// BrightData credentials
const BRIGHTDATA_API_KEY = process.env.BRIGHT_DATA_API_KEY;
const CUSTOMER_ID = 'hl_4da0a16e';
const ZONE = 'residential';

if (!BRIGHTDATA_API_KEY) {
  console.error('Error: BRIGHT_DATA_API_KEY not found in environment variables');
  process.exit(1);
}

// Proxy configuration
const proxyConfig = {
  host: 'brd.superproxy.io',
  port: 22225,
  auth: `brd-customer-${CUSTOMER_ID}-zone-${ZONE}:${BRIGHTDATA_API_KEY}`
};

console.log('Proxy auth string:', proxyConfig.auth);

// Simple HTTP client through proxy
const testHttpProxy = (url) => {
  return new Promise((resolve, reject) => {
    const options = {
      host: proxyConfig.host,
      port: proxyConfig.port,
      path: url,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
        'Proxy-Authorization': `Basic ${Buffer.from(proxyConfig.auth).toString('base64')}`
      }
    };

    console.log(`Testing proxy connection to ${url}...`);
    const req = http.request(options, (res) => {
      console.log(`Response status code: ${res.statusCode}`);
      
      let data = '';
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data.substring(0, 500) + '...' // First 500 chars
        });
      });
    });
    
    req.on('error', (err) => {
      reject(err);
    });
    
    req.end();
  });
};

// Run tests
async function main() {
  console.log('BrightData Proxy Test');
  console.log('====================');
  console.log(`Using Customer ID: ${CUSTOMER_ID}`);
  console.log(`Using Zone: ${ZONE}`);
  console.log('Testing connectivity...');
  
  try {
    // Test with a simple HTTP site
    console.log('\n[TEST 1] Basic HTTP test - example.com:');
    const result1 = await testHttpProxy('http://example.com');
    console.log(`Status: ${result1.statusCode}`);
    console.log(`Response preview: ${result1.data.substring(0, 100)}...`);
    
    // Test with HTTPS
    console.log('\n[TEST 2] HTTPS test - httpbin.org:');
    const result2 = await testHttpProxy('https://httpbin.org/ip');
    console.log(`Status: ${result2.statusCode}`);
    console.log(`Response preview: ${result2.data}`);
    
    // Test Perplexity
    console.log('\n[TEST 3] Target site test - Perplexity.ai:');
    const result3 = await testHttpProxy('https://www.perplexity.ai');
    console.log(`Status: ${result3.statusCode}`);
    console.log(`Response preview: ${result3.data.substring(0, 100)}...`);
    
    console.log('\nAll tests completed!');
  } catch (error) {
    console.error('Error during proxy testing:', error.message);
  }
}

main().catch(console.error);