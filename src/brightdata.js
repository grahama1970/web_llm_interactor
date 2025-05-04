/**
 * BrightData proxy helper for Perplexity.ai stealth automation
 */

const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

/**
 * Get BrightData proxy configuration from environment variables
 * @param {string} zone - The zone to use (residential, datacenter, isp)
 * @param {string} customerId - Optional customer ID (if not in environment)
 * @returns {Object|null} Proxy configuration for Playwright
 */
function getBrightDataProxy(zone = 'residential', customerId = null) {
  const apiKey = process.env.BRIGHT_DATA_API_KEY;
  const envCustomerId = process.env.BRD_CUSTOMER_ID;
  
  if (!apiKey && !process.env.BRD_PASSWORD) {
    console.warn('No BrightData API key found in environment variables. Set BRIGHT_DATA_API_KEY in your .env file.');
    return null;
  }
  
  if (!customerId && !envCustomerId) {
    console.warn('No BrightData customer ID found. Set BRD_CUSTOMER_ID in your .env file or pass it as parameter.');
    return null;
  }
  
  console.log('Using BrightData API key from .env file');
  
  // Use customer ID from parameter or environment
  const finalCustomerId = customerId || envCustomerId;
  
  // Password can be either API key or BRD_PASSWORD
  const password = apiKey || process.env.BRD_PASSWORD;
  
  // Use the exact zone name from the image (residential_proxy1)
  const zoneString = 'residential_proxy1';
  
  // Add custom country targeting for higher success rates with Perplexity.ai
  // US IPs tend to work well with Perplexity
  const defaultCountry = 'us';
  
  console.log(`BrightData proxy configured with zone: ${zoneString} (rotating residential IP in ${defaultCountry.toUpperCase()})`);
  
  // Advanced BrightData configuration with session persistence and country targeting
  // Create a session ID for consistency
  const sessionId = Math.random().toString(36).substring(2, 10);
  
  // Based on the working example, use this format: brd.superproxy.io:33335
  return {
    server: 'http://brd.superproxy.io:33335',
    username: `brd-customer-${finalCustomerId}-zone-${zoneString}`,  // Basic format
    password: password
  };
}

/**
 * Quick start configuration with BrightData proxy
 * @param {Object} config - Base configuration object
 * @param {Object} options - Optional BrightData configuration options
 * @returns {Object} Configuration with BrightData proxy enabled
 */
function enableBrightDataProxy(config, options = {}) {
  const proxyConfig = getBrightDataProxy(options.zone || 'residential_proxy1', options.customerId);
  
  if (!proxyConfig) {
    return config;
  }
  
  // Log additional configuration details
  console.log('Using BrightData proxy with rotating residential IPs');
  if (options.country) {
    console.log(`Targeting country: ${options.country}`);
  }
  
  // Based on the working curl example, build the username properly
  let username = proxyConfig.username;
  
  // Add country targeting if specified (after the base username)
  if (options.country) {
    username += `-country-${options.country}`;
  }
  
  // Add session persistence for consistent IP
  if (options.session !== false) {
    const sessionId = options.sessionId || Math.random().toString(36).substring(2, 10);
    username += `-session-${sessionId}`;
  }
  
  console.log(`Using proxy username: ${username}`);
  
  // Update config to use BrightData
  config.proxy = config.proxy || {};
  config.proxy.enabled = true;
  config.proxy.type = 'brightdata';
  config.proxy.brightdata = {
    server: proxyConfig.server,
    username: username,
    password: proxyConfig.password,
    zone: 'residential_proxy1'
  };
  
  return config;
}

module.exports = {
  getBrightDataProxy,
  enableBrightDataProxy
};