#!/usr/bin/env node

/**
 * Super simple test for Perplexity.ai with BrightData
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Output directory
const outputDir = path.join(__dirname, 'simple-output');
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

// Main function
async function main() {
  console.log('Starting simple test...');
  
  // No proxy for this test
  console.log('Testing without proxy');
  
  // Launch browser
  console.log('Launching browser...');
  const browser = await chromium.launch({
    headless: true
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  
  const page = await context.newPage();
  
  try {
    console.log('Navigating to Perplexity.ai...');
    await page.goto('https://www.perplexity.ai', { timeout: 60000 });
    console.log('Page loaded');
    
    // Save page content
    const content = await page.content();
    fs.writeFileSync(path.join(outputDir, 'page.html'), content);
    console.log(`Page content saved (${content.length} bytes)`);
    
    // Save plain text of the page
    const text = await page.evaluate(() => document.body.innerText);
    fs.writeFileSync(path.join(outputDir, 'page.txt'), text);
    console.log(`Page text saved (${text.length} characters)`);
    
    // Try to check if it's a bot detection page
    const isBotPage = text.toLowerCase().includes('captcha') || 
                      text.toLowerCase().includes('challenge') ||
                      text.toLowerCase().includes('security check') ||
                      text.toLowerCase().includes('verify you are human');
                      
    if (isBotPage) {
      console.log('BOT DETECTION PAGE DETECTED');
      fs.writeFileSync(path.join(outputDir, 'is_bot_page.txt'), 'true');
    } else {
      console.log('Regular page loaded (no bot detection)');
      fs.writeFileSync(path.join(outputDir, 'is_bot_page.txt'), 'false');
    }
    
    // Try to find and use the input field
    console.log('Looking for input field...');
    const inputSelector = 'textarea[placeholder*="Ask"]';
    const inputField = await page.$(inputSelector);
    
    if (inputField) {
      console.log('Input field found! Entering query...');
      
      // Click the input field
      await inputField.click();
      
      // Type the query
      const query = "What is the capital of France?";
      await page.keyboard.type(query, { delay: 50 });
      console.log('Query typed: ' + query);
      
      // Press Enter to submit
      await page.keyboard.press('Enter');
      console.log('Query submitted');
      
      // Wait for response (up to 30 seconds)
      console.log('Waiting for response...');
      await page.waitForTimeout(10000); // Wait 10 seconds for response to start
      
      // Save the updated page content
      const responsePageContent = await page.content();
      fs.writeFileSync(path.join(outputDir, 'response_page.html'), responsePageContent);
      console.log('Response page content saved');
      
      // Try to extract the response
      const responseText = await page.evaluate(() => {
        // Common response selectors
        const selectors = [
          '[aria-label="Answer"]',
          '.answer-container',
          '[data-testid="answer-container"]',
          '.perplexity-answer',
          '.prose'
        ];
        
        // Try each selector
        for (const selector of selectors) {
          const element = document.querySelector(selector);
          if (element) return element.innerText;
        }
        
        // Fall back to body text if no specific answer container is found
        return document.body.innerText;
      });
      
      // Save the response text
      fs.writeFileSync(path.join(outputDir, 'response.txt'), responseText);
      console.log('Response saved to response.txt');
      
      // Print preview of response
      console.log('\nRESPONSE PREVIEW:\n-----------------');
      console.log(responseText.substring(0, 500));
      console.log('\n-----------------');
    } else {
      console.log('Input field not found');
    }
    
  } catch (error) {
    console.error('Error:', error.message);
    fs.writeFileSync(path.join(outputDir, 'error.txt'), error.message);
  } finally {
    await browser.close();
    console.log('Test completed. Results in simple-output directory');
  }
}

// Run the script
main().catch(console.error);