// Command parsing and processing utilities

import { CommandParameter } from '@dexagent/shared-types';

/**
 * Parses PowerShell command output into structured data
 */
export function parseCommandOutput(output: string): {
  lines: string[];
  tables: Array<Record<string, string>>;
  errors: string[];
  warnings: string[];
} {
  if (!output || typeof output !== 'string') {
    return { lines: [], tables: [], errors: [], warnings: [] };
  }
  
  const lines = output.split(/\r?\n/).filter(line => line.trim() !== '');
  const errors: string[] = [];
  const warnings: string[] = [];
  const tables: Array<Record<string, string>> = [];
  
  // Extract errors and warnings
  lines.forEach(line => {
    const trimmedLine = line.trim();
    if (trimmedLine.toLowerCase().includes('error:') || 
        trimmedLine.toLowerCase().includes('exception:')) {
      errors.push(trimmedLine);
    } else if (trimmedLine.toLowerCase().includes('warning:')) {
      warnings.push(trimmedLine);
    }
  });
  
  // Try to parse table-like output
  const tableLines = lines.filter(line => 
    !line.toLowerCase().includes('error:') && 
    !line.toLowerCase().includes('warning:') &&
    !line.toLowerCase().includes('exception:')
  );
  
  if (tableLines.length > 1) {
    const table = parseTableOutput(tableLines);
    if (table.length > 0) {
      tables.push(...table);
    }
  }
  
  return { lines, tables, errors, warnings };
}

/**
 * Parses table-like output from PowerShell commands
 */
function parseTableOutput(lines: string[]): Array<Record<string, string>> {
  if (lines.length < 2) return [];
  
  try {
    // Look for header line (usually has spaces between columns)
    const headerLine = lines[0];
    if (!headerLine.includes(' ')) return [];
    
    // Split header by multiple spaces
    const headers = headerLine.split(/\s{2,}/).map(h => h.trim()).filter(h => h);
    if (headers.length < 2) return [];
    
    const result: Array<Record<string, string>> = [];
    
    // Process data lines
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || line.startsWith('-')) continue; // Skip separator lines
      
      const values = line.split(/\s{2,}/).map(v => v.trim());
      if (values.length === headers.length) {
        const row: Record<string, string> = {};
        headers.forEach((header, index) => {
          row[header] = values[index] || '';
        });
        result.push(row);
      }
    }
    
    return result;
  } catch {
    return [];
  }
}

/**
 * Validates a PowerShell command for safety
 */
