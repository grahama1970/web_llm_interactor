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
  
  return {
    server: 'http://brd.superproxy.io:22225',
    username: `brd-customer-${finalCustomerId}-zone-${zone}`,
    password: password
  };
}

/**
 * Quick start configuration with BrightData proxy
 * @param {Object} config - Base configuration object
 * @returns {Object} Configuration with BrightData proxy enabled
 */
function enableBrightDataProxy(config) {
  const proxyConfig = getBrightDataProxy();
  
  if (!proxyConfig) {
    return config;
  }
  
  // Update config to use BrightData
  config.proxy = config.proxy || {};
  config.proxy.enabled = true;
  config.proxy.type = 'brightdata';
  config.proxy.brightdata = {
    server: proxyConfig.server,
    username: proxyConfig.username,
    password: proxyConfig.password,
    zone: 'residential'
  };
  
  return config;
}

module.exports = {
  getBrightDataProxy,
  enableBrightDataProxy
};