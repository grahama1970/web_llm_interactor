#!/usr/bin/env node

/**
 * Perplexity Stealth Agent CLI
 * A JavaScript CLI for AI agents to interact with Perplexity.ai stealth automation
 */

const fs = require('fs');
const path = require('path');
const { program } = require('commander');
const chalk = require('chalk');
const ora = require('ora');
const boxen = require('boxen');
const dotenv = require('dotenv');
const { spawn } = require('child_process');
const { formatOutput } = require('./output-formatter');

// Load environment variables
dotenv.config();

// Helper function to ensure a directory exists
function ensureDirectoryExists(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

// Set version
const packageJson = require('./package.json');
const version = packageJson.version || '1.0.0';

// Banner display function
function displayBanner() {
  const banner = boxen(
    chalk.cyan.bold('Perplexity Stealth Agent CLI') + '\n' +
    chalk.white(`v${version}`),
    {
      padding: 1,
      margin: 1,
      borderStyle: 'round',
      borderColor: 'cyan'
    }
  );
  
  console.log(banner);
}

// Execute a command and return a promise
function executeCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const childProcess = spawn(command, args, {
      stdio: options.silent ? 'pipe' : 'inherit',
      ...options
    });
    
    let stdout = '';
    let stderr = '';
    
    if (options.silent) {
      childProcess.stdout.on('data', (data) => {
        stdout += data.toString();
      });
      
      childProcess.stderr.on('data', (data) => {
        stderr += data.toString();
      });
    }
    
    childProcess.on('close', (code) => {
      if (code === 0) {
        resolve({ code, stdout, stderr });
      } else {
        reject(new Error(`Command failed with exit code ${code}: ${stderr}`));
      }
    });
    
    childProcess.on('error', (err) => {
      reject(new Error(`Failed to start command: ${err.message}`));
    });
  });
}

// Initialize CLI
program
  .name('perplexity-agent')
  .description('CLI for AI agents to interact with Perplexity.ai stealth automation')
  .version(version);

// Query command
program
  .command('query')
  .description('Send a single query to Perplexity.ai')
  .argument('<prompt>', 'Prompt to send to Perplexity.ai')
  .option('-h, --headless', 'Run in headless mode', false)
  .option('-p, --proxy <type>', 'Proxy type to use (none, custom, brightdata). For brightdata, set BRIGHT_DATA_API_KEY and BRD_CUSTOMER_ID in .env file or environment', 'none')
  .option('-c, --country <code>', 'Two-letter country code for BrightData proxy (example: US, GB, DE)')
  .option('-s, --session-id <id>', 'Session ID for BrightData proxy to maintain IP consistency')
  .option('-w, --wait-time <ms>', 'Response wait timeout in ms', '60000')
  .option('-o, --output-dir <path>', 'Directory to save responses')
  .option('-d, --debug', 'Enable debug mode', false)
  .option('-f, --format <type>', 'Output format (table, json)', 'table')
  .option('--agent', 'Enable agent mode (same as --format=json --headless)', false)
  .action(async (prompt, options) => {
    // Handle agent mode flag
    if (options.agent) {
      options.format = 'json';
      options.headless = true;
    }
    
    // Only show banner in table mode
    if (options.format !== 'json') {
      displayBanner();
    }
    
    // Prepare command arguments
    const args = ['run.js'];
    
    if (options.headless) {
      args.push('--headless');
    }
    
    if (options.proxy !== 'none') {
      args.push(`--proxy=${options.proxy}`);
      
      // Add BrightData-specific options if using BrightData
      if (options.proxy === 'brightdata') {
        if (options.country) {
          args.push(`--brd-country=${options.country}`);
        }
        if (options.sessionId) {
          args.push(`--brd-session=${options.sessionId}`);
        }
      }
    }
    
    // Create a unique output directory for response data
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const outputDir = options.outputDir || path.join('./responses', `query_${timestamp}`);
    ensureDirectoryExists(outputDir);
    args.push(`--output-dir=${outputDir}`);
    
    if (options.debug) {
      args.push('--log-level=DEBUG');
    }
    
    args.push(`--timeout=${options.waitTime}`);
    args.push(`--prompt=${prompt}`);
    args.push('--json-output=true'); // Always save metadata
    
    // Display spinner in table mode, no output in json mode
    const spinner = options.format === 'json' ? null : ora('Querying Perplexity.ai...').start();
    
    try {
      await executeCommand('node', args);
      
      if (spinner) {
        spinner.succeed('Query completed successfully');
      }
      
      // Check for response data
      const responseFile = path.join(outputDir, 'response.json');
      if (fs.existsSync(responseFile)) {
        const responseData = JSON.parse(fs.readFileSync(responseFile, 'utf8'));
        
        // Format the output based on requested format
        const formattedOutput = formatOutput(responseData, options.format, {
          color: true,
          maxWidth: process.stdout.columns || 100,
          includeMetadata: true,
          includeLinks: true
        });
        
        if (options.format === 'json') {
          // For JSON output just print the formatted JSON
          console.log(formattedOutput);
        } else {
          // For table output, add a newline before
          console.log('\n' + formattedOutput);
        }
      } else {
        // If no response data, show an error
        if (options.format === 'json') {
          console.log(JSON.stringify({
            success: false,
            error: 'No response data found',
            timestamp: new Date().toISOString(),
            query: prompt
          }));
        } else {
          console.log(chalk.yellow('No response data found. Check logs for errors.'));
        }
      }
    } catch (error) {
      if (spinner) {
        spinner.fail('Query failed');
      }
      
      if (options.format === 'json') {
        console.log(JSON.stringify({
          success: false,
          error: error.message,
          timestamp: new Date().toISOString(),
          query: prompt
        }));
      } else {
        console.error(chalk.red(`Error: ${error.message}`));
      }
      
      process.exit(1);
    }
  });

