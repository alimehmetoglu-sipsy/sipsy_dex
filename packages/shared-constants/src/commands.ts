// Command-related constants

import { CommandCategory, CommandType } from '@dexagent/shared-types';

// Command categories
export const COMMAND_CATEGORIES = {
  SYSTEM: 'system' as CommandCategory,
  NETWORK: 'network' as CommandCategory,
  SECURITY: 'security' as CommandCategory,
  MONITORING: 'monitoring' as CommandCategory,
  MAINTENANCE: 'maintenance' as CommandCategory,
  TROUBLESHOOTING: 'troubleshooting' as CommandCategory,
  CUSTOM: 'custom' as CommandCategory
} as const;

// Command types
export const COMMAND_TYPES = {
  POWERSHELL: 'powershell' as CommandType,
  CMD: 'cmd' as CommandType,
  BASH: 'bash' as CommandType,
  PYTHON: 'python' as CommandType,
  CUSTOM: 'custom' as CommandType
} as const;

// Default commands by category
export const DEFAULT_COMMANDS = {
  [COMMAND_CATEGORIES.SYSTEM]: [
    {
      name: 'Get System Information',
      command: 'Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors',
      description: 'Retrieve basic system information'
    },
    {
      name: 'Get Disk Usage',
      command: 'Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace, @{Name="PercentFree";Expression={[math]::Round(($_.FreeSpace/$_.Size)*100,2)}}',
      description: 'Check disk usage for all drives'
    },
    {
      name: 'Get Running Processes',
      command: 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, ID, CPU, WorkingSet',
      description: 'List top 10 processes by CPU usage'
    },
    {
      name: 'Get System Uptime',
      command: '(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime',
      description: 'Get system uptime'
    }
  ],
  
  [COMMAND_CATEGORIES.NETWORK]: [
    {
      name: 'Test Network Connectivity',
      command: 'Test-NetConnection -ComputerName google.com -Port 80',
      description: 'Test internet connectivity'
    },
    {
      name: 'Get Network Adapters',
      command: 'Get-NetAdapter | Where-Object {$_.Status -eq "Up"} | Select-Object Name, InterfaceDescription, LinkSpeed',
      description: 'List active network adapters'
    },
    {
      name: 'Get IP Configuration',
      command: 'Get-NetIPConfiguration | Where-Object {$_.IPv4Address -ne $null}',
      description: 'Get IP configuration for all interfaces'
    },
    {
      name: 'DNS Lookup',
      command: 'Resolve-DnsName -Name {{hostname}} -Type A',
      description: 'Perform DNS lookup for a hostname'
    }
  ],
  
  [COMMAND_CATEGORIES.SECURITY]: [
    {
      name: 'Get Windows Defender Status',
      command: 'Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, OnAccessProtectionEnabled',
      description: 'Check Windows Defender status'
    },
    {
      name: 'Get Firewall Rules',
      command: 'Get-NetFirewallRule | Where-Object {$_.Enabled -eq "True"} | Select-Object DisplayName, Direction, Action | Sort-Object DisplayName',
      description: 'List enabled firewall rules'
    },
    {
      name: 'Get Failed Login Attempts',
      command: 'Get-WinEvent -FilterHashtable @{LogName="Security"; ID=4625} -MaxEvents 10 | Select-Object TimeCreated, @{Name="Account";Expression={$_.Properties[5].Value}}',
      description: 'Get recent failed login attempts'
    }
  ],
  
  [COMMAND_CATEGORIES.MONITORING]: [
    {
      name: 'Get CPU Usage',
      command: 'Get-Counter "\\Processor(_Total)\\% Processor Time" | Select-Object -ExpandProperty CounterSamples | Select-Object CookedValue',
      description: 'Get current CPU usage'
    },
    {
      name: 'Get Memory Usage',
      command: 'Get-CimInstance Win32_OperatingSystem | Select-Object @{Name="MemoryUsage";Expression={[math]::Round((($_.TotalVisibleMemorySize - $_.FreePhysicalMemory) / $_.TotalVisibleMemorySize) * 100, 2)}}',
      description: 'Get memory usage percentage'
    },
    {
      name: 'Get Event Log Errors',
      command: 'Get-WinEvent -FilterHashtable @{LogName="System"; Level=2} -MaxEvents 5 | Select-Object TimeCreated, Id, LevelDisplayName, Message',
      description: 'Get recent system errors from event log'
    }
  ],
  
  [COMMAND_CATEGORIES.MAINTENANCE]: [
    {
      name: 'Clean Temporary Files',
      command: 'Get-ChildItem -Path $env:TEMP -Recurse | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-7)} | Remove-Item -Force -Recurse -ErrorAction SilentlyContinue',
      description: 'Clean temporary files older than 7 days'
    },
    {
      name: 'Check Disk Health',
      command: 'Get-PhysicalDisk | Get-StorageReliabilityCounter | Select-Object DeviceId, Temperature, PowerOnHours, ReadErrorsTotal, WriteErrorsTotal',
      description: 'Check physical disk health'
    },
    {
      name: 'Get Windows Updates',
      command: 'Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10 HotFixID, Description, InstalledOn',
      description: 'List recent Windows updates'
    }
  ],
  
  [COMMAND_CATEGORIES.TROUBLESHOOTING]: [
    {
      name: 'System File Check',
      command: 'sfc /scannow',
      description: 'Run system file checker'
    },
    {
      name: 'Check Memory',
      command: 'mdsched.exe',
      description: 'Schedule memory diagnostic'
    },
    {
      name: 'Network Diagnostics',
      command: 'netsh winsock reset; netsh int ip reset; ipconfig /flushdns',
      description: 'Reset network configuration'
    }
  ]
} as const;

