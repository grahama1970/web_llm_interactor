/**
 * Utility functions for Perplexity stealth automation
 */
const fs = require('fs');
const path = require('path');

/**
 * Creates directory if it doesn't exist
 * @param {string} dirPath - Directory path to create
 */
function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Executes a function with retry logic
 * @param {Function} fn - Async function to execute
 * @param {Object} options - Retry options
 * @param {number} options.maxRetries - Maximum number of retry attempts (default: 3)
 * @param {number} options.initialDelay - Initial delay in ms before first retry (default: 1000)
 * @param {number} options.backoffFactor - Multiplier for subsequent delays (default: 1.5)
 * @param {Function} options.shouldRetry - Function to determine if retry is needed (default: retry on any error)
 * @param {Function} options.onRetry - Callback function before each retry attempt
 * @returns {Promise<any>} - Result of the function execution
 */
async function withRetry(fn, options = {}) {
  const {
    maxRetries = 3,
    initialDelay = 1000,
    backoffFactor = 1.5,
    shouldRetry = () => true,
    onRetry = () => {}
  } = options;

  let lastError;
  let delay = initialDelay;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn(attempt);
    } catch (error) {
      lastError = error;
      
      if (attempt === maxRetries || !shouldRetry(error, attempt)) {
        break;
      }
      
      // Wait before retry with exponential backoff
      await new Promise(resolve => setTimeout(resolve, delay));
      delay = Math.floor(delay * backoffFactor);
      
      // Call the onRetry callback
      onRetry(error, attempt + 1, delay);
    }
  }

  throw lastError;
}

/**
 * Validates proxy configuration and provides useful error messages
 * @param {Object} proxyConfig - Proxy configuration to validate
 * @returns {Object} Validation result with isValid and error properties
 */
function validateProxyConfig(proxyConfig) {
  if (!proxyConfig) {
    return { isValid: false, error: 'Proxy configuration is missing' };
  }
  
  if (!proxyConfig.enabled) {
    return { isValid: true, error: null }; // Not enabled, so no validation needed
  }
  
  // Common validation for any proxy type
  if (!proxyConfig.type) {
    return { isValid: false, error: 'Proxy type is missing' };
  }
  
  switch (proxyConfig.type) {
    case 'none':
      return { isValid: true, error: null };
      
    case 'brightdata':
      if (!proxyConfig.brightdata) {
        return { isValid: false, error: 'BrightData proxy configuration is missing' };
      }
      
      // Check for required BrightData fields
      if (!proxyConfig.brightdata.server) {
        return { isValid: false, error: 'BrightData server URL is missing' };
      }
      
      // Check if username contains placeholder
      if (proxyConfig.brightdata.username.includes('YOUR_CUSTOMER_ID') && !process.env.BRD_CUSTOMER_ID) {
        return { 
          isValid: false, 
          error: 'BrightData customer ID is missing. Set BRD_CUSTOMER_ID in environment variables or update config.js' 
        };
      }
      
      // Check if password contains placeholder
      if (proxyConfig.brightdata.password.includes('YOUR_PASSWORD') && 
          !process.env.BRIGHT_DATA_API_KEY && 
          !process.env.BRD_PASSWORD) {
        return { 
          isValid: false, 
          error: 'BrightData password/API key is missing. Set BRIGHT_DATA_API_KEY or BRD_PASSWORD in environment variables or update config.js' 
        };
      }
      
      return { isValid: true, error: null };
      
    case 'custom':
      if (!proxyConfig.custom) {
        return { isValid: false, error: 'Custom proxy configuration is missing' };
      }
      
      // Check for required custom proxy fields
      if (!proxyConfig.custom.server) {
        return { isValid: false, error: 'Custom proxy server URL is missing' };
      }
      
      return { isValid: true, error: null };
      
    default:
      return { 
        isValid: false, 
        error: `Unknown proxy type: ${proxyConfig.type}. Supported types are: none, custom, brightdata` 
      };
  }
}

/**
 * Gets proxy configuration based on settings
 * @param {Object} proxyConfig - Proxy configuration from config file
 * @returns {Object|null} Playwright proxy configuration or null if disabled
 */
function getProxyConfiguration(proxyConfig) {
  if (!proxyConfig.enabled) {
    return null;
  }
  
  // Validate proxy configuration
  const validation = validateProxyConfig(proxyConfig);
  if (!validation.isValid) {
    console.error(`Proxy configuration error: ${validation.error}`);
    console.error('Running without proxy due to configuration error.');
    return null;
  }
  
  switch (proxyConfig.type) {
    case 'brightdata':
      const zone = proxyConfig.brightdata.zone || 'residential';
      
      // Check for API key in environment variables
      const brightDataApiKey = process.env.BRIGHT_DATA_API_KEY || process.env.BRD_PASSWORD || '';
      
      // Use either the customer ID from config or environment
      const customerId = process.env.BRD_CUSTOMER_ID || '';
      
      // Create the proxy configuration
      const brightdataProxy = {
        server: proxyConfig.brightdata.server,
        username: customerId 
          ? proxyConfig.brightdata.username.replace('YOUR_CUSTOMER_ID', customerId)
          : proxyConfig.brightdata.username,
        password: brightDataApiKey || proxyConfig.brightdata.password
      };
      
      console.log(`BrightData proxy configured with zone: ${zone}`);
      return brightdataProxy;
      
    case 'custom':
      console.log(`Custom proxy configured: ${proxyConfig.custom.server}`);
      return {
        server: proxyConfig.custom.server,
        username: proxyConfig.custom.username,
        password: proxyConfig.custom.password
      };
      
    default:
      return null;
  }
}

/**
 * Saves screenshot with timestamp
 * @param {Object} page - Playwright page object
 * @param {string} screenshotPath - Path to save screenshots
 * @param {string} prefix - Prefix for the filename
 */
async function saveScreenshot(page, screenshotPath, prefix = 'screenshot') {
  ensureDirectoryExists(screenshotPath);
  const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
  const filename = `${prefix}_${timestamp}.png`;
  const filepath = path.join(screenshotPath, filename);
  
  await page.screenshot({ path: filepath });
  console.log(`Screenshot saved: ${filepath}`);
  
  return filepath;
}

/**
 * Generates a random delay within range
 * @param {number} min - Minimum delay in ms
 * @param {number} max - Maximum delay in ms
 * @returns {number} Random delay in ms
 */
function randomDelay(min, max) {
  return min + Math.random() * (max - min);
}

/**
 * Validates configuration object
 * @param {Object} config - Configuration object
 * @returns {boolean} True if valid
 */
function validateConfig(config) {
  // Basic validation
  if (!config) {
    console.error('Error: Configuration is missing');
    return false;
  }
  
  // Check for required fields
  if (!config.prompt) {
    console.error('Error: Prompt is required in configuration');
    return false;
  }
  
  // Check for proxy configuration
  if (config.proxy?.enabled) {
    if (config.proxy.type === 'brightdata') {
      if (!process.env.BRD_CUSTOMER_ID && config.proxy.brightdata.username.includes('YOUR_CUSTOMER_ID')) {
        console.warn('Warning: BRD_CUSTOMER_ID environment variable not set for BrightData proxy');
      }
      if (!process.env.BRD_PASSWORD && config.proxy.brightdata.password.includes('YOUR_PASSWORD')) {
        console.warn('Warning: BRD_PASSWORD environment variable not set for BrightData proxy');
      }
    }
  }
  
  return true;
}

module.exports = {
  ensureDirectoryExists,
  getProxyConfiguration,
  validateProxyConfig,
  saveScreenshot,
  randomDelay,
  validateConfig,
  withRetry
};