// Tasks command
program
  .command('tasks')
  .description('Execute a list of tasks defined in a JSON file')
  .argument('<tasks-file>', 'JSON file containing tasks to execute')
  .option('-h, --headless', 'Run in headless mode', true)
  .option('-p, --proxy <type>', 'Proxy type to use (none, custom, brightdata). For brightdata, set BRIGHT_DATA_API_KEY and BRD_CUSTOMER_ID in .env file or environment', 'none')
  .option('-c, --country <code>', 'Two-letter country code for BrightData proxy (example: US, GB, DE)')
  .option('-s, --session-id <id>', 'Session ID for BrightData proxy to maintain IP consistency')
  .option('-o, --output-dir <path>', 'Directory to save responses', './responses')
  .option('-f, --format <type>', 'Output format (table, json)', 'table')
  .option('--agent', 'Enable agent mode (same as --format=json --headless)', false)
  .action(async (tasksFile, options) => {
    displayBanner();
    
    // Load tasks file
    let tasks;
    try {
      const fileContent = fs.readFileSync(tasksFile, 'utf8');
      tasks = JSON.parse(fileContent);
    } catch (error) {
      console.error(chalk.red(`Error loading tasks file: ${error.message}`));
      process.exit(1);
    }
    
    if (!tasks.tasks || !Array.isArray(tasks.tasks)) {
      console.error(chalk.red('Invalid tasks file format. Expected a "tasks" array.'));
      process.exit(1);
    }
    
    // Print task list summary
    if (tasks.title) {
      console.log(chalk.bold(`Executing task list: ${tasks.title}`));
    }
    
    if (tasks.description) {
      console.log(chalk.italic(tasks.description));
    }
    
    console.log(chalk.bold(`Found ${tasks.tasks.length} tasks to execute`));
    
    // Create output directory if it doesn't exist
    if (!fs.existsSync(options.outputDir)) {
      fs.mkdirSync(options.outputDir, { recursive: true });
    }
    
    // Execute each task
    for (let i = 0; i < tasks.tasks.length; i++) {
      const task = tasks.tasks[i];
      const prompt = task.prompt;
      
      if (!prompt) {
        console.log(chalk.yellow(`Skipping task ${i+1} - No prompt specified`));
        continue;
      }
      
      const taskOutputDir = path.join(options.outputDir, `task_${i+1}`);
      if (!fs.existsSync(taskOutputDir)) {
        fs.mkdirSync(taskOutputDir, { recursive: true });
      }
      
      console.log(chalk.green.bold(`\nTask ${i+1}/${tasks.tasks.length}:`), task.title || prompt.substring(0, 50) + '...');
      
      // Prepare command arguments
      const args = ['run.js'];
      
      if (options.headless) {
        args.push('--headless');
      }
      
      if (options.proxy !== 'none') {
        args.push(`--proxy=${options.proxy}`);
        
        // Add BrightData-specific options if using BrightData
        if (options.proxy === 'brightdata') {
          if (options.country) {
            args.push(`--brd-country=${options.country}`);
          }
          if (options.sessionId) {
            args.push(`--brd-session=${options.sessionId}`);
          }
        }
      }
      
      const waitTime = task.wait_time || 60000;
      args.push(`--timeout=${waitTime}`);
      
      args.push(`--output-dir=${taskOutputDir}`);
      args.push(`--prompt=${prompt}`);
      
      // Execute the task
      const spinner = ora(`Executing task ${i+1}/${tasks.tasks.length}...`).start();
      
      try {
        await executeCommand('node', args);
        spinner.succeed(`Task ${i+1} completed`);
        
        // Save task info
        const taskInfo = {
          task_id: i+1,
          title: task.title,
          prompt: prompt,
          status: 'completed',
          timestamp: new Date().toISOString()
        };
        
        fs.writeFileSync(
          path.join(taskOutputDir, 'task_info.json'),
          JSON.stringify(taskInfo, null, 2)
        );
      } catch (error) {
        spinner.fail(`Task ${i+1} failed`);
        console.error(chalk.red(`Error: ${error.message}`));
        
        // Save failed task info
        const taskInfo = {
          task_id: i+1,
          title: task.title,
          prompt: prompt,
          status: 'failed',
          error: error.message,
          timestamp: new Date().toISOString()
        };
        
        fs.writeFileSync(
          path.join(taskOutputDir, 'task_info.json'),
          JSON.stringify(taskInfo, null, 2)
        );
      }
    }
    
    console.log(chalk.green.bold(`\nAll tasks completed. Responses saved to: ${options.outputDir}`));
  });

