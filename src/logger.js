/**
 * Logger utility for Perplexity.ai stealth automation
 * Provides consistent logging with support for different log levels
 */
const fs = require('fs');
const path = require('path');

// Log levels
const LOG_LEVELS = {
  ERROR: 0,
  WARN: 1,
  INFO: 2,
  DEBUG: 3,
  TRACE: 4
};

// ANSI color codes for terminal output
const COLORS = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  gray: '\x1b[90m',
  bold: '\x1b[1m'
};

/**
 * Logger class with support for different log levels and file output
 */
class Logger {
  /**
   * Create a new logger instance
   * @param {Object} options - Logger options
   * @param {string} options.level - Minimum log level to display (default: 'INFO')
   * @param {boolean} options.useColors - Whether to use colors in console output (default: true)
   * @param {string} options.logFile - Path to log file (optional)
   * @param {boolean} options.timestamp - Whether to include timestamps in logs (default: true)
   */
  constructor(options = {}) {
    this.level = (options.level && LOG_LEVELS[options.level.toUpperCase()]) !== undefined 
      ? LOG_LEVELS[options.level.toUpperCase()] 
      : LOG_LEVELS.INFO;
    this.useColors = options.useColors !== false;
    this.logFile = options.logFile || null;
    this.timestamp = options.timestamp !== false;
    
    // Create log directory if a file is specified
    if (this.logFile) {
      const logDir = path.dirname(this.logFile);
      if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir, { recursive: true });
      }
      
      // Initialize log file with header
      const header = `=== Perplexity.ai Stealth Automation Log ===\nStarted: ${new Date().toISOString()}\n\n`;
      fs.writeFileSync(this.logFile, header);
    }
  }
  
  /**
   * Format a log message
   * @param {string} level - Log level
   * @param {string} message - Log message
   * @returns {string} Formatted log message
   */
  formatMessage(level, message) {
    const timestamp = this.timestamp ? `[${new Date().toISOString()}] ` : '';
    return `${timestamp}${level}: ${message}`;
  }
  
  /**
   * Write a message to the log file if enabled
   * @param {string} message - Log message
   */
  writeToFile(message) {
    if (this.logFile) {
      fs.appendFileSync(this.logFile, message + '\n');
    }
  }
  
  /**
   * Log an error message
   * @param {string} message - Error message
   */
  error(message) {
    if (this.level >= LOG_LEVELS.ERROR) {
      const formattedMessage = this.formatMessage('ERROR', message);
      
      if (this.useColors) {
        console.error(`${COLORS.red}${COLORS.bold}${formattedMessage}${COLORS.reset}`);
      } else {
        console.error(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Log a warning message
   * @param {string} message - Warning message
   */
  warn(message) {
    if (this.level >= LOG_LEVELS.WARN) {
      const formattedMessage = this.formatMessage('WARN', message);
      
      if (this.useColors) {
        console.warn(`${COLORS.yellow}${formattedMessage}${COLORS.reset}`);
      } else {
        console.warn(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Log an info message
   * @param {string} message - Info message
   */
  info(message) {
    if (this.level >= LOG_LEVELS.INFO) {
      const formattedMessage = this.formatMessage('INFO', message);
      
      if (this.useColors) {
        console.info(`${COLORS.green}${formattedMessage}${COLORS.reset}`);
      } else {
        console.info(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Log a debug message
   * @param {string} message - Debug message
   */
  debug(message) {
    if (this.level >= LOG_LEVELS.DEBUG) {
      const formattedMessage = this.formatMessage('DEBUG', message);
      
      if (this.useColors) {
        console.debug(`${COLORS.blue}${formattedMessage}${COLORS.reset}`);
      } else {
        console.debug(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Log a trace message
   * @param {string} message - Trace message
   */
  trace(message) {
    if (this.level >= LOG_LEVELS.TRACE) {
      const formattedMessage = this.formatMessage('TRACE', message);
      
      if (this.useColors) {
        console.log(`${COLORS.gray}${formattedMessage}${COLORS.reset}`);
      } else {
        console.log(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Log a section header
   * @param {string} title - Section title
   */
  section(title) {
    if (this.level >= LOG_LEVELS.INFO) {
      const line = '='.repeat(title.length + 4);
      const formattedMessage = `\n${line}\n= ${title} =\n${line}`;
      
      if (this.useColors) {
        console.log(`${COLORS.cyan}${COLORS.bold}${formattedMessage}${COLORS.reset}`);
      } else {
        console.log(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Log a success message
   * @param {string} message - Success message
   */
  success(message) {
    if (this.level >= LOG_LEVELS.INFO) {
      const formattedMessage = this.formatMessage('SUCCESS', message);
      
      if (this.useColors) {
        console.log(`${COLORS.green}${COLORS.bold}${formattedMessage}${COLORS.reset}`);
      } else {
        console.log(formattedMessage);
      }
      
      this.writeToFile(formattedMessage);
    }
  }
  
  /**
   * Create a logger instance from config
   * @param {Object} config - Configuration object
   * @returns {Logger} Logger instance
   */
  static fromConfig(config) {
    const logOptions = {
      level: config.debug?.logLevel || 'INFO',
      useColors: config.debug?.colorLogs !== false,
      timestamp: true
    };
    
    if (config.debug?.logToFile) {
      const timestamp = new Date().toISOString().replace(/:/g, '-').replace(/\..+/, '');
      const logDir = config.debug?.logPath || './logs';
      logOptions.logFile = path.join(logDir, `perplexity_${timestamp}.log`);
    }
    
    return new Logger(logOptions);
  }
}

// Export a default instance
const defaultLogger = new Logger();

module.exports = {
  Logger,
  defaultLogger,
  LOG_LEVELS
};