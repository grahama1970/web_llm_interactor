// Configuration file for Perplexity.ai stealth automation with MCP Desktop Commander

module.exports = {
  // Prompt configuration - uses MCP Desktop Commander to access local files
  // Make sure to run 'npx @anthropic-ai/desktop-commander@latest' before using this script
  prompt: `Use the local MCP tool desktop-commander to read the file located at ~/Downloads/Arc_Prize_Guide.txt. Return the file's contents. Do not use any other method. Then create a concise summary of the text file`,
  
  // Browser configuration
  browser: {
    headless: false, // Set to true for headless mode
    viewportWidth: 1920,
    viewportHeight: 1080,
    locale: 'en-US',
    timezoneId: 'America/New_York',
    latitude: 40.7128, // New York
    longitude: -74.0060
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
      username: 'brd-customer-YOUR_CUSTOMER_ID-zone-residential', // Replace YOUR_CUSTOMER_ID
      password: 'YOUR_PASSWORD',
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
    verboseLogging: true,
    // Advanced logging options
    logLevel: 'INFO',     // Options: ERROR, WARN, INFO, DEBUG, TRACE
    colorLogs: true,      // Use colored console output
    logToFile: false,     // Save logs to file
    logPath: './logs/'    // Directory for log files
  },
  
  // Advanced options - use with caution
  advanced: {
    disableWebSecurity: false,
    disableSiteIsolation: true
  },
  
  // Retry configuration
  retry: {
    enabled: true, // Enable retry mechanism
    maxRetries: 3, // Maximum number of retry attempts
    initialDelay: 2000, // Initial delay before first retry (ms)
    backoffFactor: 1.5, // Multiplier for subsequent delays
    operations: {
      navigation: true, // Retry page navigation
      inputField: true, // Retry finding input field
      responseCapture: true // Retry response capture
    }
  },
  
  // Response capture options
  responseCapture: {
    saveHtml: true, // Save HTML version of the response
    saveText: true, // Save plaintext version of the response
    saveMetadata: true, // Save links and images as metadata
    maxPreviewLength: 500, // Maximum length of console preview
    extractLinks: true, // Extract links from response
    extractImages: true, // Extract image references from response
    outputDir: './responses/' // Directory to save responses (fallback to screenshots path if not exists)
  }
};