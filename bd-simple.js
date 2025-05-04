#!/usr/bin/env node

/**
 * Simple BrightData proxy test for Perplexity.ai
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// BrightData proxy configuration
const getProxyConfig = () => {
  const apiKey = process.env.BRIGHT_DATA_API_KEY;
  const customerId = 'hl_4da0a16e';
  
  if (!apiKey) {
    console.error('BrightData API key not found in .env file');
    process.exit(1);
  }
  
  // Simple proxy config with only essential parameters
  return {
    server: 'http://brd.superproxy.io:22225',
    username: `brd-customer-${customerId}-zone-residential`,
    password: apiKey
  };
};

// Output directory
const outputDir = path.join(__dirname, 'bd-output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Main function
async function main() {
  console.log('Starting BrightData proxy test...');
  
  // Get proxy config
  const proxyConfig = getProxyConfig();
  console.log('Using simple BrightData residential proxy configuration');
  
  try {
    // Launch browser
    console.log('Launching browser...');
    const browser = await chromium.launch({
      headless: true,
      proxy: proxyConfig
    });
    
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    });
    
    const page = await context.newPage();
    
    // Timeout config
    page.setDefaultTimeout(90000); // 90 seconds timeout
    
    // Navigate to Perplexity
    console.log('Navigating to Perplexity.ai...');
    try {
      await page.goto('https://www.perplexity.ai');
      console.log('Page loaded successfully!');
      
      // Save page content
      const content = await page.content();
      fs.writeFileSync(path.join(outputDir, 'page.html'), content);
      console.log(`Page HTML saved (${content.length} bytes)`);
      
      // Check if we got the main page or a challenge page
      const bodyText = await page.evaluate(() => document.body.innerText);
      fs.writeFileSync(path.join(outputDir, 'page_text.txt'), bodyText);
      
      // Look for bot detection phrases
      const isBotPage = 
        bodyText.includes('challenge') || 
        bodyText.includes('captcha') || 
        bodyText.includes('Cloudflare') ||
        bodyText.includes('security check') ||
        bodyText.includes('verify you are human');
      
      if (isBotPage) {
        console.log('⚠️ Bot detection page detected');
        fs.writeFileSync(path.join(outputDir, 'is_bot_page.txt'), 'true');
      } else {
        console.log('✅ Main page loaded successfully (no bot detection)');
        fs.writeFileSync(path.join(outputDir, 'is_bot_page.txt'), 'false');
        
        // Try to find and interact with the input field
        const inputSelector = 'textarea[placeholder*="Ask"]';
        console.log(`Looking for input field with selector: ${inputSelector}`);
        
        const inputExists = await page.$(inputSelector);
        if (inputExists) {
          console.log('✅ Input field found!');
          
          // Enter query
          await inputExists.click();
          await page.keyboard.type('What is the capital of France?');
          console.log('Query typed into input field');
          
          // Submit query
          await page.keyboard.press('Enter');
          console.log('Query submitted');
          
          // Wait for response loading
          console.log('Waiting for response (15s)...');
          await page.waitForTimeout(15000);
          
          // Save response page
          const responseContent = await page.content();
          fs.writeFileSync(path.join(outputDir, 'response_page.html'), responseContent);
          
          // Try to extract response text
          const responseText = await page.evaluate(() => {
            const possibleSelectors = [
              '[aria-label="Answer"]',
              '.answer-container',
              '.perplexity-response',
              '.prose'
            ];
            
            for (const selector of possibleSelectors) {
              const element = document.querySelector(selector);
              if (element) return element.innerText;
            }
            
            return document.body.innerText;
          });
          
          fs.writeFileSync(path.join(outputDir, 'response.txt'), responseText);
          console.log('Response saved to bd-output/response.txt');
          
          // Print preview
          console.log('\nRESPONSE PREVIEW:');
          console.log('-----------------');
          console.log(responseText.substring(0, 300));
          console.log('-----------------');
        } else {
          console.log('❌ Input field not found');
        }
      }
    } catch (navError) {
      console.error('Navigation error:', navError.message);
      fs.writeFileSync(path.join(outputDir, 'navigation_error.txt'), navError.message);
    }
    
    // Close browser
    await browser.close();
    
  } catch (error) {
    console.error('Error:', error.message);
    fs.writeFileSync(path.join(outputDir, 'error.txt'), error.message);
  }
  
  console.log('Test completed. Results in bd-output directory');
}

// Run the script
main().catch(console.error);