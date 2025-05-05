/**
 * Perplexity.ai Stealth Automation
 * 
 * Automates interaction with Perplexity.ai using advanced stealth techniques
 * Configurable with BrightData proxy support
 */

const path = require('path');
const fs = require('fs');
const dotenv = require('dotenv');
const { generateBezierPath, generateRandomMouseMovements } = require('./bezier');
const { 
  getProxyConfiguration, 
  validateProxyConfig,
  saveScreenshot, 
  randomDelay,
  validateConfig,
  ensureDirectoryExists,
  withRetry
} = require('./utils');
const {
  createBrowserSetup
} = require('./browser');

// Load environment variables from .env file
dotenv.config();

// Load configuration
let config;
try {
  config = require('./config');
  
  // Check for CLI argument to load alternative config
  const configArg = process.argv.find(arg => arg.startsWith('--config='));
  if (configArg) {
    const configPath = configArg.split('=')[1];
    config = require(path.resolve(configPath));
  }
  
  // Validate configuration
  if (!validateConfig(config)) {
    process.exit(1);
  }
} catch (error) {
  console.error('Error loading configuration:', error.message);
  process.exit(1);
}

// Main function
(async () => {
  // Create screenshots directory if enabled
  if (config.debug.saveScreenshots) {
    ensureDirectoryExists(config.debug.screenshotPath);
  }
  
  // Create responses directory if configured
  if (config.responseCapture?.outputDir) {
    ensureDirectoryExists(config.responseCapture.outputDir);
  }
  
  // Get proxy configuration
  const proxyConfig = getProxyConfiguration(config.proxy);
  if (proxyConfig) {
    console.log(`Using proxy: ${config.proxy.type}`);
  }

  // Create browser, context, and page using our browser setup module
  console.log('Setting up browser with stealth configuration...');
  let browser, context, page;
  
  try {
    ({ browser, context, page } = await createBrowserSetup(config, proxyConfig));
    console.log('Browser setup complete.');
  } catch (browserSetupError) {
    console.error('Failed to set up browser:', browserSetupError.message);
    process.exit(1);
  }

  try {
    // Navigate to Perplexity.ai with retry mechanism
    console.log('Navigating to Perplexity.ai...');
    
    if (config.retry.enabled && config.retry.operations.navigation) {
      await withRetry(
        async (attempt) => {
          console.log(`Navigation attempt ${attempt + 1}${attempt > 0 ? ' (retry)' : ''}...`);
          await page.goto('https://www.perplexity.ai', { 
            waitUntil: 'networkidle', 
            timeout: 60000 
          });
          console.log('Page loaded successfully.');
        },
        {
          maxRetries: config.retry.maxRetries,
          initialDelay: config.retry.initialDelay,
          backoffFactor: config.retry.backoffFactor,
          onRetry: (error, attempt, delay) => {
            console.log(`Navigation failed (attempt ${attempt-1}). Retrying in ${Math.floor(delay/1000)} seconds...`);
            console.log(`Error: ${error.message}`);
            
            // Take screenshot of the current state for debugging
            if (config.debug.saveScreenshots) {
              saveScreenshot(page, config.debug.screenshotPath, `navigation_retry_${attempt}`).catch(() => {});
            }
          },
          shouldRetry: (error) => {
            // Only retry on timeout or connection errors
            return error.message.includes('timeout') || 
                   error.message.includes('net::') || 
                   error.message.includes('connection');
          }
        }
      );
    } else {
      // Original non-retry navigation logic
      try {
        await page.goto('https://www.perplexity.ai', { 
          waitUntil: 'networkidle', 
          timeout: 60000 
        });
        console.log('Page loaded successfully.');
      } catch (navigationError) {
        console.error(`Navigation failed: ${navigationError.message}`);
        
        if (navigationError.message.includes('timeout')) {
          console.error('TROUBLESHOOTING: The page load timed out. This could be due to:');
          console.error(' - Slow internet connection');
          console.error(' - Proxy issues (if using a proxy)');
          console.error(' - Site blocking automated access');
          console.error('Try increasing the timeout in config.js or using a residential proxy.');
        }
        
        // Take screenshot of the current state for debugging
        if (config.debug.saveScreenshots) {
          await saveScreenshot(page, config.debug.screenshotPath, 'navigation_error');
        }
        
        throw navigationError;
      }
    }

    if (config.debug.saveScreenshots) {
      await saveScreenshot(page, config.debug.screenshotPath, 'initial_page');
    }

    // Check for CAPTCHA, anti-bot page, or other blocking mechanisms
    const pageContent = await page.content();
    const botDetectionPhrases = [
      'CAPTCHA', 
      'captcha',
      'verify you are not a bot', 
      'security check', 
      'blocked', 
      'challenge',
      'suspicious activity',
      'unusual traffic',
      'verify your identity',
      'check if you are a human'
    ];
    
    const detectedPhrase = botDetectionPhrases.find(phrase => pageContent.includes(phrase));
    if (detectedPhrase) {
      if (config.debug.saveScreenshots) {
        await saveScreenshot(page, config.debug.screenshotPath, 'bot_detection');
      }
      
      console.error(`Bot protection detected: Found "${detectedPhrase}" on the page.`);
      console.error('TROUBLESHOOTING:');
      console.error(' - Try using a residential proxy (BrightData recommended)');
      console.error(' - Check if your IP address might be flagged');
      console.error(' - Try running with different User-Agent settings');
      console.error(' - Consider adjusting browser fingerprinting options');
      
      throw new Error('Bot protection detected. Consider using a CAPTCHA-solving service or residential proxy.');
    }

    // Wait for chat input with multiple selector options
    const inputSelectors = [
      'textarea#ask-input', // Primary selector based on provided HTML
      'textarea[placeholder*="Ask anything"]',
      'input[placeholder*="Ask anything"]',
      'textarea[placeholder*="Message"]',
      'textarea[id*="query"]',
      'input[id*="query"]',
      'textarea[role="textbox"]',
      'div[contenteditable="true"]', // Fallback for contenteditable
      'textarea.w-full', // Another common pattern
    ];
    
    const selectorString = inputSelectors.join(', ');
    
    if (config.debug.logSelectors) {
      console.log('Searching for input with selectors:', selectorString);
    }
    
    let inputElement = null;
    
    // Function to find input element
    const findInputElement = async () => {
      // Save page content for debugging
      console.log('Saving page content for debugging...');
      const debugDir = path.join(config.debug.screenshotPath, 'debug');
      ensureDirectoryExists(debugDir);
      const pageContent = await page.content();
      fs.writeFileSync(path.join(debugDir, 'page_content.html'), pageContent);
      console.log(`Page content saved to ${path.join(debugDir, 'page_content.html')}`);
      
      try {
        inputElement = await page.waitForSelector(selectorString, { 
          state: 'visible', 
          timeout: 15000 
        });
        
        if (inputElement) {
          return inputElement;
        }
      } catch (selectorError) {
        console.error('Failed to find input element with combined selectors.');
        
        // Try each selector individually for better diagnostics
        console.log('Checking each selector individually:');
        for (const selector of inputSelectors) {
          try {
            const exists = await page.$(selector);
            console.log(`${selector}: ${exists ? 'FOUND' : 'not found'}`);
            if (exists) {
              return exists;
            }
          } catch (e) {
            console.log(`${selector}: error - ${e.message}`);
          }
        }
        
        // If we still don't have an input element, try to find other textareas or inputs as fallback
        console.log('Trying to find any textarea or input as fallback...');
        try {
          const fallbackElement = await page.$('textarea, input[type="text"]');
          if (fallbackElement) {
            console.log('Found potential input element with fallback selector.');
            return fallbackElement;
          }
        } catch (e) {
          console.error('Fallback selector also failed:', e.message);
        }
        
        // Take a screenshot to help diagnose the issue
        if (config.debug.saveScreenshots) {
          await saveScreenshot(page, config.debug.screenshotPath, 'input_field_not_found');
        }
        
        throw new Error('Input field not found after trying all selectors');
      }
    };
    
    // Use retry mechanism if enabled
    if (config.retry.enabled && config.retry.operations.inputField) {
      try {
        inputElement = await withRetry(
          async (attempt) => {
            console.log(`Finding input field, attempt ${attempt + 1}${attempt > 0 ? ' (retry)' : ''}...`);
            
            // On retry attempts, we can try refreshing the page
            if (attempt > 0) {
              console.log('Refreshing page before retry...');
              await page.reload({ waitUntil: 'networkidle', timeout: 30000 }).catch(e => {
                console.log(`Page refresh failed: ${e.message}`);
              });
              await page.waitForTimeout(1000); // Brief pause after reload
            }
            
            return await findInputElement();
          },
          {
            maxRetries: config.retry.maxRetries,
            initialDelay: config.retry.initialDelay,
            backoffFactor: config.retry.backoffFactor,
            onRetry: (error, attempt, delay) => {
              console.log(`Failed to find input field (attempt ${attempt-1}). Retrying in ${Math.floor(delay/1000)} seconds...`);
              console.log(`Error: ${error.message}`);
              
              if (config.debug.saveScreenshots) {
                saveScreenshot(page, config.debug.screenshotPath, `input_field_retry_${attempt}`).catch(() => {});
              }
            }
          }
        );
      } catch (retryError) {
        console.error('All attempts to find input field failed.');
        console.error('TROUBLESHOOTING:');
        console.error(' - The website structure may have changed');
        console.error(' - You may be redirected to a different page');
        console.error(' - Check the screenshots to see the actual page loaded');
        throw retryError;
      }
    } else {
      // Original non-retry approach
      inputElement = await findInputElement().catch(error => {
        console.error('TROUBLESHOOTING:');
        console.error(' - The website structure may have changed');
        console.error(' - You may be redirected to a different page');
        console.error(' - Check the screenshot to see the actual page loaded');
        throw error;
      });
    }
    
    if (!inputElement) {
      throw new Error('Input field not found. Check selector or page structure.');
    }
    
    console.log('Input field found successfully.');

    // Add some random pre-interaction movements to simulate human behavior
    if (config.debug.verboseLogging) {
      console.log('Performing random mouse movements before main interaction...');
    }
    
    const randomMovements = generateRandomMouseMovements(
      3, // 3 random movements
      50, 
      config.browser.viewportWidth - 50,
      50, 
      config.browser.viewportHeight - 50
    );
    
    for (const point of randomMovements) {
      await page.mouse.move(point.x, point.y);
      await page.waitForTimeout(randomDelay(20, 50));
    }

    // Ensure input is focused
    await inputElement.focus();
    console.log('Input field focused.');

    // Get input field bounding box for mouse movement
    const inputBox = await inputElement.boundingBox();
    if (!inputBox) {
      throw new Error('Could not retrieve input field bounding box.');
    }

    // Generate Bézier spline path to input field
    const startX = 100 + Math.random() * 200;
    const startY = 100 + Math.random() * 200;
    const endX = inputBox.x + inputBox.width / 2;
    const endY = inputBox.y + inputBox.height / 2;
    
    const path = generateBezierPath(
      startX, 
      startY, 
      endX, 
      endY, 
      config.mouse.movementSteps,
      config.mouse.randomizationFactor
    );

    // Simulate human-like mouse movement
    console.log('Simulating mouse movement to input field...');
    for (const point of path) {
      await page.mouse.move(point.x, point.y);
      await page.waitForTimeout(
        randomDelay(
          config.timing.mouseMovementDelayMin, 
          config.timing.mouseMovementDelayMax
        )
      );
    }

    // Click input field
    await page.mouse.click(endX, endY);
    console.log('Input field clicked.');

    if (config.debug.saveScreenshots) {
      await saveScreenshot(page, config.debug.screenshotPath, 'input_field_focused');
    }

    // Simulate human-like typing
    console.log('Typing prompt...');
    for (const char of config.prompt) {
      await page.keyboard.type(char, { 
        delay: randomDelay(
          config.timing.typingDelayMin, 
          config.timing.typingDelayMax
        ) 
      });
    }

    // Simulate pressing Enter
    console.log('Submitting prompt...');
    await page.keyboard.press('Enter');

    if (config.debug.saveScreenshots) {
      await saveScreenshot(page, config.debug.screenshotPath, 'prompt_submitted');
    }

    // Wait for response with more robust detection
    console.log('Waiting for response...');
    
    // Determine response output directory
    const responsesDir = config.responseCapture?.outputDir || config.debug.screenshotPath;
    ensureDirectoryExists(responsesDir);
    
    // Response selectors to try (in order of preference)
    const responseSelectors = [
      '[aria-label="Answer"]', 
      '.answer-container', 
      '[data-testid="answer-container"]',
      '[role="region"]',
      '.prose', // Common class for text content
      '[data-perplexity-answer]', // Hypothetical attribute
      'div.relative > div.markdown', // Potential structure
      '[data-testid="response"]'
    ];
    
    // Function to capture response content
    const captureResponse = async () => {
      let responseElement = null;
      let responseText = '';
      let responseHtml = '';
      let responseFound = false;
      
      // First, wait for any typing/streaming indicator to disappear (signals completion)
      const typingIndicators = [
        '.typing-indicator', 
        '.loading-dots', 
        '[data-testid="streaming-indicator"]', 
        '.streaming'
      ].join(', ');
      
      console.log('Checking for typing indicators...');
      const hasTypingIndicator = await page.$(typingIndicators);
      
      if (hasTypingIndicator) {
        console.log('Typing indicator found, waiting for it to disappear...');
        await page.waitForSelector(typingIndicators, { 
          state: 'detached', 
          timeout: config.timing.responseWaitTime 
        }).catch(() => console.log('Typing indicator still present after timeout.'));
      }
      
      // Try each response selector
      for (const selector of responseSelectors) {
        try {
          responseElement = await page.$(selector);
          if (responseElement) {
            console.log(`Response found with selector: ${selector}`);
            responseFound = true;
            
            // Get text content
            responseText = await responseElement.innerText();
            
            // Get HTML content for more complete capturing (includes links, etc.)
            responseHtml = await page.evaluate(sel => {
              const element = document.querySelector(sel);
              return element ? element.outerHTML : '';
            }, selector);
            
            break;
          }
        } catch (err) {
          console.log(`Selector ${selector} check failed: ${err.message}`);
        }
      }
      
      // If no specific selector worked, try to get all text content from main areas
      if (!responseFound) {
        console.log('No specific response element found, trying general content extraction...');
        responseText = await page.evaluate(() => {
          // Get text from main content area or article elements
          const mainContent = document.querySelector('main, article, [role="main"]');
          return mainContent ? mainContent.innerText : document.body.innerText;
        });
        
        responseFound = responseText.length > 0;
      }
      
      if (!responseFound) {
        throw new Error('No response content could be extracted');
      }
      
      return { responseElement, responseText, responseHtml, responseFound };
    };
    
    // Function to save response data
    const saveResponseData = async (responseData) => {
      const { responseText, responseHtml } = responseData;
      
      console.log('Response captured successfully!');
      
      if (config.debug.saveScreenshots) {
        await saveScreenshot(page, config.debug.screenshotPath, 'response_received');
      }
      
      // Extract and save additional information if configured
      let links = [];
      let images = [];
      
      if (config.responseCapture.extractLinks) {
        links = await page.evaluate(() => {
          const linkElements = document.querySelectorAll('a[href]');
          return Array.from(linkElements).map(link => ({
            text: link.innerText,
            href: link.getAttribute('href')
          }));
        });
      }
      
      if (config.responseCapture.extractImages) {
        images = await page.evaluate(() => {
          const imgElements = document.querySelectorAll('img');
          return Array.from(imgElements).map(img => ({
            alt: img.getAttribute('alt'),
            src: img.getAttribute('src')
          })).filter(img => img.src && !img.src.startsWith('data:')); // Filter out data URLs
        });
      }
      
      // Create a timestamp for file naming
      const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
      
      // Create a response directory with timestamp
      const responseDir = path.join(responsesDir, `response_${timestamp}`);
      ensureDirectoryExists(responseDir);
      
      // Save plain text response if configured
      if (config.responseCapture.saveText) {
        const responseFile = path.join(responseDir, 'response.txt');
        fs.writeFileSync(responseFile, responseText);
        console.log(`Text response saved to: ${responseFile}`);
      }
      
      // Save HTML response if available and configured
      if (responseHtml && config.responseCapture.saveHtml) {
        const htmlFile = path.join(responseDir, 'response.html');
        fs.writeFileSync(htmlFile, responseHtml);
        console.log(`HTML response saved to: ${htmlFile}`);
      }
      
      // Save links and images as JSON if configured
      if ((links.length > 0 || images.length > 0) && config.responseCapture.saveMetadata) {
        const metadataFile = path.join(responseDir, 'metadata.json');
        fs.writeFileSync(metadataFile, JSON.stringify({
          timestamp: new Date().toISOString(),
          links,
          images,
          prompt: config.prompt
        }, null, 2));
        console.log(`Metadata saved to: ${metadataFile}`);
      }
      
      // Save a complete structured response JSON for API/CLI access
      const responseJson = {
        content: responseText,
        raw: responseHtml,
        links: links.map(link => ({
          title: link.text || '',
          url: link.href || ''
        })),
        images: images.map(img => ({
          alt: img.alt || '',
          url: img.src || ''
        })),
        metadata: {
          timestamp: new Date().toISOString(),
          query: config.prompt,
          model: "perplexity"
        }
      };
      
      fs.writeFileSync(path.join(responsesDir, 'response.json'), JSON.stringify(responseJson, null, 2));
      console.log(`Structured JSON response saved to: ${path.join(responsesDir, 'response.json')}`);
      
      
      // Save a full page screenshot
      if (config.debug.saveScreenshots) {
        await page.screenshot({ 
          path: path.join(responseDir, 'full_page.png'),
          fullPage: true
        });
      }
      
      // Save full page HTML for reference
      const fullPageHtml = path.join(responseDir, 'full_page.html');
      fs.writeFileSync(fullPageHtml, await page.content());
      
      // Display response summary
      console.log('\nResponse from Perplexity:\n------------------------');
      // Print preview based on configured max length
      const maxPreviewLength = config.responseCapture.maxPreviewLength || 500;
      const previewText = responseText.length > maxPreviewLength 
        ? responseText.substring(0, maxPreviewLength) + '...' 
        : responseText;
      console.log(previewText);
      console.log('------------------------');
      
      if (links.length > 0) {
        console.log(`Found ${links.length} links in the response`);
      }
      
      if (images.length > 0) {
        console.log(`Found ${images.length} images in the response`);
      }
      
      return responseDir;
    };
    
    // Use retry mechanism if enabled
    if (config.retry.enabled && config.retry.operations.responseCapture) {
      try {
        const responseData = await withRetry(
          async (attempt) => {
            console.log(`Capturing response, attempt ${attempt + 1}${attempt > 0 ? ' (retry)' : ''}...`);
            return await captureResponse();
          },
          {
            maxRetries: config.retry.maxRetries,
            initialDelay: config.retry.initialDelay,
            backoffFactor: config.retry.backoffFactor,
            onRetry: (error, attempt, delay) => {
              console.log(`Response capture failed (attempt ${attempt-1}). Retrying in ${Math.floor(delay/1000)} seconds...`);
              console.log(`Error: ${error.message}`);
              
              if (config.debug.saveScreenshots) {
                saveScreenshot(page, config.debug.screenshotPath, `response_retry_${attempt}`).catch(() => {});
              }
            }
          }
        );
        
        const responseDir = await saveResponseData(responseData);
        console.log(`All response data saved to: ${responseDir}`);
        
      } catch (error) {
        console.error(`All response capture attempts failed: ${error.message}`);
        console.log('Response may still be loading or page structure has changed.');
        
        if (config.debug.saveScreenshots) {
          await saveScreenshot(page, config.debug.screenshotPath, 'response_capture_failed');
        }
        
        // Attempt to save whatever page content we have
        try {
          const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
          const fullPageContent = await page.content();
          const fallbackDir = path.join(responsesDir, `fallback_${timestamp}`);
          ensureDirectoryExists(fallbackDir);
          const fallbackFile = path.join(fallbackDir, 'page_content.html');
          fs.writeFileSync(fallbackFile, fullPageContent);
          console.log(`Fallback page content saved to: ${fallbackFile}`);
        } catch (saveError) {
          console.error(`Failed to save fallback page content: ${saveError.message}`);
        }
      }
    } else {
      // Original non-retry approach
      try {
        const responseData = await captureResponse();
        await saveResponseData(responseData);
      } catch (error) {
        console.error(`Error capturing response: ${error.message}`);
        console.log('Response may still be loading or page structure has changed.');
        
        if (config.debug.saveScreenshots) {
          await saveScreenshot(page, config.debug.screenshotPath, 'response_timeout');
        }
        
        // Attempt to save whatever page content we have
        try {
          const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
          const fullPageContent = await page.content();
          const fallbackFile = path.join(config.debug.screenshotPath, `page_content_${timestamp}.html`);
          fs.writeFileSync(fallbackFile, fullPageContent);
          console.log(`Full page content saved to: ${fallbackFile}`);
        } catch (saveError) {
          console.error(`Failed to save fallback page content: ${saveError.message}`);
        }
      }
    }
  } catch (error) {
    console.error('Error:', error.message);
    
    if (config.debug.saveScreenshots) {
      try {
        await saveScreenshot(page, config.debug.screenshotPath, 'error');
      } catch (screenshotError) {
        console.error('Failed to save error screenshot:', screenshotError.message);
      }
    }
  } finally {
    // Add a delay before closing to allow viewing the result in non-headless mode
    if (!config.browser.headless) {
      console.log(`Keeping browser open for ${config.timing.keepBrowserOpenTime/1000} seconds for inspection...`);
      await page.waitForTimeout(config.timing.keepBrowserOpenTime);
    }
    
    await browser.close();
    console.log('Browser closed.');
  }
})();