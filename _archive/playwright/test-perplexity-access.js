const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
const UserAgent = require('user-agents');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Apply stealth plugin
chromium.use(stealth);

// Enhanced stealth settings for AI site access
async function testAIAccess() {
  // Get target URL from environment variable or use default
  const targetUrl = process.env.TARGET_URL || 'https://www.perplexity.ai';
  const siteName = new URL(targetUrl).hostname;
  
  console.log(`Testing ${siteName} access with enhanced stealth...`);
  
  // Generate a more common user agent
  const userAgent = new UserAgent({ 
    deviceCategory: 'desktop',
    platform: 'MacIntel' 
  }).toString();
  
  console.log(`Using User-Agent: ${userAgent}`);
  
  // BrightData proxy settings from environment variables with fallback
  const proxyConfig = {
    server: process.env.BRD_SERVER || 'brd.superproxy.io:22225',
    username: process.env.BRD_USERNAME || 'brd-customer-hl_4da0a16e-zone-datacenter',
    password: process.env.BRD_PASSWORD || 'x8btfu41tj0i'
  };
  
  console.log('Using proxy config:', JSON.stringify(proxyConfig, null, 2));
  
  // Use proxy based on environment variable
  const useProxy = process.env.USE_PROXY !== 'false';
  
  // Launch options with enhanced stealth
  const launchOptions = {
    headless: false, // Try with visible browser first
    ignoreHTTPSErrors: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--disable-features=IsolateOrigins,site-per-process',
      '--disable-site-isolation-trials',
      '--disable-web-security',
      '--disable-extensions',
      '--disable-audio-output',
      '--disable-infobars',
      '--window-size=1920,1080',
      '--start-maximized',
      '--ignore-certificate-errors',
      '--ignore-ssl-errors'
    ]
  };
  
  // Add proxy config if enabled
  if (useProxy) {
    console.log('Using proxy configuration');
    launchOptions.proxy = proxyConfig;
  } else {
    console.log('Running without proxy');
  }
  
  try {
    console.log('Launching browser...');
    const browser = await chromium.launch(launchOptions);
    
    console.log('Creating context with enhanced fingerprinting...');
    const context = await browser.newContext({ 
      viewport: { width: 1920, height: 1080 },
      userAgent,
      ignoreHTTPSErrors: true,
      locale: 'en-US',
      timezoneId: 'America/New_York',
      geolocation: { latitude: 40.7128, longitude: -74.0060 },
      permissions: ['geolocation', 'notifications'],
      javaScriptEnabled: true,
      hasTouch: false,
      isMobile: false,
      deviceScaleFactor: 1
    });
    
    // Hide webdriver
    await context.addInitScript(() => {
      // Remove webdriver traces
      Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
      window.navigator.chrome = { runtime: {} };
      
      // Spoof navigator properties
      Object.defineProperty(navigator, 'platform', { get: () => 'MacIntel' });
      Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
      Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
      Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
      
      // Randomize canvas fingerprint
      const originalCanvas = HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext = function (type) {
        const context = originalCanvas.call(this, type);
        if (type === '2d') {
          const originalGetImageData = context.getImageData;
          context.getImageData = function (...args) {
            const imageData = originalGetImageData.apply(this, args);
            const data = imageData.data;
            for (let i = 0; i < data.length; i++) {
              data[i] = data[i] + Math.random() * 0.1; // Add noise
            }
            return imageData;
          };
        }
        return context;
      };
      
      // Spoof WebGL
      const getParameter = WebGLRenderingContext.prototype.getParameter;
      WebGLRenderingContext.prototype.getParameter = function (parameter) {
        if (parameter === 37445) return 'Intel Inc.'; // VENDOR
        if (parameter === 37446) return 'Intel Iris Pro OpenGL Engine'; // RENDERER
        return getParameter.apply(this, arguments);
      };
    });
    
    console.log('Creating page...');
    const page = await context.newPage();
    
    // Set up console messages to catch issues
    page.on('console', msg => {
      if (msg.type() === 'error' || msg.type() === 'warning') {
        console.log(`Console ${msg.type()}: ${msg.text()}`);
      }
    });
    
    // Make some random mouse movements before loading the page (looks more human)
    await page.mouse.move(150, 150);
    await page.waitForTimeout(200);
    await page.mouse.move(400, 300);
    await page.waitForTimeout(150);
    await page.mouse.move(500, 200);
    await page.waitForTimeout(250);
    
    console.log(`Navigating to ${targetUrl}...`);
    try {
      // First try to navigate, with more detailed error handling
      let response;
      try {
        response = await page.goto(targetUrl, { 
          waitUntil: 'networkidle',
          timeout: 60000 
        });
        
        console.log(`Navigation response status: ${response.status()} (${response.statusText()})`);
        
        if (!response.ok()) {
          console.log(`Got HTTP error: ${response.status()} - trying to proceed anyway`);
        }
      } catch (navError) {
        console.error(`Navigation error details: ${navError.message}`);
        
        // Try to get a screenshot even if navigation failed
        try {
          console.log('Attempting to take screenshot despite navigation error...');
          const errorScreenshot = `${siteName.replace(/\./g, '-')}-error.png`;
          await page.screenshot({ path: errorScreenshot });
          console.log(`Error screenshot saved to ${errorScreenshot}`);
        } catch (ssError) {
          console.error('Could not take error screenshot:', ssError.message);
        }
        
        // Continue and try to process the page anyway
        console.log('Attempting to proceed despite navigation error...');
      }
      
      // Try to get content even if we had errors
      console.log('Page loaded. Taking screenshot...');
      const screenshotName = `${siteName.replace(/\./g, '-')}-access-test.png`;
      await page.screenshot({ path: screenshotName, fullPage: true });
      
      console.log('Checking for CAPTCHA or challenge...');
      const pageContent = await page.content();
      const botDetectionPhrases = [
        'CAPTCHA', 'captcha', 'verify you are not a bot', 
        'security check', 'blocked', 'challenge',
        'suspicious activity', 'unusual traffic',
        'verify your identity', 'check if you are a human'
      ];
      
      const detectedPhrase = botDetectionPhrases.find(phrase => pageContent.includes(phrase));
      if (detectedPhrase) {
        console.log(`Bot protection detected: Found "${detectedPhrase}" on the page`);
      } else {
        console.log('No bot detection phrases found on the page');
      }
      
      console.log('Checking for input field...');
      const inputSelectors = [
        'textarea#ask-input',
        'textarea[placeholder*="Ask anything"]',
        'input[placeholder*="Ask anything"]',
        'textarea[placeholder*="Message"]',
        'textarea[id*="query"]',
        'input[id*="query"]',
        'textarea[role="textbox"]',
        'div[contenteditable="true"]',
        'textarea.w-full'
      ];
      
      for (const selector of inputSelectors) {
        try {
          const exists = await page.$(selector);
          console.log(`${selector}: ${exists ? 'FOUND' : 'not found'}`);
          if (exists) {
            console.log('SUCCESS: Input field found!');
            break;
          }
        } catch (e) {
          console.log(`${selector}: error - ${e.message}`);
        }
      }
      
      // Save the page content for inspection
      const debugDir = path.join(__dirname, 'debug');
      if (!fs.existsSync(debugDir)) {
        fs.mkdirSync(debugDir, { recursive: true });
      }
      fs.writeFileSync(path.join(debugDir, 'page_content.html'), pageContent);
      console.log(`Page content saved to ${path.join(debugDir, 'page_content.html')}`);
      
      // Wait for user to see the results
      console.log('Test complete. Browser will remain open for 30 seconds for inspection...');
      await page.waitForTimeout(30000);
    } catch (error) {
      console.error('Navigation error:', error);
    } finally {
      await browser.close();
      console.log('Browser closed.');
    }
  } catch (error) {
    console.error('Error during proxy test:', error);
  }
}

// Run the test
testAIAccess().catch(console.error);