// Security command
program
  .command('security')
  .description('Run a security assessment on the codebase')
  .option('--full', 'Run a full security assessment', false)
  .option('--code-only', 'Only analyze code for security issues', false)
  .option('--deps-only', 'Only check dependencies for vulnerabilities', false)
  .option('-o, --output <path>', 'Path to save the security report', './security-report.md')
  .action(async (options) => {
    displayBanner();
    
    console.log(chalk.bold('Running security assessment...'));
    
    // Prepare command arguments
    const args = ['security-eval.js', '--yes']; // Skip confirmation prompt
    
    if (options.full) {
      args.push('--full');
    } else if (options.codeOnly) {
      args.push('--analyze-code');
    } else if (options.depsOnly) {
      args.push('--check-deps');
    } else {
      // Default to full if no specific option is provided
      args.push('--full');
    }
    
    args.push(`--output=${options.output}`);
    
    // Run security evaluation
    const spinner = ora('Analyzing security...').start();
    
    try {
      await executeCommand('node', args);
      spinner.succeed('Security assessment completed');
      
      if (fs.existsSync(options.output)) {
        console.log(chalk.green(`Security report generated: ${options.output}`));
      } else {
        console.log(chalk.yellow('Security report could not be found at the expected location'));
      }
    } catch (error) {
      spinner.fail('Security assessment failed');
      console.error(chalk.red(`Error: ${error.message}`));
      process.exit(1);
    }
  });

// Create tasks file command
program
  .command('create-tasks')
  .description('Create a template task list file')
  .argument('[output-file]', 'Output file path', './tasks.json')
  .action((outputFile) => {
    displayBanner();
    
    const template = {
      "title": "Example Agent Task Workflow",
      "description": "A sequence of tasks demonstrating agent interaction with Perplexity.ai",
      "tasks": [
        {
          "title": "Basic Information Query",
          "prompt": "What is quantum computing and how does it differ from classical computing? Provide a concise explanation.",
          "wait_time": 60000
        },
        {
          "title": "Code Example Request",
          "prompt": "Show me a Python implementation of the quicksort algorithm with detailed comments explaining how it works.",
          "wait_time": 60000
        },
        {
          "title": "Desktop Commander File Access",
          "prompt": "Use the local MCP tool desktop-commander to read the file located at ~/Documents/readme.txt. Return the file's contents. Then summarize the key points in bullet form.",
          "wait_time": 120000
        },
        {
          "title": "Complex Research Query",
          "prompt": "Research the current state of nuclear fusion energy. What are the most promising approaches? What challenges remain? When might commercial fusion power become a reality?",
          "wait_time": 120000
        },
        {
          "title": "Follow-up Question",
          "prompt": "Based on what we know about fusion power challenges, what alternative clean energy technologies might serve as bridge solutions until fusion becomes commercially viable?",
          "wait_time": 90000
        }
      ]
    };
    
    try {
      fs.writeFileSync(outputFile, JSON.stringify(template, null, 2));
      console.log(chalk.green(`Task template created: ${outputFile}`));
      console.log('Edit this file to define your own sequence of tasks.');
    } catch (error) {
      console.error(chalk.red(`Error creating template: ${error.message}`));
      process.exit(1);
    }
  });

// Ensure dependencies are installed
program
  .command('setup')
  .description('Ensure all required dependencies are installed')
  .action(async () => {
    displayBanner();
    
    const spinner = ora('Checking dependencies...').start();
    
    try {
      // Check if node_modules exists
      if (!fs.existsSync('./node_modules')) {
        spinner.text = 'Installing dependencies...';
        await executeCommand('npm', ['install'], { silent: true });
      }
      
      spinner.succeed('Dependencies are installed');
    } catch (error) {
      spinner.fail('Failed to install dependencies');
      console.error(chalk.red(`Error: ${error.message}`));
      process.exit(1);
    }
  });

// Parse command line arguments
program.parse();

// If no arguments are passed, display help
if (!process.argv.slice(2).length) {
  displayBanner();
  program.help();
}