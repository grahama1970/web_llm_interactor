/**
 * Security evaluation module for Perplexity.ai stealth automation
 * Inspired by the Hacker agent methodology for identifying security issues
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// OWASP Top 10 categories for reference
const OWASP_CATEGORIES = {
  A1: 'Broken Access Control',
  A2: 'Cryptographic Failures',
  A3: 'Injection',
  A4: 'Insecure Design',
  A5: 'Security Misconfiguration',
  A6: 'Vulnerable Components',
  A7: 'Identification and Authentication Failures',
  A8: 'Software and Data Integrity Failures',
  A9: 'Security Logging and Monitoring Failures',
  A10: 'Server-Side Request Forgery (SSRF)'
};

/**
 * Performs a security analysis of the codebase
 * @param {Object} options - Analysis options
 * @param {boolean} options.checkDependencies - Whether to check for vulnerable dependencies
 * @param {boolean} options.analyzeCode - Whether to analyze code for vulnerabilities
 * @param {boolean} options.testExploits - Whether to attempt test exploits in sandbox
 * @param {string} options.outputPath - Path to save security report
 * @returns {Object} Security analysis results
 */
async function analyzeSecurity(options = {}) {
  const defaultOptions = {
    checkDependencies: true,
    analyzeCode: true,
    testExploits: false, // Disabled by default for safety
    outputPath: './security-report.json'
  };
  
  const config = { ...defaultOptions, ...options };
  const results = {
    timestamp: new Date().toISOString(),
    summary: {
      vulnerabilities: [],
      securityIssues: [],
      recommendations: []
    },
    details: {
      dependencies: null,
      codeAnalysis: null,
      exploitTests: null
    }
  };
  
  // Check dependencies if enabled
  if (config.checkDependencies) {
    results.details.dependencies = checkDependencies();
    
    // Add findings to summary
    if (results.details.dependencies.vulnerablePackages.length > 0) {
      results.summary.vulnerabilities.push({
        type: 'Vulnerable Dependencies',
        count: results.details.dependencies.vulnerablePackages.length,
        severity: 'HIGH',
        category: OWASP_CATEGORIES.A6
      });
      
      results.summary.recommendations.push(
        'Update all packages with known vulnerabilities',
        'Implement a dependency scanning tool in your CI pipeline'
      );
    }
  }
  
  // Analyze code if enabled
  if (config.analyzeCode) {
    results.details.codeAnalysis = analyzeCodeSecurity();
    
    // Add findings to summary
    results.details.codeAnalysis.issues.forEach(issue => {
      results.summary.securityIssues.push({
        type: issue.type,
        location: issue.location,
        severity: issue.severity,
        category: issue.category
      });
    });
    
    // Add unique recommendations
    const uniqueRecommendations = new Set([
      ...results.summary.recommendations,
      ...results.details.codeAnalysis.recommendations
    ]);
    results.summary.recommendations = [...uniqueRecommendations];
  }
  
  // Test exploits if enabled (be careful with this)
  if (config.testExploits) {
    results.details.exploitTests = await testExploits();
    
    // Add successful exploits to vulnerabilities
    results.details.exploitTests.successfulExploits.forEach(exploit => {
      results.summary.vulnerabilities.push({
        type: 'Successful Exploit',
        details: exploit.name,
        severity: 'CRITICAL',
        category: exploit.category
      });
    });
  }
  
  // Save report if path is provided
  if (config.outputPath) {
    fs.writeFileSync(
      config.outputPath, 
      JSON.stringify(results, null, 2)
    );
  }
  
  return results;
}

/**
 * Checks dependencies for known vulnerabilities
 * @returns {Object} Dependency analysis results
 */
function checkDependencies() {
  const results = {
    totalPackages: 0,
    vulnerablePackages: [],
    recommendations: []
  };
  
  try {
    // Check if package.json exists
    const packageJsonPath = path.resolve(process.cwd(), 'package.json');
    if (!fs.existsSync(packageJsonPath)) {
      return {
        error: 'package.json not found',
        vulnerablePackages: [],
        recommendations: ['Create a package.json file to track dependencies']
      };
    }
    
    // Read package.json
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    const dependencies = {
      ...(packageJson.dependencies || {}),
      ...(packageJson.devDependencies || {})
    };
    
    results.totalPackages = Object.keys(dependencies).length;
    
    // Check for known vulnerable packages and outdated versions
    // Note: Normally you'd use npm audit or another security scanning tool here
    const knownVulnerablePackageVersions = {
      'playwright': {
        vulnerableVersions: ['<1.30.0'],
        description: 'Earlier versions have known security issues'
      },
      'puppeteer-extra-plugin-stealth': {
        vulnerableVersions: ['<2.8.0'],
        description: 'Earlier versions may have fingerprinting issues'
      }
    };
    
    // Check each dependency
    for (const [name, version] of Object.entries(dependencies)) {
      if (knownVulnerablePackageVersions[name]) {
        const info = knownVulnerablePackageVersions[name];
        const cleanVersion = version.replace(/[^\d.]/g, '');
        
        // Simple version check (in a real tool, use semver)
        for (const vulnVersion of info.vulnerableVersions) {
          if (vulnVersion.startsWith('<') && cleanVersion < vulnVersion.slice(1)) {
            results.vulnerablePackages.push({
              name,
              version,
              vulnerability: info.description
            });
            break;
          }
        }
      }
    }
    
    // Add recommendations based on findings
    if (results.vulnerablePackages.length > 0) {
      results.recommendations.push('Run npm audit to check for vulnerabilities');
      results.recommendations.push('Update vulnerable packages to their latest versions');
    }
    
    // Check if there's a package lock file
    if (!fs.existsSync(path.resolve(process.cwd(), 'package-lock.json'))) {
      results.recommendations.push('Create a package-lock.json file to lock dependency versions');
    }
    
  } catch (error) {
    results.error = `Error analyzing dependencies: ${error.message}`;
  }
  
  return results;
}

