/**
 * Browser setup utilities for Perplexity.ai stealth automation
 * Provides functions for setting up the browser with proper fingerprinting and stealth
 */

const { chromium } = require('playwright-extra');
const stealth = require('puppeteer-extra-plugin-stealth')();
const UserAgent = require('user-agents');

// Apply stealth plugin to chromium
chromium.use(stealth);

/**
 * Creates a new browser instance with stealth settings
 * @param {Object} config - Configuration object
 * @param {Object} proxyConfig - Optional proxy configuration
 * @returns {Promise<Browser>} Playwright Browser instance
 */
async function setupBrowser(config, proxyConfig = null) {
  // Generate random User-Agent for configured platform
  const userAgent = new UserAgent({ 
    deviceCategory: 'desktop', 
    platform: config.browser.platform || 'MacIntel' 
  }).toString();
  
  if (config.debug.logUserAgent) {
    console.log(`Using User-Agent: ${userAgent}`);
  }
  
  // Launch browser with stealth and optional proxy
  const launchOptions = {
    headless: config.browser.headless,
    ignoreHTTPSErrors: true, // Ignore certificate errors
    args: [
      '--disable-blink-features=AutomationControlled',
      '--no-sandbox',
      '--disable-dev-shm-usage',
      '--ignore-certificate-errors', // Additional flag for certificate errors
      '--ignore-ssl-errors',         // Additional flag for SSL errors
      ...(config.advanced.disableSiteIsolation ? ['--disable-features=IsolateOrigins,site-per-process', '--disable-site-isolation-trials'] : []),
      ...(config.advanced.disableWebSecurity ? ['--disable-web-security'] : []),
    ]
  };
  
  // Only add proxy config if it exists and has required properties
  if (proxyConfig && proxyConfig.server) {
    console.log(`Adding proxy configuration: ${proxyConfig.server}`);
    launchOptions.proxy = proxyConfig;
  } else if (proxyConfig) {
    console.warn('Incomplete proxy configuration received, running without proxy');
  }
  
  const browser = await chromium.launch(launchOptions);
  
  return browser;
}

/**
 * Creates a new browser context with enhanced fingerprinting
 * @param {Browser} browser - Playwright Browser instance
 * @param {Object} config - Configuration object
 * @param {string} userAgent - User agent string
 * @returns {Promise<BrowserContext>} Playwright BrowserContext
 */
async function setupBrowserContext(browser, config, userAgent) {
  const context = await browser.newContext({
    viewport: { 
      width: config.browser.viewportWidth, 
      height: config.browser.viewportHeight 
    },
    userAgent,
    locale: config.browser.locale,
    timezoneId: config.browser.timezoneId,
    geolocation: { 
      latitude: config.browser.latitude, 
      longitude: config.browser.longitude 
    },
    ignoreHTTPSErrors: true, // Ignore certificate errors for context
  });
  
  return context;
}

/**
 * Applies fingerprint spoofing to a page
 * @param {Page} page - Playwright Page object
 * @returns {Promise<void>}
 */
async function applyFingerprintSpoofing(page) {
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
}

/**
 * Apply advanced fingerprint spoofing techniques
 * @param {Page} page - Playwright Page object
 * @param {Object} options - Options for fingerprinting
 * @returns {Promise<void>}
 */
async function applyAdvancedFingerprinting(page, options = {}) {
  // Default options
  const defaults = {
    plugins: 5,
    webGL: true,
    vendor: 'Google Inc.',
    renderer: 'ANGLE (Intel, Intel(R) UHD Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)',
    language: 'en-US',
    platform: 'MacIntel',
  };
  
  const settings = { ...defaults, ...options };
  
  await page.addInitScript(({ settings }) => {
    // Override plugins to set a specific count
    if (navigator.plugins) {
      Object.defineProperty(Navigator.prototype, 'plugins', {
        get: () => {
          const fakePlugins = new Array(settings.plugins).fill().map(() => ({
            name: 'Chromium PDF Plugin',
            filename: 'internal-pdf-viewer',
            description: 'Portable Document Format'
          }));
          
          // Create a fake PluginArray
          const plugins = Object.create(PluginArray.prototype);
          Object.defineProperties(plugins, {
            length: { value: fakePlugins.length },
            item: { value: (index) => fakePlugins[index] || null },
            namedItem: { value: (name) => fakePlugins.find(p => p.name === name) || null },
          });
          
          // Add numbered properties
          fakePlugins.forEach((plugin, i) => {
            Object.defineProperty(plugins, i, { value: plugin, enumerable: true });
          });
          
          return plugins;
        }
      });
    }
    
    // Override more fingerprinting methods as needed
    if (settings.webGL) {
      const getParameter = WebGLRenderingContext.prototype.getParameter;
      WebGLRenderingContext.prototype.getParameter = function(parameter) {
        // UNMASKED_VENDOR_WEBGL
        if (parameter === 37445) return settings.vendor;
        // UNMASKED_RENDERER_WEBGL
        if (parameter === 37446) return settings.renderer;
        return getParameter.apply(this, arguments);
      };
    }
    
    // Override language settings
    if (settings.language) {
      Object.defineProperty(navigator, 'language', { get: () => settings.language });
      Object.defineProperty(navigator, 'languages', { get: () => [settings.language, 'en'] });
    }
    
    // Override platform
    if (settings.platform) {
      Object.defineProperty(navigator, 'platform', { get: () => settings.platform });
    }
  }, { settings });
}

/**
 * Creates a complete browser setup with a page ready for navigation
 * @param {Object} config - Configuration object
 * @param {Object} proxyConfig - Optional proxy configuration
 * @returns {Promise<{browser, context, page}>} Browser components
 */
async function createBrowserSetup(config, proxyConfig = null) {
  // Generate random User-Agent for configured platform
  const userAgent = new UserAgent({ 
    deviceCategory: 'desktop', 
    platform: config.browser.platform || 'MacIntel' 
  }).toString();
  
  if (config.debug.logUserAgent) {
    console.log(`Using User-Agent: ${userAgent}`);
  }
  
  // Create browser
  const browser = await setupBrowser(config, proxyConfig);
  
  // Create context
  const context = await setupBrowserContext(browser, config, userAgent);
  
  // Create page
  const page = await context.newPage();
  
  // Apply fingerprint spoofing
  await applyFingerprintSpoofing(page);
  
  // Apply advanced fingerprinting if configured
  if (config.advanced && config.advanced.enhancedFingerprinting) {
    await applyAdvancedFingerprinting(page, config.advanced.fingerprintOptions || {});
  }
  
  return { browser, context, page };
}

module.exports = {
  setupBrowser,
  setupBrowserContext,
  applyFingerprintSpoofing,
  applyAdvancedFingerprinting,
  createBrowserSetup
};