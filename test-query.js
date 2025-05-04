#!/usr/bin/env node

/**
 * Simple test script for Perplexity.ai query with BrightData
 */

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Apply stealth plugin
chromium.use(stealth);

// BrightData configuration
const getBrightDataProxy = () => {
  const apiKey = process.env.BRIGHT_DATA_API_KEY;
  const customerId = process.env.BRD_CUSTOMER_ID || 'hl_4da0a16e';
  
  if (!apiKey) {
    console.error('BrightData API key not found in .env file');
    process.exit(1);
  }
  
  // Create a stable session ID
  const sessionId = 'test123';
  
  return {
    server: 'http://brd.superproxy.io:22225',
    username: `brd-customer-${customerId}-zone-residential_proxy1-country-us-session-${sessionId}`,
    password: apiKey
  };
};

// Create output directory
const ensureDirectoryExists = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
};

// Main function
async function main() {
  console.log('Starting Perplexity.ai test query...');
  
  // Setup output directories
  const outputDir = path.join(__dirname, 'test-output');
  ensureDirectoryExists(outputDir);
  
  // Get proxy configuration
  const proxyConfig = getBrightDataProxy();
  console.log(`Using BrightData proxy with US IP and session: test123`);
  
  // Browser launch options
  const launchOptions = {
    headless: true,
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-dev-shm-usage',
    ],
    proxy: proxyConfig
  };
  
  console.log('Launching browser...');
  const browser = await chromium.launch(launchOptions);
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'en-US',
    timezoneId: 'America/New_York',
  });
  
  // Create page and add stealth
  const page = await context.newPage();
  
  try {
    console.log('Navigating to Perplexity.ai...');
    await page.goto('https://www.perplexity.ai', { 
      waitUntil: 'networkidle',
      timeout: 60000 
    });
    console.log('Page loaded successfully');
    
    // Save initial page content
    const initialHtml = await page.content();
    fs.writeFileSync(path.join(outputDir, 'initial_page.html'), initialHtml);
    
    // Skip screenshots to avoid timeouts
    console.log('Skipping screenshots to avoid timeouts');
    
    console.log('Checking for bot detection...');
    // Check for bot detection elements
    const botDetection = await page.evaluate(() => {
      const html = document.documentElement.innerHTML;
      const botPhrases = ['captcha', 'challenge', 'security check', 'verify you are not a bot'];
      return botPhrases.some(phrase => html.toLowerCase().includes(phrase));
    });
    
    if (botDetection) {
      console.error('Bot detection found on the page');
      // Skip screenshot to avoid timeouts
      fs.writeFileSync(path.join(outputDir, 'bot_detection.txt'), 'Bot detection detected on the page');
      throw new Error('Bot detection triggered');
    }
    
    console.log('Looking for input field...');
    
    // Try to find input field with various selectors
    const inputSelectors = [
      'textarea[placeholder*="Ask"]',
      'textarea[placeholder*="Message"]',
      'textarea[id*="prompt"]',
      'textarea[aria-label*="Ask"]',
      'textarea.w-full',
      'textarea',
      'div[contenteditable="true"]',
    ];
    
    for (const selector of inputSelectors) {
      console.log(`Trying selector: ${selector}`);
      const exists = await page.$(selector);
      if (exists) {
        console.log(`Found input with selector: ${selector}`);
        
        // Click the input
        await exists.click();
        
        // Type the query
        const query = "What is the capital of France?";
        await page.keyboard.type(query, { delay: 50 });
        
        // Skip screenshot to avoid timeouts
        console.log('Input field filled with query');
        
        // Press Enter to submit
        await page.keyboard.press('Enter');
        console.log('Query submitted: ' + query);
        
        // Wait for response
        console.log('Waiting for response (30s)...');
        
        try {
          // Try to detect typing indicators
          const typingIndicator = await page.waitForSelector([
            '.typing-indicator', 
            '[data-testid="typing-indicator"]',
            '.loading',
            '.dots',
            '.streaming'
          ].join(', '), { timeout: 5000 }).catch(() => null);
          
          if (typingIndicator) {
            console.log('Typing indicator found, waiting for it to disappear...');
            await typingIndicator.waitForElementState('hidden', { timeout: 30000 }).catch(() => {});
          }
          
          // Wait a bit longer for full response
          await page.waitForTimeout(5000);
          
          console.log('Checking for response...');
          
          // Get page content with response
          const responseHtml = await page.content();
          fs.writeFileSync(path.join(outputDir, 'response_page.html'), responseHtml);
          console.log('Response page HTML saved');
          
          // Try to extract the response text
          const responseText = await page.evaluate(() => {
            // Look for answer container elements
            const answerContainer = document.querySelector('.answer-container, [data-testid="answer-container"], [aria-label="Answer"]');
            if (answerContainer) return answerContainer.innerText;
            
            // Look for any main content as fallback
            const mainContent = document.querySelector('main, article');
            if (mainContent) return mainContent.innerText;
            
            return 'No response text found';
          });
          
          console.log('\nEXTRACTED RESPONSE:\n------------------');
          console.log(responseText);
          console.log('------------------');
          
          // Save the response text
          fs.writeFileSync(path.join(outputDir, 'response.txt'), responseText);
          
          console.log('Response saved to test-output/response.txt');
          break;
        } catch (error) {
          console.error('Error capturing response:', error.message);
          fs.writeFileSync(path.join(outputDir, 'response_error.txt'), error.message);
        }
        
        break;
      }
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    fs.writeFileSync(path.join(outputDir, 'error.txt'), error.message);
  } finally {
    console.log('Closing browser...');
    await browser.close();
    console.log('Test completed. Check test-output directory for results.');
  }
}

main().catch(console.error);