/**
 * Analyzes code for security issues
 * @returns {Object} Code analysis results
 */
function analyzeCodeSecurity() {
  const results = {
    filesAnalyzed: 0,
    issues: [],
    recommendations: []
  };
  
  // Security patterns to check for
  const securityPatterns = [
    {
      pattern: /eval\s*\(/g,
      type: 'Code Injection Risk',
      severity: 'HIGH',
      category: OWASP_CATEGORIES.A3,
      recommendation: 'Avoid using eval() as it can execute arbitrary code'
    },
    {
      pattern: /Object\.defineProperty\s*\(\s*navigator/g,
      type: 'Browser Fingerprinting Modification',
      severity: 'MEDIUM',
      category: OWASP_CATEGORIES.A4,
      recommendation: 'Be cautious when modifying browser properties for fingerprinting'
    },
    {
      pattern: /password.*=.*['"][^'"]*['"]|apiKey.*=.*['"][^'"]*['"]|token.*=.*['"][^'"]*['"]|secret.*=.*['"][^'"]*['"]|key.*=.*['"][^'"]*['"]|auth.*=.*['"][^'"]*['"]|credential.*=.*['"][^'"]*['"]|pass.*=.*['"][^'"]*['"]|api_key.*=.*['"][^'"]*['"]|BRIGHT_DATA_API_KEY/gi,
      type: 'Hardcoded Credentials',
      severity: 'HIGH',
      category: OWASP_CATEGORIES.A2,
      recommendation: 'Never hardcode credentials in source code. Use environment variables instead.'
    },
    {
      pattern: /https?:\/\/[^\s/$.?#].[^\s]*['"]|url:.*['"]http/gi,
      type: 'Potential Insecure URL',
      severity: 'MEDIUM',
      category: OWASP_CATEGORIES.A2,
      recommendation: 'Ensure all URLs use HTTPS and validate URLs before use'
    },
    {
      pattern: /\.innerHTML\s*=|document\.write\s*\(/g,
      type: 'Potential XSS',
      severity: 'MEDIUM',
      category: OWASP_CATEGORIES.A3,
      recommendation: 'Avoid using innerHTML or document.write with untrusted content'
    }
  ];
  
  // Specific security concerns for this application
  const specificConcerns = [
    {
      pattern: /await page\.addInitScript\s*\(/g,
      type: 'Page Script Injection',
      severity: 'MEDIUM',
      category: OWASP_CATEGORIES.A3,
      recommendation: 'Be cautious with page.addInitScript as it runs in the browser context'
    },
    {
      pattern: /console\.log\s*\([^)]*config/g,
      type: 'Sensitive Information Logging',
      severity: 'LOW',
      category: OWASP_CATEGORIES.A9,
      recommendation: 'Avoid logging configuration details that might contain sensitive information'
    }
  ];
  
  // Combine all patterns
  const allPatterns = [...securityPatterns, ...specificConcerns];
  
  try {
    // Get all JavaScript files in the project
    const srcDir = path.resolve(process.cwd(), 'src');
    const jsFiles = getJsFiles(srcDir);
    
    results.filesAnalyzed = jsFiles.length;
    
    // Analyze each file
    jsFiles.forEach(file => {
      const content = fs.readFileSync(file, 'utf8');
      const relativePath = path.relative(process.cwd(), file);
      
      // Check for each pattern
      allPatterns.forEach(({ pattern, type, severity, category, recommendation }) => {
        const matches = content.match(pattern);
        
        if (matches) {
          results.issues.push({
            file: relativePath,
            type,
            severity,
            category,
            matchCount: matches.length,
            location: `${relativePath}`
          });
          
          if (!results.recommendations.includes(recommendation)) {
            results.recommendations.push(recommendation);
          }
        }
      });
    });
    
    // Add general security recommendations for this type of application
    results.recommendations.push(
      'Implement rate limiting to prevent abuse',
      'Consider adding user-agent rotation if not already implemented',
      'Consider using a secure proxy solution',
      'Add CAPTCHA handling capabilities',
      'Add secure credential storage'
    );
    
  } catch (error) {
    results.error = `Error analyzing code: ${error.message}`;
  }
  
  return results;
}

/**
 * Recursively gets all JavaScript files in a directory
 * @param {string} dir - Directory to search
 * @returns {Array<string>} Array of file paths
 */
function getJsFiles(dir) {
  let results = [];
  
  if (!fs.existsSync(dir)) {
    return results;
  }
  
  const list = fs.readdirSync(dir);
  
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    
    if (stat && stat.isDirectory()) {
      // Recursive call for directories
      results = results.concat(getJsFiles(filePath));
    } else if (file.endsWith('.js')) {
      // Add JavaScript files
      results.push(filePath);
    }
  });
  
  return results;
}

/**
 * Tests for exploits in a sandbox environment
 * @returns {Promise<Object>} Exploit test results
 */
async function testExploits() {
  const results = {
    testsRun: 0,
    successfulExploits: [],
    failedExploits: []
  };
  
  // This function would normally conduct actual exploit tests
  // For safety, we're just returning a dummy result
  results.testsRun = 0;
  results.note = 'Exploit testing is disabled for safety. This function would normally run tests in a sandbox.';
  
  return results;
}

/**
 * Generates a security report for the project
 * @param {string} outputPath - Path to save the report
 * @returns {Promise<string>} Path to the report file
 */
async function generateSecurityReport(outputPath = './security-report.md') {
  // Run the security analysis
  const analysis = await analyzeSecurity({ outputPath: outputPath.replace('.md', '.json') });
  
  // Generate a markdown report
  let report = `# Security Analysis Report\n\n`;
  report += `Generated: ${new Date().toISOString()}\n\n`;
  
  // Add summary
  report += `## Summary\n\n`;
  
  if (analysis.summary.vulnerabilities.length === 0 && analysis.summary.securityIssues.length === 0) {
    report += `✅ No security issues detected\n\n`;
  } else {
    report += `⚠️ Found ${analysis.summary.vulnerabilities.length} vulnerabilities and ${analysis.summary.securityIssues.length} security issues\n\n`;
  }
  
  // Add vulnerabilities section if there are any
  if (analysis.summary.vulnerabilities.length > 0) {
    report += `## Vulnerabilities\n\n`;
    
    analysis.summary.vulnerabilities.forEach(vuln => {
      report += `### ${vuln.type}\n\n`;
      report += `- **Severity**: ${vuln.severity}\n`;
      report += `- **Category**: ${vuln.category}\n`;
      if (vuln.details) {
        report += `- **Details**: ${vuln.details}\n`;
      }
      report += '\n';
    });
  }
  
  // Add security issues section if there are any
  if (analysis.summary.securityIssues.length > 0) {
    report += `## Security Issues\n\n`;
    
    analysis.summary.securityIssues.forEach(issue => {
      report += `### ${issue.type}\n\n`;
      report += `- **Location**: ${issue.location}\n`;
      report += `- **Severity**: ${issue.severity}\n`;
      report += `- **Category**: ${issue.category}\n`;
      report += '\n';
    });
  }
  
  // Add recommendations
  report += `## Recommendations\n\n`;
  
  if (analysis.summary.recommendations.length > 0) {
    analysis.summary.recommendations.forEach(rec => {
      report += `- ${rec}\n`;
    });
  } else {
    report += `No specific recommendations\n`;
  }
  
  // Add detailed results
  report += `\n## Detailed Results\n\n`;
  
  if (analysis.details.dependencies) {
    report += `### Dependency Analysis\n\n`;
    report += `- Total packages: ${analysis.details.dependencies.totalPackages}\n`;
    report += `- Vulnerable packages: ${analysis.details.dependencies.vulnerablePackages.length}\n\n`;
    
    if (analysis.details.dependencies.vulnerablePackages.length > 0) {
      report += `#### Vulnerable Packages\n\n`;
      
      analysis.details.dependencies.vulnerablePackages.forEach(pkg => {
        report += `- **${pkg.name}@${pkg.version}**: ${pkg.vulnerability}\n`;
      });
      
      report += '\n';
    }
  }
  
  if (analysis.details.codeAnalysis) {
    report += `### Code Analysis\n\n`;
    report += `- Files analyzed: ${analysis.details.codeAnalysis.filesAnalyzed}\n`;
    report += `- Issues found: ${analysis.details.codeAnalysis.issues.length}\n\n`;
    
    if (analysis.details.codeAnalysis.issues.length > 0) {
      report += `#### Issues\n\n`;
      
      analysis.details.codeAnalysis.issues.forEach(issue => {
        report += `- **${issue.type}** in ${issue.file} (${issue.severity})\n`;
      });
      
      report += '\n';
    }
  }
  
  // Save the report
  fs.writeFileSync(outputPath, report);
  
  return outputPath;
}

module.exports = {
  analyzeSecurity,
  checkDependencies,
  analyzeCodeSecurity,
  testExploits,
  generateSecurityReport,
  OWASP_CATEGORIES
};