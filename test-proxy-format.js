const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();

// Apply stealth plugin
chromium.use(stealth);

// Proxy configuration in Playwright format
async function testProxy() {
  console.log('Testing proxy configuration...');
  
  // BrightData proxy settings
  const proxyConfig = {
    server: 'brd.superproxy.io:33335',
    username: 'brd-customer-hl_4da0a16e-zone-residential_proxy1',
    password: 'x8btfu41tj0i'
  };
  
  console.log('Using proxy config:', JSON.stringify(proxyConfig, null, 2));
  
  // Launch options
  const launchOptions = {
    headless: true,
    ignoreHTTPSErrors: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--ignore-certificate-errors',
      '--ignore-ssl-errors'
    ],
    proxy: proxyConfig
  };
  
  try {
    console.log('Launching browser...');
    const browser = await chromium.launch(launchOptions);
    
    console.log('Creating context...');
    const context = await browser.newContext({ ignoreHTTPSErrors: true });
    
    console.log('Creating page...');
    const page = await context.newPage();
    
    console.log('Testing connection to test URL...');
    await page.goto('https://geo.brdtest.com/mygeo.json', { timeout: 60000 });
    
    console.log('Getting content...');
    const content = await page.content();
    const text = await page.innerText('body');
    
    console.log('Test URL Response:');
    console.log(text);
    
    await browser.close();
    console.log('Test completed successfully');
  } catch (error) {
    console.error('Error during proxy test:', error);
  }
}

// Run the test
testProxy().catch(console.error);