export function validateCommand(command: string): {
  isValid: boolean;
  issues: string[];
  riskLevel: 'low' | 'medium' | 'high';
} {
  const issues: string[] = [];
  let riskLevel: 'low' | 'medium' | 'high' = 'low';
  
  if (!command || typeof command !== 'string') {
    return { isValid: false, issues: ['Command is empty or invalid'], riskLevel };
  }
  
  const lowerCommand = command.toLowerCase();
  
  // High-risk patterns
  const highRiskPatterns = [
    /format\s+[a-z]:/i,          // Format disk
    /del\s+\/s\s+\/q/i,          // Delete with force
    /rm\s+-rf/i,                 // Remove recursively
    /shutdown\s+\/s/i,           // Shutdown system
    /net\s+user.*\/add/i,        // Add user
    /reg\s+delete/i,             // Delete registry
    /taskkill\s+\/f/i,           // Force kill process
    /invoke-expression/i,        // Execute arbitrary code
    /iex\s*\(/i,                 // Short form of Invoke-Expression
    /start-process.*-verb\s+runas/i, // Run as administrator
  ];
  
  // Medium-risk patterns  
  const mediumRiskPatterns = [
    /get-wmiobject/i,           // WMI access
    /get-ciminstance/i,         // CIM access
    /new-object\s+system\.net/i, // Network objects
    /invoke-webrequest/i,       // Web requests
    /invoke-restmethod/i,       // REST calls
    /set-executionpolicy/i,     // Change execution policy
    /enable-psremoting/i,       // Enable remoting
    /new-pssession/i,          // Create PS session
  ];
  
  // Check for high-risk patterns
  for (const pattern of highRiskPatterns) {
    if (pattern.test(command)) {
      issues.push(`High-risk operation detected: ${pattern.source}`);
      riskLevel = 'high';
    }
  }
  
  // Check for medium-risk patterns (only if not already high risk)
  if (riskLevel !== 'high') {
    for (const pattern of mediumRiskPatterns) {
      if (pattern.test(command)) {
        issues.push(`Medium-risk operation detected: ${pattern.source}`);
        riskLevel = 'medium';
      }
    }
  }
  
  // Check for common issues
  if (lowerCommand.includes('password') && lowerCommand.includes('convertto-securestring')) {
    issues.push('Password handling detected - ensure secure practices');
  }
  
  if (command.includes('|') && command.split('|').length > 5) {
    issues.push('Complex pipeline detected - review for performance impact');
  }
  
  if (command.length > 1000) {
    issues.push('Command is very long - consider breaking into smaller parts');
  }
  
  return {
    isValid: issues.length === 0 || riskLevel !== 'high',
    issues,
    riskLevel
  };
}

/**
 * Sanitizes command parameters
 */
export function sanitizeCommandParameters(
  command: string,
  parameters: Record<string, unknown>
): string {
  let sanitizedCommand = command;
  
  Object.entries(parameters).forEach(([key, value]) => {
    const placeholder = `{{${key}}}`;
    const sanitizedValue = sanitizeParameterValue(value);
    sanitizedCommand = sanitizedCommand.replace(
      new RegExp(placeholder, 'g'),
      sanitizedValue
    );
  });
  
  return sanitizedCommand;
}

/**
 * Sanitizes a single parameter value
 */
function sanitizeParameterValue(value: unknown): string {
  if (value === null || value === undefined) {
    return '';
  }
  
  const stringValue = String(value);
  
  // Escape PowerShell special characters
  return stringValue
    .replace(/'/g, "''")           // Escape single quotes
    .replace(/`/g, '``')           // Escape backticks
    .replace(/\$/g, '`$')          // Escape dollar signs
    .replace(/"/g, '`"');          // Escape double quotes
}

/**
 * Validates command parameters against their definitions
 */
export function validateCommandParameters(
  parameters: Record<string, unknown>,
  parameterDefinitions: CommandParameter[]
): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check required parameters
  parameterDefinitions.forEach(param => {
    if (param.required && (parameters[param.name] === undefined || parameters[param.name] === null)) {
      errors.push(`Required parameter '${param.name}' is missing`);
    }
  });
  
  // Validate parameter types and constraints
  Object.entries(parameters).forEach(([name, value]) => {
    const definition = parameterDefinitions.find(p => p.name === name);
    if (!definition) {
      errors.push(`Unknown parameter '${name}'`);
      return;
    }
    
    // Type validation
    const typeError = validateParameterType(value, definition);
    if (typeError) {
      errors.push(`Parameter '${name}': ${typeError}`);
    }
    
    // Constraint validation
    const constraintError = validateParameterConstraints(value, definition);
    if (constraintError) {
      errors.push(`Parameter '${name}': ${constraintError}`);
    }
  });
  
  return { isValid: errors.length === 0, errors };
}

/**
 * Validates parameter type
 */
function validateParameterType(value: unknown, definition: CommandParameter): string | null {
  if (value === null || value === undefined) {
    return null; // Null values are handled by required check
  }
  
  switch (definition.type) {
    case 'string':
      if (typeof value !== 'string') {
        return `Expected string, got ${typeof value}`;
      }
      break;
    case 'number':
      if (typeof value !== 'number' || isNaN(value)) {
        return `Expected number, got ${typeof value}`;
      }
      break;
    case 'boolean':
      if (typeof value !== 'boolean') {
        return `Expected boolean, got ${typeof value}`;
      }
      break;
    case 'choice':
      if (definition.choices && !definition.choices.includes(String(value))) {
        return `Expected one of [${definition.choices.join(', ')}], got '${value}'`;
      }
      break;
  }
  
  return null;
}

/**
 * Validates parameter constraints
 */
function validateParameterConstraints(value: unknown, definition: CommandParameter): string | null {
  if (!definition.validation || value === null || value === undefined) {
    return null;
  }
  
  const { validation } = definition;
  
  if (typeof value === 'string') {
    if (validation.minLength && value.length < validation.minLength) {
      return `Minimum length is ${validation.minLength}`;
    }
    if (validation.maxLength && value.length > validation.maxLength) {
      return `Maximum length is ${validation.maxLength}`;
    }
    if (validation.pattern && !new RegExp(validation.pattern).test(value)) {
      return `Does not match required pattern`;
    }
  }
  
  if (typeof value === 'number') {
    if (validation.min && value < validation.min) {
      return `Minimum value is ${validation.min}`;
    }
    if (validation.max && value > validation.max) {
      return `Maximum value is ${validation.max}`;
    }
  }
  
  return null;
}

/**
 * Estimates command execution time based on command type
 */
export function estimateExecutionTime(command: string): number {
  const lowerCommand = command.toLowerCase();
  
  // Network operations - typically slow
  if (lowerCommand.includes('test-netconnection') || 
      lowerCommand.includes('invoke-webrequest') ||
      lowerCommand.includes('ping')) {
    return 10; // 10 seconds
  }
  
  // File system operations
  if (lowerCommand.includes('get-childitem') || 
      lowerCommand.includes('dir') ||
      lowerCommand.includes('copy-item')) {
    return 5; // 5 seconds
  }
  
  // Registry operations
  if (lowerCommand.includes('get-itemproperty') ||
      lowerCommand.includes('registry:')) {
    return 3; // 3 seconds
  }
  
  // Simple operations
  if (lowerCommand.includes('get-date') ||
      lowerCommand.includes('hostname') ||
      lowerCommand.includes('whoami')) {
    return 1; // 1 second
  }
  
  // Default estimation
  return 30; // 30 seconds
}