/**
 * BrightData Diagnostics Tool
 * This script runs a series of tests to diagnose BrightData proxy issues
 */

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

// Apply stealth plugin
chromium.use(stealth);

// BrightData credentials
const BRD_CUSTOMER_ID = 'hl_4da0a16e';
const BRD_API_KEY = 'x8btfu41tj0i';

// Test URLs
const TEST_URLS = [
  {
    name: "BrightData Test URL",
    url: "https://geo.brdtest.com/mygeo.json",
    description: "BrightData's official test URL"
  },
  {
    name: "Google",
    url: "https://www.google.com",
    description: "Simple high-availability site"
  },
  {
    name: "Perplexity.ai",
    url: "https://www.perplexity.ai",
    description: "Target site with bot detection"
  },
  {
    name: "ChatGPT",
    url: "https://chat.openai.com",
    description: "Another AI site with bot detection"
  },
  {
    name: "Bing",
    url: "https://www.bing.com",
    description: "Search engine with moderate bot detection"
  }
];

// Proxy configurations to test
const PROXY_CONFIGS = [
  {
    name: "Residential - Port 33335",
    server: "brd.superproxy.io:33335",
    username: `brd-customer-${BRD_CUSTOMER_ID}-zone-residential_proxy1`,
    password: BRD_API_KEY
  },
  {
    name: "Datacenter - Port 22225",
    server: "brd.superproxy.io:22225",
    username: `brd-customer-${BRD_CUSTOMER_ID}-zone-datacenter`,
    password: BRD_API_KEY
  },
  {
    name: "HTTPS - Port 24000",
    server: "brd.superproxy.io:24000",
    username: `brd-customer-${BRD_CUSTOMER_ID}-zone-residential_proxy1`,
    password: BRD_API_KEY
  },
  {
    name: "Alternate Hostname",
    server: "zproxy.lum-superproxy.io:22225",
    username: `brd-customer-${BRD_CUSTOMER_ID}-zone-residential_proxy1`,
    password: BRD_API_KEY
  }
];

// Direct HTTP/HTTPS request with proxy
async function makeProxyRequest(url, proxyConfig) {
  return new Promise((resolve, reject) => {
    const proxyUrl = new URL(`http://${proxyConfig.server}`);
    const targetUrl = new URL(url);
    
    // Determine if we need http or https module
    const requestor = url.startsWith('https') ? https : http;
    
    const options = {
      host: proxyUrl.hostname,
      port: proxyUrl.port,
      path: url,
      method: 'GET',
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'Proxy-Authorization': 'Basic ' + Buffer.from(`${proxyConfig.username}:${proxyConfig.password}`).toString('base64')
      },
      timeout: 10000
    };
    
    const req = requestor.request(options, (res) => {
      let data = '';
      
      res.on('data', (chunk) => {
        data += chunk;
      });
      
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data.substring(0, 100) // Just get the first 100 chars of data
        });
      });
    });
    
    req.on('error', (err) => {
      reject(err);
    });
    
    req.end();
  });
}

// Test a URL with Playwright and proxy
async function testWithPlaywright(testUrl, proxyConfig) {
  const timeStart = Date.now();
  
  try {
    // Launch browser with proxy
    const browser = await chromium.launch({
      headless: true,
      ignoreHTTPSErrors: true,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--ignore-certificate-errors'
      ],
      proxy: proxyConfig
    });
    
    // Create context with enhanced fingerprinting
    const context = await browser.newContext({ 
      ignoreHTTPSErrors: true
    });
    
    // Create page and set up console capture
    const page = await context.newPage();
    let consoleErrors = [];
    
    page.on('console', msg => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    
    // Navigate to the test URL
    await page.goto(testUrl, { 
      waitUntil: 'domcontentloaded',
      timeout: 15000 
    });
    
    // Get page info
    const title = await page.title();
    const url = page.url(); // Final URL after any redirects
    let botDetected = false;
    
    // Check for bot detection
    const pageContent = await page.content();
    const botDetectionPhrases = [
      'CAPTCHA', 'captcha', 'verify you are not a bot', 
      'security check', 'blocked', 'challenge',
      'suspicious activity', 'unusual traffic',
      'verify your identity', 'check if you are a human'
    ];
    
    const detectedPhrase = botDetectionPhrases.find(phrase => pageContent.includes(phrase));
    if (detectedPhrase) {
      botDetected = true;
    }
    
    // Take a screenshot
    const screenshotDir = path.join(__dirname, 'screenshots', 'diagnostics');
    if (!fs.existsSync(screenshotDir)) {
      fs.mkdirSync(screenshotDir, { recursive: true });
    }
    
    const screenshotFile = path.join(
      screenshotDir, 
      `${proxyConfig.name.replace(/\s+/g, '_').toLowerCase()}_${new URL(testUrl).hostname.replace(/\./g, '_')}.png`
    );
    
    await page.screenshot({ path: screenshotFile });
    
    // Close browser
    await browser.close();
    
    // Calculate time
    const timeEnd = Date.now();
    const timeElapsed = timeEnd - timeStart;
    
    return {
      success: true,
      title,
      url,
      loadTime: timeElapsed,
      botDetected,
      consoleErrors: consoleErrors.length > 0 ? consoleErrors : null,
      screenshotPath: screenshotFile
    };
  } catch (error) {
    // Calculate time even on error
    const timeEnd = Date.now();
    const timeElapsed = timeEnd - timeStart;
    
    return {
      success: false,
      error: error.message,
      loadTime: timeElapsed
    };
  }
}

