# Output Formatter

The Output Formatter is a utility module that provides flexible formatting of Perplexity.ai responses for both human users and AI agents. It supports two primary output formats:

1. **Table Format**: Rich, colorful tables designed for human readability
2. **JSON Format**: Structured data designed for AI agents and programmatic processing

## Installation

The Output Formatter is bundled with the Perplexity Stealth Automation tool. It's available by importing from the `output-formatter.js` file:

```javascript
const { formatOutput, formatAsTable, formatAsJson } = require('./output-formatter');
```

Make sure the required dependencies are installed:

```
npm install cli-table3 chalk strip-ansi
```

## API Reference

### formatOutput(responseData, format, options)

Main formatting function that auto-selects the appropriate formatter based on the requested format.

**Parameters:**
- `responseData` (Object): The response data from Perplexity.ai
- `format` (String): The output format, either 'table' or 'json'
- `options` (Object): Format-specific options

**Returns:**
- (String): Formatted output string

**Example:**
```javascript
const formattedOutput = formatOutput(responseData, 'table', {
  color: true,
  maxWidth: 100
});
console.log(formattedOutput);
```

### formatAsTable(responseData, options)

Formats response data as a rich table for human consumption.

**Parameters:**
- `responseData` (Object): The response data from Perplexity.ai
- `options` (Object): Table formatting options
  - `color` (Boolean): Enable/disable colors (default: true)
  - `maxWidth` (Number): Maximum width of the table (default: 100)
  - `includeMetadata` (Boolean): Include metadata section (default: true)
  - `includeLinks` (Boolean): Include links section (default: true)

**Returns:**
- (String): Formatted table string

**Example:**
```javascript
const tableOutput = formatAsTable(responseData, {
  color: true,
  maxWidth: 80,
  includeMetadata: true,
  includeLinks: true
});
console.log(tableOutput);
```

### formatAsJson(responseData, options)

Formats response data as JSON for agent consumption.

**Parameters:**
- `responseData` (Object): The response data from Perplexity.ai
- `options` (Object): JSON formatting options
  - `pretty` (Boolean): Enable/disable pretty printing (default: true)
  - `includeRaw` (Boolean): Include raw HTML in output (default: false)

**Returns:**
- (String): JSON string

**Example:**
```javascript
const jsonOutput = formatAsJson(responseData, {
  pretty: true,
  includeRaw: false
});
console.log(jsonOutput);
```

## Response Data Structure

The expected structure of the response data object is:

```javascript
{
  content: "The main text response from Perplexity.ai",
  raw: "<div>The raw HTML response (optional)</div>",
  links: [
    { title: "Source 1", url: "https://example.com/1" },
    { title: "Source 2", url: "https://example.com/2" }
  ],
  metadata: {
    timestamp: "2025-05-04T10:45:12.819Z",
    query: "The original query",
    model: "perplexity"
  }
}
```

## Integration with CLI

The Output Formatter is integrated with the Perplexity Stealth CLI to provide both human-friendly and agent-friendly output formats:

```bash
# Human-friendly output (default)
./cli.js query "What is quantum computing?" --format=table

# Agent-friendly output
./cli.js query "What is quantum computing?" --format=json

# Agent mode (combines json format with headless operation)
./cli.js query "What is quantum computing?" --agent
```

## Examples

See the [output-formatter-usage.js](../examples/output-formatter-usage.js) file for detailed usage examples.

## Customization

The formatter can be easily customized or extended:

1. To add new table styles, modify the `styles` object in the `formatAsTable` function
2. To add new JSON fields, modify the `jsonData` object in the `formatAsJson` function
3. To support new formats, extend the `formatOutput` function with additional format options