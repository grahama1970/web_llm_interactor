/**
 * Output formatter for Perplexity Stealth Automation
 * Formats responses as rich tables for humans or structured JSON for AI agents
 */

const chalk = require('chalk');
const Table = require('cli-table3');
const stripAnsi = require('strip-ansi');

/**
 * Format response data as a rich table for human consumption
 * @param {Object} responseData - The response data from Perplexity
 * @param {Object} options - Format options
 * @returns {String} Formatted table output
 */
function formatAsTable(responseData, options = {}) {
  const { 
    color = true, 
    maxWidth = 100, 
    includeMetadata = true,
    includeLinks = true 
  } = options;

  // Format styles
  const styles = {
    title: color ? chalk.bold.cyan : text => text,
    header: color ? chalk.bold.white : text => text,
    metadata: color ? chalk.dim : text => text,
    text: color ? chalk.white : text => text,
    link: color ? chalk.blue.underline : text => text,
    source: color ? chalk.green : text => text,
    timestamp: color ? chalk.gray : text => text
  };

  // Create table header
  const table = new Table({
    head: [styles.header('Perplexity Response')],
    style: {
      head: color ? ['cyan'] : []
    },
    wordWrap: true,
    wrapOnWordBoundary: true,
    colWidths: [maxWidth]
  });

  // Add metadata
  if (includeMetadata && responseData.metadata) {
    const metadata = [];
    
    if (responseData.metadata.timestamp) {
      const date = new Date(responseData.metadata.timestamp);
      metadata.push(styles.timestamp(`Time: ${date.toLocaleString()}`));
    }
    
    if (responseData.metadata.model) {
      metadata.push(styles.metadata(`Model: ${responseData.metadata.model}`));
    }
    
    if (responseData.metadata.query) {
      metadata.push(styles.metadata(`Query: ${responseData.metadata.query}`));
    }
    
    if (metadata.length > 0) {
      table.push([metadata.join('\n')]);
    }
  }

  // Add response content
  if (responseData.content) {
    // Process content - clean up formatting, wrap text
    const content = wordWrap(responseData.content, maxWidth - 4);
    table.push([styles.text(content)]);
  }

  // Add links
  if (includeLinks && responseData.links && responseData.links.length > 0) {
    const linkTable = new Table({
      head: [styles.header('Source'), styles.header('URL')],
      style: {
        head: color ? ['cyan'] : []
      },
      colWidths: [Math.floor(maxWidth * 0.3), Math.floor(maxWidth * 0.7)]
    });

    responseData.links.forEach(link => {
      linkTable.push([
        styles.source(truncate(link.title || 'Source', Math.floor(maxWidth * 0.3) - 4)),
        styles.link(truncate(link.url, Math.floor(maxWidth * 0.7) - 4))
      ]);
    });

    table.push([{ content: linkTable.toString(), colSpan: 1 }]);
  }

  return table.toString();
}

/**
 * Format response data as JSON for agent consumption
 * @param {Object} responseData - The response data from Perplexity
 * @param {Object} options - Format options
 * @returns {String} JSON string
 */
function formatAsJson(responseData, options = {}) {
  const { pretty = true, includeRaw = false } = options;
  
  // Create a clean copy of the data for JSON output
  const jsonData = {
    success: true,
    timestamp: new Date().toISOString(),
    query: responseData.metadata?.query || '',
    content: responseData.content || '',
    links: (responseData.links || []).map(link => ({
      title: link.title || '',
      url: link.url || ''
    }))
  };
  
  // Add raw data if requested
  if (includeRaw && responseData.raw) {
    jsonData.raw = responseData.raw;
  }
  
  // Add optional fields if they exist
  if (responseData.metadata) {
    if (responseData.metadata.model) {
      jsonData.model = responseData.metadata.model;
    }
    if (responseData.metadata.timestamp) {
      jsonData.query_time = responseData.metadata.timestamp;
    }
  }
  
  return pretty ? JSON.stringify(jsonData, null, 2) : JSON.stringify(jsonData);
}

/**
 * Format the output based on the requested format
 * @param {Object} responseData - The response data from Perplexity
 * @param {String} format - The output format (table, json)
 * @param {Object} options - Format options
 * @returns {String} Formatted output
 */
function formatOutput(responseData, format = 'table', options = {}) {
  if (format === 'json') {
    return formatAsJson(responseData, options);
  } else {
    return formatAsTable(responseData, options);
  }
}

/**
 * Simple word wrap function
 * @param {String} text - Text to wrap
 * @param {Number} width - Maximum width
 * @returns {String} Wrapped text
 */
function wordWrap(text, width) {
  const cleanText = stripAnsi(text || '').replace(/\r\n/g, '\n');
  const words = cleanText.split(' ');
  let line = '';
  let result = '';
  
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    
    if (word.includes('\n')) {
      const parts = word.split('\n');
      line += parts[0];
      result += line + '\n';
      
      for (let j = 1; j < parts.length - 1; j++) {
        result += parts[j] + '\n';
      }
      
      line = parts[parts.length - 1] + ' ';
      continue;
    }
    
    if (line.length + word.length + 1 > width) {
      result += line.trim() + '\n';
      line = word + ' ';
    } else {
      line += word + ' ';
    }
  }
  
  if (line.trim()) {
    result += line.trim();
  }
  
  return result;
}

/**
 * Truncate text with ellipsis
 * @param {String} text - Text to truncate
 * @param {Number} length - Maximum length
 * @returns {String} Truncated text
 */
function truncate(text, length) {
  if (!text) return '';
  const cleanText = stripAnsi(text);
  return cleanText.length > length 
    ? cleanText.substring(0, length - 3) + '...' 
    : cleanText;
}

module.exports = {
  formatOutput,
  formatAsTable,
  formatAsJson
};