// Command execution limits
export const COMMAND_LIMITS = {
  MIN_TIMEOUT: 1, // seconds
  MAX_TIMEOUT: 3600, // 1 hour
  DEFAULT_TIMEOUT: 30, // seconds
  MAX_COMMAND_LENGTH: 5000, // characters
  MAX_PARAMETER_COUNT: 20,
  MAX_PARAMETER_VALUE_LENGTH: 1000
} as const;

// Command validation patterns
export const COMMAND_VALIDATION = {
  // High-risk command patterns
  HIGH_RISK_PATTERNS: [
    /format\s+[a-z]:/i,
    /del\s+\/s\s+\/q/i,
    /rm\s+-rf/i,
    /shutdown\s+\/s/i,
    /net\s+user.*\/add/i,
    /reg\s+delete/i,
    /taskkill\s+\/f/i,
    /invoke-expression/i,
    /iex\s*\(/i,
    /start-process.*-verb\s+runas/i
  ],
  
  // Medium-risk command patterns
  MEDIUM_RISK_PATTERNS: [
    /get-wmiobject/i,
    /get-ciminstance/i,
    /new-object\s+system\.net/i,
    /invoke-webrequest/i,
    /invoke-restmethod/i,
    /set-executionpolicy/i,
    /enable-psremoting/i,
    /new-pssession/i
  ],
  
  // Forbidden commands
  FORBIDDEN_COMMANDS: [
    'format c:',
    'del /s /q c:\\',
    'rm -rf /',
    'shutdown /s /t 0'
  ]
} as const;

// Command parameter types
export const PARAMETER_TYPES = {
  STRING: 'string',
  NUMBER: 'number',
  BOOLEAN: 'boolean',
  CHOICE: 'choice'
} as const;

// Command execution status priorities
export const STATUS_PRIORITIES = {
  'failed': 1,
  'timeout': 2,
  'cancelled': 3,
  'running': 4,
  'pending': 5,
  'completed': 6
} as const;

// Command templates
export const COMMAND_TEMPLATES = {
  BASIC_INFO: {
    name: 'Basic System Information',
    command: 'Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory, CsProcessors',
    category: COMMAND_CATEGORIES.SYSTEM,
    timeout: 30
  },
  PROCESS_LIST: {
    name: 'Process List',
    command: 'Get-Process | Sort-Object CPU -Descending | Select-Object Name, Id, CPU, WorkingSet',
    category: COMMAND_CATEGORIES.SYSTEM,
    timeout: 15
  },
  DISK_SPACE: {
    name: 'Disk Space Check',
    command: 'Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace',
    category: COMMAND_CATEGORIES.SYSTEM,
    timeout: 10
  }
} as const;