// Test account balance/status
async function testBrightDataAccount() {
  console.log('Testing BrightData account status...');
  
  try {
    // Make a request to the BrightData status URL
    const balanceUrl = `https://brightdata.com/api/users/${BRD_CUSTOMER_ID}/status`;
    
    const options = {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${BRD_API_KEY}`
      }
    };
    
    const response = await fetch(balanceUrl, options);
    
    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        data
      };
    } else {
      return {
        success: false,
        status: response.status,
        statusText: response.statusText
      };
    }
  } catch (error) {
    return {
      success: false,
      error: error.message
    };
  }
}

async function runAllTests() {
  console.log('===== BrightData Diagnostics Tool =====');
  console.log(`Starting tests at: ${new Date().toLocaleString()}`);
  console.log(`BrightData customer ID: ${BRD_CUSTOMER_ID}`);
  console.log('=====================================\n');
  
  // Create results object
  const results = {
    accountStatus: null,
    tests: {}
  };
  
  // Test account status
  console.log('Testing BrightData account status...');
  results.accountStatus = await testBrightDataAccount();
  console.log('Account status check complete.');
  
  // For each proxy config, test each URL
  for (const proxyConfig of PROXY_CONFIGS) {
    console.log(`\nTesting proxy configuration: ${proxyConfig.name}`);
    results.tests[proxyConfig.name] = {};
    
    for (const testSite of TEST_URLS) {
      console.log(`  → Testing ${testSite.name} (${testSite.url})...`);
      
      try {
        // First try direct HTTP request
        const directResult = await makeProxyRequest(testSite.url, proxyConfig)
          .catch(err => ({ success: false, error: err.message }));
        
        console.log(`    • Direct HTTP request: ${directResult.statusCode || 'Failed'}`);
        
        // Then try with Playwright
        const result = await testWithPlaywright(testSite.url, proxyConfig);
        
        if (result.success) {
          console.log(`    • Success! Page title: ${result.title}`);
          if (result.botDetected) {
            console.log(`    • WARNING: Bot detection triggered`);
          }
        } else {
          console.log(`    • Failed: ${result.error}`);
        }
        
        // Store results
        results.tests[proxyConfig.name][testSite.name] = {
          directRequest: directResult,
          playwrightTest: result
        };
      } catch (error) {
        console.error(`    • Error running test: ${error.message}`);
        results.tests[proxyConfig.name][testSite.name] = {
          error: error.message
        };
      }
    }
  }
  
  // Save results to file
  const resultsDir = path.join(__dirname, 'diagnostics');
  if (!fs.existsSync(resultsDir)) {
    fs.mkdirSync(resultsDir, { recursive: true });
  }
  
  const resultsFile = path.join(resultsDir, `brightdata_test_results_${Date.now()}.json`);
  fs.writeFileSync(resultsFile, JSON.stringify(results, null, 2));
  
  console.log('\n=====================================');
  console.log(`Tests completed at: ${new Date().toLocaleString()}`);
  console.log(`Results saved to: ${resultsFile}`);
  console.log('=====================================');
  
  // Generate an HTML report
  const reportFile = path.join(resultsDir, `brightdata_report_${Date.now()}.html`);
  
  let html = `
  <!DOCTYPE html>
  <html>
  <head>
    <title>BrightData Diagnostics Report</title>
    <style>
      body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
      h1, h2, h3 { color: #333; }
      table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
      th, td { text-align: left; padding: 8px; border: 1px solid #ddd; }
      th { background-color: #f2f2f2; }
      .success { color: green; }
      .error { color: red; }
      .warning { color: orange; }
      pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
    </style>
  </head>
  <body>
    <h1>BrightData Diagnostics Report</h1>
    <p>Generated at: ${new Date().toLocaleString()}</p>
    <p>BrightData Customer ID: ${BRD_CUSTOMER_ID}</p>
    
    <h2>Account Status</h2>
    <pre>${JSON.stringify(results.accountStatus, null, 2)}</pre>
    
    <h2>Test Results by Proxy Configuration</h2>
  `;
  
  for (const [proxyName, siteResults] of Object.entries(results.tests)) {
    html += `
    <h3>${proxyName}</h3>
    <table>
      <tr>
        <th>Site</th>
        <th>Direct Request</th>
        <th>Playwright Test</th>
        <th>Bot Detection</th>
      </tr>
    `;
    
    for (const [siteName, result] of Object.entries(siteResults)) {
      const directStatus = result.directRequest?.statusCode || 'Failed';
      const playwrightSuccess = result.playwrightTest?.success ? 'Success' : 'Failed';
      const botDetected = result.playwrightTest?.botDetected ? 'Detected' : 'Not Detected';
      
      html += `
      <tr>
        <td>${siteName}</td>
        <td class="${directStatus.toString().startsWith('2') ? 'success' : 'error'}">${directStatus}</td>
        <td class="${playwrightSuccess === 'Success' ? 'success' : 'error'}">${playwrightSuccess}${result.playwrightTest?.error ? `: ${result.playwrightTest.error}` : ''}</td>
        <td class="${botDetected === 'Detected' ? 'warning' : 'success'}">${botDetected}</td>
      </tr>
      `;
    }
    
    html += `</table>`;
  }
  
  html += `
    <h2>Conclusions</h2>
    <p>This report can help determine if your BrightData account is properly configured and if specific sites are blocking BrightData IPs.</p>
    <ul>
      <li>If the BrightData test URL works but other sites don't, your account is working but those sites may be blocking BrightData IPs.</li>
      <li>If no sites work, your BrightData account may have issues (insufficient credits, incorrect configuration, etc.)</li>
      <li>If some sites work but Perplexity doesn't, Perplexity is specifically blocking BrightData IPs.</li>
    </ul>
  </body>
  </html>
  `;
  
  fs.writeFileSync(reportFile, html);
  console.log(`HTML report saved to: ${reportFile}`);
}

// Run all the tests
runAllTests().catch(error => {
  console.error('Error running tests:', error);
});