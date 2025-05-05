/**
 * No-Proxy Test for Perplexity
 * This script tests accessing Perplexity.ai directly without proxies
 * To determine if the issue is with BrightData specifically
 */

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
const fs = require('fs');
const path = require('path');

// Apply stealth plugin
chromium.use(stealth);

async function testDirectAccess() {
  console.log('Testing direct access to Perplexity.ai without proxy...');
  
  // Create screenshots directory
  const screenshotDir = path.join(__dirname, 'screenshots', 'direct');
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }
  
  try {
    // Launch browser with maximum stealth
    const browser = await chromium.launch({
      headless: false, // Use visible browser
      ignoreHTTPSErrors: true,
      args: [
        '--disable-blink-features=AutomationControlled',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-features=IsolateOrigins,site-per-process',
        '--disable-site-isolation-trials',
        '--disable-web-security',
        '--disable-extensions',
        '--disable-infobars',
        '--window-size=1920,1080',
        '--start-maximized'
      ]
    });
    
    console.log('Creating browser context with enhanced stealth...');
    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
      locale: 'en-US',
      timezoneId: 'America/New_York',
      ignoreHTTPSErrors: true
    });
    
    // Create page and navigate to Perplexity.ai
    console.log('Creating page and navigating to Perplexity.ai...');
    const page = await context.newPage();
    
    // Add stealth scripts
    await page.addInitScript(() => {
      // Hide webdriver
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
        if (parameter === 37445) return 'Google Inc.'; // VENDOR
        if (parameter === 37446) return 'ANGLE (Intel, Intel Iris Pro OpenGL Engine, OpenGL 4.1)'; // RENDERER
        return getParameter.apply(this, arguments);
      };
    });
    
    // Capture console messages
    let consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text()
      });
    });
    
    // Navigate to Perplexity
    try {
      await page.goto('https://www.perplexity.ai', { 
        waitUntil: 'networkidle',
        timeout: 60000 
      });
      
      console.log('Page loaded. Taking screenshot...');
      await page.screenshot({ 
        path: path.join(screenshotDir, 'perplexity_direct_access.png'),
        fullPage: true 
      });
      
      // Check for bot detection
      console.log('Checking for bot detection...');
      const content = await page.content();
      const botDetectionPhrases = [
        'CAPTCHA', 'captcha', 'verify you are not a bot', 
        'security check', 'blocked', 'challenge',
        'suspicious activity', 'unusual traffic',
        'verify your identity', 'check if you are a human'
      ];
      
      const detectedPhrase = botDetectionPhrases.find(phrase => content.includes(phrase));
      if (detectedPhrase) {
        console.log(`Bot protection detected: Found "${detectedPhrase}" on the page`);
        
        // Save detailed information
        fs.writeFileSync(
          path.join(screenshotDir, 'perplexity_bot_detection.txt'),
          `Bot detection phrase: ${detectedPhrase}\n\nContext: ${content.substring(content.indexOf(detectedPhrase) - 100, content.indexOf(detectedPhrase) + 100)}`
        );
      } else {
        console.log('No bot detection phrases found. Looking for input field...');
        
        // Check for input field
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
          const exists = await page.$(selector);
          if (exists) {
            console.log(`Input field found with selector: ${selector}`);
            
            // Try typing a query
            console.log('Typing a test query...');
            await exists.type('What is Claude AI?', { delay: 100 });
            await page.screenshot({ 
              path: path.join(screenshotDir, 'perplexity_with_query.png')
            });
            
            break;
          }
        }
      }
      
      // Save page content
      fs.writeFileSync(
        path.join(screenshotDir, 'perplexity_page_content.html'),
        await page.content()
      );
      
      // Wait for user to see what's happening
      console.log('Waiting 30 seconds for manual inspection...');
      await page.waitForTimeout(30000);
    } catch (error) {
      console.error('Navigation error:', error);
      fs.writeFileSync(
        path.join(screenshotDir, 'perplexity_error.txt'),
        `Error: ${error.message}\n\nStack: ${error.stack}`
      );
    }
    
    // Save console messages
    fs.writeFileSync(
      path.join(screenshotDir, 'console_messages.json'),
      JSON.stringify(consoleMessages, null, 2)
    );
    
    // Close browser
    await browser.close();
    console.log('Test completed.');
  } catch (error) {
    console.error('Test failed:', error);
  }
}

// Run the test
testDirectAccess().catch(console.error);