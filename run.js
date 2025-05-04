#!/usr/bin/env node

/**
 * Command-line runner for Perplexity.ai stealth automation
 * Provides easy configuration of proxy and other settings
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const readline = require('readline');
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

// Parse command line arguments
const args = process.argv.slice(2);
const flags = {};
const params = {};

args.forEach(arg => {
  if (arg.startsWith('--')) {
    const [key, value] = arg.substring(2).split('=');
    flags[key] = value || true;
  } else if (arg.startsWith('-')) {
    flags[arg.substring(1)] = true;
  } else {
    const [key, value] = arg.split('=');
    if (value) {
      params[key] = value;
    }
  }
});

// Default config file
const CONFIG_FILE = path.join(__dirname, 'src/config.js');
let config;

// Check if config.js exists and load it
try {
  config = require(CONFIG_FILE);
} catch (error) {
  console.error('Error loading configuration file:', error.message);
  process.exit(1);
}

// Interactive mode for setting up BrightData proxy
async function setupBrightData() {
  // Check if we already have the API key in .env
  const brightDataApiKey = process.env.BRIGHT_DATA_API_KEY;
  
  if (brightDataApiKey) {
    console.log('\n=== BrightData API Key found in .env file ===');
    console.log('Using existing BrightData API key from environment variables');
    
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const ask = (question) => new Promise(resolve => rl.question(question, resolve));
    
    // Still ask for customer ID since it might not be in .env
    const customerId = await ask('Enter your BrightData Customer ID (or press Enter to input manually): ') || '';
    let password = brightDataApiKey; // Use the API key from .env
    
    if (!customerId) {
      console.log('No Customer ID provided, requesting full credentials...');
      console.log('Note: API key from .env will be used as password if no password is provided');
    }
    
    // Only ask for password if the user wants to manually input it
    if (!customerId) {
      const manualPassword = await ask('Enter your BrightData Password (press Enter to use API key from .env): ');
      if (manualPassword) {
        password = manualPassword;
      }
    }
    
    const zone = await ask('Enter Zone (residential, datacenter, isp) [default: residential]: ') || 'residential';
    
    rl.close();
    
    // Update config object
    config.proxy.enabled = true;
    config.proxy.type = 'brightdata';
    config.proxy.brightdata.username = customerId 
      ? config.proxy.brightdata.username.replace('YOUR_CUSTOMER_ID', customerId)
      : config.proxy.brightdata.username;
    config.proxy.brightdata.password = password;
    config.proxy.brightdata.zone = zone;
    
    return { customerId, password, zone };
  } else {
    // Standard interactive flow if no API key in .env
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });

    const ask = (question) => new Promise(resolve => rl.question(question, resolve));

    console.log('\n=== BrightData Proxy Configuration ===');
    
    const customerId = await ask('Enter your BrightData Customer ID: ');
    const password = await ask('Enter your BrightData Password: ');
    const zone = await ask('Enter Zone (residential, datacenter, isp) [default: residential]: ') || 'residential';
    
    rl.close();
    
    // Update config object
    config.proxy.enabled = true;
    config.proxy.type = 'brightdata';
    config.proxy.brightdata.username = config.proxy.brightdata.username.replace('YOUR_CUSTOMER_ID', customerId);
    config.proxy.brightdata.password = password;
    config.proxy.brightdata.zone = zone;
    
    return { customerId, password, zone };
  }
}

// Main function
async function main() {
  // Show help if requested
  if (flags.h || flags.help) {
    console.log(`
Perplexity.ai Stealth Automation Runner

Usage:
  node run.js [options]

Options:
  --help, -h                      Show this help message
  --config=<path>                 Use custom config file
  --headless                      Run in headless mode
  --proxy=<type>                  Use proxy (none, custom, brightdata)
  --brd-country=<code>            Set country for BrightData proxy (US, GB, DE, etc.)
  --brd-session=<id>              Set session ID for BrightData proxy (for consistent IP)
  --interactive, -i               Configure proxy interactively
  --prompt=<text>                 Override prompt in config
  --output-dir=<path>             Directory to save responses (default: ./responses/)
  --screenshots-dir=<path>        Directory to save screenshots (default: ./screenshots/)
  --disable-screenshots           Don't capture screenshots
  --log-level=<level>             Set log level (ERROR, WARN, INFO, DEBUG, TRACE)
  --log-file                      Save logs to file
  --disable-colors                Disable colored console output
  --retries=<number>              Number of retry attempts (default: 3)
  --timeout=<ms>                  Response wait timeout in ms (default: 60000)
  --browser-open-time=<ms>        Time to keep browser open after completion (default: 30000)
  --max-preview-length=<chars>    Maximum length of response preview (default: 500)
  
Examples:
  node run.js --headless                             # Run in headless mode
  node run.js --proxy=brightdata -i                  # Configure BrightData proxy interactively
  node run.js --prompt="What is the capital of France?" # Override the prompt
  node run.js --config=./my-config.js                # Use custom config file
  node run.js --log-level=DEBUG --log-file           # Enable debug logging with file output
  node run.js --output-dir=./my-responses            # Save responses to custom directory
  node run.js --retries=5 --timeout=90000            # Increase retries and timeout
    `);
    return;
  }

  // Handle custom config file
  if (flags.config) {
    const customConfigPath = path.resolve(flags.config);
    if (fs.existsSync(customConfigPath)) {
      process.env.NODE_CONFIG_PATH = customConfigPath;
    } else {
      console.error(`Config file not found: ${customConfigPath}`);
      return;
    }
  }

  // Handle proxy configuration
  if (flags.proxy) {
    config.proxy.enabled = flags.proxy !== 'none';
    config.proxy.type = flags.proxy;
    
    // Interactive mode for BrightData
    if ((flags.proxy === 'brightdata' || flags.proxy === 'bd') && (flags.i || flags.interactive)) {
      const bdConfig = await setupBrightData();
      process.env.BRD_CUSTOMER_ID = bdConfig.customerId;
      process.env.BRD_PASSWORD = bdConfig.password;
    } else if (flags.proxy === 'brightdata' || flags.proxy === 'bd') {
      // Non-interactive mode but use the API key from .env if available
      if (process.env.BRIGHT_DATA_API_KEY) {
        console.log('Using BrightData API key from .env file');
        config.proxy.brightdata.password = process.env.BRIGHT_DATA_API_KEY;
        
        // Load the brightdata module
        const { enableBrightDataProxy } = require('./src/brightdata');
        
        // Add advanced BrightData options
        const brightDataOptions = {};
        
        // Add country targeting if specified
        if (flags['brd-country']) {
          brightDataOptions.country = flags['brd-country'];
          console.log(`BrightData country targeting: ${flags['brd-country']}`);
        }
        
        // Add session ID if specified
        if (flags['brd-session']) {
          brightDataOptions.sessionId = flags['brd-session'];
          console.log(`BrightData session ID: ${flags['brd-session']}`);
        }
        
        // Enable BrightData proxy with options
        config = enableBrightDataProxy(config, brightDataOptions);
      }
    }
  }
  
  // Handle headless mode
  if (flags.headless) {
    config.browser.headless = true;
  }
  
  // Handle prompt override
  if (flags.prompt) {
    config.prompt = flags.prompt;
  }
  
  // Handle response output directory
  if (flags['output-dir']) {
    config.responseCapture = config.responseCapture || {};
    config.responseCapture.outputDir = path.resolve(flags['output-dir']);
  }
  
  // Handle screenshots directory
  if (flags['screenshots-dir']) {
    config.debug.screenshotPath = path.resolve(flags['screenshots-dir']);
  }
  
  // Handle screenshot disable
  if (flags['disable-screenshots']) {
    config.debug.saveScreenshots = false;
  }
  
  // Handle logging options
  if (flags['log-level']) {
    const validLevels = ['ERROR', 'WARN', 'INFO', 'DEBUG', 'TRACE'];
    const level = flags['log-level'].toUpperCase();
    if (validLevels.includes(level)) {
      config.debug.logLevel = level;
    } else {
      console.warn(`Invalid log level: ${flags['log-level']}. Using default: INFO`);
    }
  }
  
  // Handle log file
  if (flags['log-file']) {
    config.debug.logToFile = true;
  }
  
  // Handle color disable
  if (flags['disable-colors']) {
    config.debug.colorLogs = false;
  }
  
  // Handle retry count
  if (flags.retries) {
    const retries = parseInt(flags.retries, 10);
    if (!isNaN(retries) && retries >= 0) {
      config.retry = config.retry || {};
      config.retry.maxRetries = retries;
    }
  }
  
  // Handle timeout
  if (flags.timeout) {
    const timeout = parseInt(flags.timeout, 10);
    if (!isNaN(timeout) && timeout > 1000) {
      config.timing.responseWaitTime = timeout;
    }
  }
  
  // Handle browser open time
  if (flags['browser-open-time']) {
    const openTime = parseInt(flags['browser-open-time'], 10);
    if (!isNaN(openTime) && openTime >= 0) {
      config.timing.keepBrowserOpenTime = openTime;
    }
  }
  
  // Handle max preview length
  if (flags['max-preview-length']) {
    const previewLength = parseInt(flags['max-preview-length'], 10);
    if (!isNaN(previewLength) && previewLength > 0) {
      config.responseCapture = config.responseCapture || {};
      config.responseCapture.maxPreviewLength = previewLength;
    }
  }
  
  // Set environment variables for production mode if headless
  if (config.browser.headless) {
    process.env.NODE_ENV = 'production';
  }
  
  // Create temporary config file for the run
  const tmpConfig = path.join(__dirname, '.tmp-config.js');
  fs.writeFileSync(tmpConfig, `module.exports = ${JSON.stringify(config, null, 2)};`);
  
  // Run the main script
  const scriptPath = path.join(__dirname, 'src/index.js');
  
  // ANSI color codes for terminal output
  const COLORS = {
    reset: '\x1b[0m',
    red: '\x1b[31m',
    green: '\x1b[32m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    magenta: '\x1b[35m',
    cyan: '\x1b[36m',
    bold: '\x1b[1m'
  };
  
  const ENABLED = `${COLORS.green}enabled${COLORS.reset}`;
  const DISABLED = `${COLORS.yellow}disabled${COLORS.reset}`;
  
  // Print startup banner
  console.log('\n' + COLORS.cyan + COLORS.bold);
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║  PERPLEXITY.AI STEALTH AUTOMATION                          ║');
  console.log('║  With MCP Desktop Commander Integration                    ║');
  console.log('╚════════════════════════════════════════════════════════════╝');
  console.log(COLORS.reset);
  
  console.log(`${COLORS.cyan}${COLORS.bold}[CONFIGURATION]${COLORS.reset}`);
  console.log(`▶ Headless mode: ${config.browser.headless ? ENABLED : DISABLED}`);
  console.log(`▶ Proxy: ${config.proxy.enabled ? `${COLORS.green}${config.proxy.type}${COLORS.reset}` : DISABLED}`);
  console.log(`▶ Retry mechanism: ${config.retry?.enabled ? `${ENABLED} (max ${config.retry.maxRetries} retries)` : DISABLED}`);
  console.log(`▶ Screenshots: ${config.debug.saveScreenshots ? `${ENABLED} (dir: ${config.debug.screenshotPath})` : DISABLED}`);
  
  if (config.responseCapture) {
    console.log(`▶ Response capture: ${ENABLED}`);
    console.log(`  ├─ Output directory: ${config.responseCapture.outputDir || config.debug.screenshotPath}`);
    console.log(`  ├─ Save text: ${config.responseCapture.saveText !== false ? ENABLED : DISABLED}`);
    console.log(`  ├─ Save HTML: ${config.responseCapture.saveHtml ? ENABLED : DISABLED}`);
    console.log(`  └─ Extract metadata: ${config.responseCapture.saveMetadata ? ENABLED : DISABLED}`);
  }
  
  console.log(`▶ Log level: ${COLORS.blue}${config.debug.logLevel || 'INFO'}${COLORS.reset}`);
  console.log(`▶ Log to file: ${config.debug.logToFile ? ENABLED : DISABLED}`);
  console.log(`\n${COLORS.magenta}${COLORS.bold}[PROMPT]${COLORS.reset}`);
  console.log(`${config.prompt.substring(0, 80)}${config.prompt.length > 80 ? '...' : ''}`);
  
  console.log(`\n${COLORS.green}${COLORS.bold}[STARTING]${COLORS.reset} Launching browser...`);
  
  const child = spawn('node', [scriptPath, `--config=${tmpConfig}`], {
    stdio: 'inherit'
  });
  
  child.on('close', (code) => {
    // Clean up temporary config
    if (fs.existsSync(tmpConfig)) {
      fs.unlinkSync(tmpConfig);
    }
    
    console.log(`\nPerplexity.ai automation completed with exit code ${code}`);
  });
}

// Run the main function
main().catch(error => {
  console.error('Error:', error.message);
  process.exit(1);
});