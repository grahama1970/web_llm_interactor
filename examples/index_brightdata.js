const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
const UserAgent = require('user-agents');
const { generateBezierPath } = require('./bezier');

chromium.use(stealth);

// Configurable prompt
const prompt = `Use the local MCP tool desktop-commander to read the file located at ~/Downloads/Arc_Prize_Guide.txt. Return the file's contents. Do not use any other method. Then create a concise summary of the text file`;

// Bright Data proxy configuration (replace with your credentials)
const proxyConfig = {
  server: 'http://brd.superproxy.io:22225',
  username: 'brd-customer-<YOUR_CUSTOMER_ID>-zone-residential', // e.g., brd-customer-12345-zone-residential
  password: '<YOUR_PASSWORD>',
};

(async () => {
  // Generate random User-Agent
  const userAgent = new UserAgent({ deviceCategory: 'desktop', platform: 'MacIntel' }).toString();

  // Launch browser with stealth and proxy
  const browser = await chromium.launch({
    headless: false, // Non-headless for realism
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-dev-shm-usage',
    ],
    proxy: proxyConfig, // Bright Data proxy
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent,
    locale: 'en-US',
    timezoneId: 'America/New_York',
    geolocation: { latitude: 40.7128, longitude: -74.0060 },
  });

  const page = await context.newPage();

  // Manual fingerprint spoofing
  await page.addInitScript(() => {
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
      if (parameter === 37445) return 'WebKit'; // VENDOR
      if (parameter === 37446) return 'WebKit WebGL'; // RENDERER
      return getParameter.apply(this, arguments);
    };
  });

  try {
    // Navigate to Perplexity.ai with lenient condition
    console.log('Navigating to Perplexity.ai...');
    await page.goto('https://www.perplexity.ai', { waitUntil: 'domcontentloaded', timeout: 60000 });

    // Check for CAPTCHA or anti-bot page
    const pageContent = await page.content();
    if (pageContent.includes('CAPTCHA') || pageContent.includes('verify you are not a bot')) {
      throw new Error('CAPTCHA detected. Verify proxy configuration or integrate a CAPTCHA-solving service.');
    }

    // Wait for chat input with specific selector
    const inputSelector = [
      'textarea#ask-input', // Primary selector based on provided HTML
      'textarea[placeholder*="Ask anything"]',
      'input[placeholder*="Ask anything"]',
      'textarea[id*="query"]',
      'input[id*="query"]',
      'textarea[role="textbox"]',
      'div[contenteditable="true"]', // Fallback for contenteditable
    ].join(', ');
    console.log('Searching for input with selector:', inputSelector);

    const inputElement = await page.waitForSelector(inputSelector, { state: 'visible', timeout: 15000 });
    if (!inputElement) {
      throw new Error('Input field not found. Check selector or page structure.');
    }

    // Ensure input is focused
    await page.focus(inputSelector);
    console.log('Input field focused.');

    // Get input field bounding box for mouse movement
    const inputBox = await inputElement.boundingBox();
    if (!inputBox) {
      throw new Error('Could not retrieve input field bounding box.');
    }

    // Generate Bézier spline path to input field
    const startX = 100;
    const startY = 100;
    const endX = inputBox.x + inputBox.width / 2;
    const endY = inputBox.y + inputBox.height / 2;
    const path = generateBezierPath(startX, startY, endX, endY, 10);

    // Simulate human-like mouse movement
    console.log('Simulating mouse movement to input field...');
    for (const point of path) {
      await page.mouse.move(point.x, point.y);
      await page.waitForTimeout(50 + Math.random() * 50); // Random delay
    }

    // Click input field
    await page.mouse.click(endX, endY);
    console.log('Input field clicked.');

    // Simulate human-like typing
    console.log('Typing prompt...');
    for (const char of prompt) {
      await page.keyboard.type(char, { delay: 50 + Math.random() * 100 });
    }

    // Simulate pressing Enter
    console.log('Submitting prompt...');
    await page.keyboard.press('Enter');

    // Wait for response (adjust as needed)
    await page.waitForTimeout(5000);

    console.log('Prompt submitted successfully.');
  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await browser.close();
  }
})();