// Configuration file for Perplexity.ai stealth automation

module.exports = {
  // Prompt configuration
  prompt: `What is the latest development in quantum computing?`,
  
  // Browser configuration
  browser: {
    headless: false, // Set to true for headless mode
    viewportWidth: 1920,
    viewportHeight: 1080,
    locale: 'en-US',
    timezoneId: 'America/New_York',
    latitude: 40.7128, // New York
    longitude: -74.0060,
    platform: 'MacIntel' // Platform for UserAgent (MacIntel, Win32, Linux x86_64)
  },
  
  // Proxy configuration
  proxy: {
    enabled: false, // Set to true to enable proxy
    type: 'none', // Options: none, custom, brightdata
    
    // Custom proxy configuration
    custom: {
      server: 'http://proxy.example.com:8080',
      username: 'user',
      password: 'pass'
    },
    
    // BrightData proxy configuration
    brightdata: {
      server: 'http://brd.superproxy.io:22225',
      username: 'brd-customer-YOUR_CUSTOMER_ID-zone-residential', // Replace YOUR_CUSTOMER_ID or use environment variable
      password: 'YOUR_PASSWORD', // Replace or use BRIGHT_DATA_API_KEY environment variable
      zone: 'residential' // Options: residential, datacenter, isp
    }
  },
  
  // Timing configuration
  timing: {
    typingDelayMin: 50, // Minimum delay between keystrokes (ms)
    typingDelayMax: 150, // Maximum delay between keystrokes (ms)
    mouseMovementDelayMin: 50, // Minimum delay during mouse movement (ms)
    mouseMovementDelayMax: 100, // Maximum delay during mouse movement (ms)
    responseWaitTime: 60000, // Time to wait for a response (ms)
    keepBrowserOpenTime: 30000 // Time to keep browser open after completion in non-headless mode (ms)
  },
  
  // Mouse movement configuration
  mouse: {
    movementSteps: 10, // Number of steps in Bézier curve for mouse movement
    randomizationFactor: 0.2 // Factor for randomizing control points (0-1)
  },
  
  // Debug options
  debug: {
    saveScreenshots: true,
    screenshotPath: './screenshots/',
    logUserAgent: true,
    logSelectors: true,
    verboseLogging: true
  },
  
  // Advanced options - use with caution
  advanced: {
    disableWebSecurity: false,
    disableSiteIsolation: true
  }
};