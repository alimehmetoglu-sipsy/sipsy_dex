# DexAgents Administrator Guide

## 📚 Table of Contents

1. [Overview](#overview)
2. [Deployment Planning](#deployment-planning)
3. [Installation Methods](#installation-methods)
4. [Configuration Management](#configuration-management)
5. [Service Deployment](#service-deployment)
6. [Security Configuration](#security-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Best Practices](#best-practices)
10. [Appendix](#appendix)

## 🎯 Overview

This guide provides comprehensive information for system administrators deploying and managing DexAgents Windows Agent across enterprise environments.

### Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   DexAgents     │    │    Network       │    │   Client        │
│   Server        │◄──►│   (WebSocket)    │◄──►│   Agent         │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                                              │
         │              ┌──────────────────┐           │
         └─────────────►│   Web Dashboard  │◄──────────┘
                        │                  │
                        └──────────────────┘
```

### Key Components

- **DexAgents Server**: Central management and monitoring server
- **Windows Agent**: Client-side monitoring and management agent
- **Web Dashboard**: Browser-based management interface
- **API**: RESTful API for integration and automation

## 📋 Deployment Planning

### Environment Assessment

#### Network Requirements
- **Bandwidth**: Minimum 1 Mbps per 100 agents
- **Latency**: <100ms recommended for optimal performance
- **Ports**: 
  - HTTP/HTTPS: 80/443 (configurable)
  - WebSocket: Same as HTTP ports
  - Custom: 8080/8443 (default)

#### System Requirements

**DexAgents Server**:
- OS: Linux/Windows Server
- CPU: 4+ cores
- RAM: 8GB+ (2GB per 1000 agents)
- Storage: 100GB+ for logs and data

**Windows Agents**:
- OS: Windows 10/11, Server 2019/2022
- CPU: Minimal impact (<5%)
- RAM: 50-100MB per agent
- Storage: 100MB + log files

### Deployment Scenarios

#### Small Office (1-50 computers)
```
Deployment: Manual installation
Service Mode: User-mode auto-start
Management: Direct GUI configuration
Monitoring: Web dashboard
```

#### Medium Enterprise (50-500 computers)
```
Deployment: Group Policy or SCCM
Service Mode: Windows Service
Management: Centralized configuration
Monitoring: Automated alerting
```

#### Large Enterprise (500+ computers)
```
Deployment: Automated deployment tools
Service Mode: System service with monitoring
Management: Configuration management tools
Monitoring: SIEM integration
```

### Capacity Planning

#### Server Sizing
```
Agent Count  | CPU Cores | RAM (GB) | Storage (GB) | Network (Mbps)
1-100       | 2         | 4        | 50          | 10
100-500     | 4         | 8        | 200         | 25
500-1000    | 8         | 16       | 500         | 50
1000+       | 16+       | 32+      | 1000+       | 100+
```

## 🚀 Installation Methods

### Method 1: Interactive Installer

Best for: Small deployments, initial testing

```batch
# Download installer
curl -O https://server/downloads/DexAgentsInstaller.exe

# Run with parameters
DexAgentsInstaller.exe /S /SERVER=https://server:8080 /TOKEN=api-token
```

**Parameters**:
- `/S` - Silent installation
- `/SERVER=url` - Server URL
- `/TOKEN=token` - API token
- `/INSTALLDIR=path` - Installation path
- `/AUTOSTART=1` - Enable auto-start
- `/SERVICE=1` - Install as service

### Method 2: Group Policy Deployment

Best for: Domain environments

#### Create GPO
1. **Open** Group Policy Management Console
2. **Create** new GPO: "DexAgents Deployment" 
3. **Edit** GPO settings

#### Software Installation
```
Computer Configuration
├── Policies  
    ├── Software Settings
        ├── Software Installation
            ├── New → Package
                ├── Package: DexAgentsInstaller.msi
                ├── Deployment: Assigned
                └── Installation: Basic
```

#### Registry Settings
```
Computer Configuration
├── Preferences
    ├── Windows Settings
        ├── Registry
            ├── HKLM\SOFTWARE\DexAgents
                ├── ServerURL (String): https://server:8080
                ├── ApiToken (String): your-api-token
                └── AutoStart (DWORD): 1
```

### Method 3: SCCM Deployment

Best for: Large enterprise environments

#### Create Application
```powershell
# SCCM PowerShell commands
New-CMApplication -Name "DexAgents Windows Agent" -Description "System monitoring agent"

# Add deployment type
Add-CMDeploymentType -ApplicationName "DexAgents Windows Agent" `
    -MsiInstaller -ContentLocation "\\server\share\DexAgents\" `
    -InstallationProgram "DexAgentsInstaller.exe /S /SERVER=https://server:8080 /TOKEN=token"
```

#### Deploy to Collections
```powershell
# Create device collection
New-CMDeviceCollection -Name "DexAgents Deployment" -LimitingCollectionName "All Systems"

# Deploy application
Start-CMApplicationDeployment -ApplicationName "DexAgents Windows Agent" `
    -CollectionName "DexAgents Deployment" -DeployAction Install -UserNotification DisplaySoftwareCenterOnly
```

### Method 4: PowerShell DSC

Best for: Infrastructure as Code environments

```powershell
Configuration DexAgentsDeployment {
    param(
        [string]$ServerURL = "https://server:8080",
        [string]$ApiToken = "your-token"
    )
    
    Node localhost {
        # Download installer
        Script DownloadInstaller {
            SetScript = {
                Invoke-WebRequest -Uri "$using:ServerURL/downloads/DexAgentsInstaller.exe" `
                    -OutFile "C:\temp\DexAgentsInstaller.exe"
            }
            TestScript = { Test-Path "C:\temp\DexAgentsInstaller.exe" }
            GetScript = { @{ Result = "Downloaded" } }
        }
        
        # Install DexAgents
        Package DexAgents {
            Name = "DexAgents Windows Agent"
            Path = "C:\temp\DexAgentsInstaller.exe"
            Arguments = "/S /SERVER=$ServerURL /TOKEN=$ApiToken /SERVICE=1"
            ProductId = ""
            DependsOn = "[Script]DownloadInstaller"
        }
        
        # Configure service
        Service DexAgentsService {
            Name = "DexAgentsService"
            State = "Running"
            StartupType = "Automatic"
            DependsOn = "[Package]DexAgents"
        }
    }
}
```

### Method 5: Intune Deployment

Best for: Modern device management

#### Create Win32 App
```powershell
# Prepare package
New-IntuneWin32AppPackage -SourceFolder "C:\DexAgents" -SetupFile "install.bat" -OutputFolder "C:\Output"

# Upload to Intune
Add-IntuneWin32App -FilePath "C:\Output\install.intunewin" `
    -DisplayName "DexAgents Windows Agent" `
    -Description "System monitoring and management agent" `
    -InstallCommandLine "install.bat" `
    -UninstallCommandLine "uninstall.bat"
```

## ⚙️ Configuration Management

### Centralized Configuration

#### Configuration Server
```json
{
  "default_config": {
    "server_url": "https://dexagents.company.com:8080",
    "update_interval": 30,
    "log_level": "INFO",
    "auto_start": true,
    "run_as_service": true
  },
  "environment_configs": {
    "production": {
      "tags": ["production", "monitored"],
      "heartbeat_interval": 30,
      "enable_debug_mode": false
    },
    "development": {
      "tags": ["development", "testing"], 
      "heartbeat_interval": 60,
      "enable_debug_mode": true
    }
  }
}
```

#### Configuration Distribution
```powershell
# PowerShell script for config distribution
param(
    [string]$ConfigServer = "https://config.company.com",
    [string]$Environment = "production"
)

# Download configuration
$config = Invoke-RestMethod -Uri "$ConfigServer/api/config/$Environment"

# Apply to local agent
$configPath = "C:\ProgramData\DexAgents\config.json"
$config | ConvertTo-Json -Depth 10 | Set-Content -Path $configPath

# Restart agent to apply changes
Restart-Service -Name "DexAgentsService" -Force
```

### Group Policy Templates

#### Administrative Templates (ADMX)
```xml
<?xml version="1.0" encoding="utf-8"?>
<policyDefinitions xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                   revision="1.0" schemaVersion="1.0">
  <policyNamespaces>
    <target prefix="dexagents" namespace="Company.DexAgents.Policies" />
  </policyNamespaces>
  
  <resources minRequiredRevision="1.0" />
  
  <categories>
    <category name="DexAgents" displayName="$(string.DexAgents)">
      <parentCategory ref="windows:System" />
    </category>
  </categories>
  
  <policies>
    <policy name="ServerURL" class="Machine" displayName="$(string.ServerURL)" 
            explainText="$(string.ServerURL_Explain)" key="SOFTWARE\DexAgents">
      <parentCategory ref="DexAgents" />
      <supportedOn ref="windows:SUPPORTED_WindowsVista" />
      <elements>
        <text id="ServerURL_Value" valueName="ServerURL" />
      </elements>
    </policy>
  </policies>
</policyDefinitions>
```

### Registry Configuration

#### System-wide Settings
```reg
Windows Registry Editor Version 5.00

[HKEY_LOCAL_MACHINE\SOFTWARE\DexAgents]
"ServerURL"="https://dexagents.company.com:8080"
"AutoStart"=dword:00000001
"RunAsService"=dword:00000001
"LogLevel"="INFO"
"UpdateInterval"=dword:0000001e
"Tags"="production,monitored,enterprise"

[HKEY_LOCAL_MACHINE\SOFTWARE\DexAgents\Network]
"ConnectionTimeout"=dword:0000001e
"MaxRetries"=dword:00000003
"UseProxy"=dword:00000000

[HKEY_LOCAL_MACHINE\SOFTWARE\DexAgents\Security]
"VerifySSL"=dword:00000001
"EnableDebugMode"=dword:00000000
```

## 🔧 Service Deployment

### Windows Service Installation

#### Service Configuration
```xml
<!-- service-config.xml -->
<service>
  <id>DexAgentsService</id>
  <name>DexAgents Service</name>
  <description>DexAgents Windows Management Service</description>
  <executable>DexAgentsService.exe</executable>
  <arguments>--config "C:\ProgramData\DexAgents\config.json"</arguments>
  <logpath>C:\ProgramData\DexAgents\logs</logpath>
  <logmode>rotate</logmode>
  <depend>Tcpip</depend>
  <depend>Dnscache</depend>
  <startmode>Automatic</startmode>
  <delayedAutoStart>true</delayedAutoStart>
  <recovery>
    <resetfailure>1 day</resetfailure>
    <action delay="10 sec">restart</action>
    <action delay="20 sec">restart</action>
    <action delay="60 sec">none</action>
  </recovery>
</service>
```

#### Service Installation Script
```batch
@echo off
REM DexAgents Service Installation Script

echo Installing DexAgents Windows Service...

REM Create service
sc create DexAgentsService binPath= "C:\Program Files\DexAgents\DexAgentsService.exe" ^
    DisplayName= "DexAgents Service" ^
    description= "DexAgents Windows Management Service" ^
    start= auto ^
    depend= Tcpip/Dnscache

REM Configure service recovery
sc failure DexAgentsService reset= 86400 actions= restart/10000/restart/20000/none/60000

REM Set service to delayed auto-start
sc config DexAgentsService start= delayed-auto

REM Start service
sc start DexAgentsService

echo Service installation completed.
pause
```

### Service Monitoring

#### Service Health Check
```powershell
# Service health monitoring script
function Test-DexAgentsService {
    param([string[]]$ComputerNames)
    
    foreach ($computer in $ComputerNames) {
        try {
            $service = Get-Service -ComputerName $computer -Name "DexAgentsService" -ErrorAction Stop
            $process = Get-Process -ComputerName $computer -Name "DexAgentsService" -ErrorAction SilentlyContinue
            
            [PSCustomObject]@{
                ComputerName = $computer
                ServiceStatus = $service.Status
                ProcessID = if($process) { $process.Id } else { "N/A" }
                MemoryUsage = if($process) { "$([math]::Round($process.WorkingSet/1MB))MB" } else { "N/A" }
                StartTime = if($process) { $process.StartTime } else { "N/A" }
                Status = if($service.Status -eq "Running" -and $process) { "Healthy" } else { "Unhealthy" }
            }
        }
        catch {
            [PSCustomObject]@{
                ComputerName = $computer
                ServiceStatus = "Unknown"
                ProcessID = "N/A"
                MemoryUsage = "N/A"
                StartTime = "N/A"
                Status = "Error: $($_.Exception.Message)"
            }
        }
    }
}

# Usage
$computers = Get-ADComputer -Filter "OperatingSystem -like '*Windows*'" | Select-Object -ExpandProperty Name
Test-DexAgentsService -ComputerNames $computers | Format-Table -AutoSize
```

## 🔒 Security Configuration

### SSL/TLS Configuration

#### Certificate Management
```powershell
# Generate self-signed certificate for testing
New-SelfSignedCertificate -DnsName "dexagents.company.com" `
    -CertStoreLocation "cert:\LocalMachine\My" `
    -KeyUsage DigitalSignature,KeyEncipherment `
    -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.1")

# Export certificate for clients
$cert = Get-ChildItem -Path "cert:\LocalMachine\My" | Where-Object {$_.Subject -like "*dexagents*"}
Export-Certificate -Cert $cert -FilePath "C:\certs\dexagents-ca.crt"
```

#### Client Certificate Configuration
```json
{
  "security": {
    "verify_ssl": true,
    "ca_bundle_path": "C:\\ProgramData\\DexAgents\\certs\\ca-bundle.crt",
    "client_cert_path": "C:\\ProgramData\\DexAgents\\certs\\client.crt",
    "client_key_path": "C:\\ProgramData\\DexAgents\\certs\\client.key",
    "ssl_protocols": ["TLSv1.2", "TLSv1.3"],
    "cipher_suites": ["ECDHE-RSA-AES256-GCM-SHA384", "ECDHE-RSA-AES128-GCM-SHA256"]
  }
}
```

### Network Security

#### Firewall Rules
```powershell
# Create firewall rules for DexAgents
New-NetFirewallRule -DisplayName "DexAgents Agent Outbound" `
    -Direction Outbound -Protocol TCP -LocalPort Any -RemotePort 8080,8443 `
    -Action Allow -Profile Domain,Private

New-NetFirewallRule -DisplayName "DexAgents Agent HTTP" `
    -Direction Outbound -Protocol TCP -LocalPort Any -RemotePort 80,443 `
    -Action Allow -Profile Domain,Private

# Group Policy deployment
New-GPO -Name "DexAgents Firewall Rules" | `
New-GPLink -Target "OU=Workstations,DC=company,DC=com"
```

#### Proxy Configuration
```json
{
  "proxy": {
    "use_proxy": true,
    "proxy_type": "http",
    "proxy_host": "proxy.company.com",
    "proxy_port": 8080,
    "proxy_auth": {
      "username": "service-account",
      "password": "encrypted-password"
    },
    "proxy_bypass": ["localhost", "127.0.0.1", "*.company.com"],
    "proxy_timeout": 30
  }
}
```

### Access Control

#### Service Account Configuration
```powershell
# Create service account
New-ADUser -Name "DexAgents-Service" `
    -UserPrincipalName "dexagents-service@company.com" `
    -Path "OU=Service Accounts,DC=company,DC=com" `
    -Enabled $true `
    -PasswordNeverExpires $true `
    -CannotChangePassword $true

# Grant necessary permissions
$user = "COMPANY\DexAgents-Service"
$rights = @("SeServiceLogonRight", "SeInteractiveLogonRight")
foreach ($right in $rights) {
    Grant-UserRight -Account $user -Right $right
}
```

## 📊 Monitoring & Maintenance

### Health Monitoring

#### PowerShell Monitoring Script
```powershell
# DexAgents Health Monitor
param(
    [string[]]$Computers = @(),
    [string]$OutputPath = "C:\Reports\DexAgents-Health.csv",
    [int]$TimeoutSeconds = 30
)

function Get-DexAgentsHealth {
    param([string]$ComputerName)
    
    $result = [PSCustomObject]@{
        ComputerName = $ComputerName
        Timestamp = Get-Date
        ServiceStatus = "Unknown"
        ProcessStatus = "Unknown"
        ConfigValid = "Unknown"
        ServerConnectivity = "Unknown"
        MemoryUsage = 0
        CPUUsage = 0
        LogErrors = 0
        LastSeen = "Unknown"
        OverallHealth = "Unknown"
    }
    
    try {
        # Test computer connectivity
        if (-not (Test-Connection -ComputerName $ComputerName -Count 1 -Quiet -TimeoutSeconds 5)) {
            $result.OverallHealth = "Offline"
            return $result
        }
        
        # Check service status
        $service = Get-Service -ComputerName $ComputerName -Name "DexAgentsService" -ErrorAction SilentlyContinue
        $result.ServiceStatus = if ($service) { $service.Status } else { "Not Installed" }
        
        # Check process
        $process = Get-Process -ComputerName $ComputerName -Name "*DexAgents*" -ErrorAction SilentlyContinue
        if ($process) {
            $result.ProcessStatus = "Running"
            $result.MemoryUsage = [math]::Round($process.WorkingSet / 1MB, 2)
            $result.CPUUsage = $process.CPU
        }
        
        # Check configuration
        $configPath = "\\$ComputerName\C$\ProgramData\DexAgents\config.json"
        if (Test-Path $configPath) {
            try {
                $config = Get-Content $configPath | ConvertFrom-Json
                $result.ConfigValid = if ($config.server_url -and $config.api_token) { "Valid" } else { "Invalid" }
            } catch {
                $result.ConfigValid = "Corrupt"
            }
        } else {
            $result.ConfigValid = "Missing"
        }
        
        # Check log errors
        $logPath = "\\$ComputerName\C$\ProgramData\DexAgents\logs\agent.log"
        if (Test-Path $logPath) {
            $errors = Select-String -Path $logPath -Pattern "ERROR|CRITICAL" -AllMatches | 
                      Where-Object { $_.Line -match (Get-Date).ToString("yyyy-MM-dd") }
            $result.LogErrors = $errors.Count
        }
        
        # Overall health assessment
        $result.OverallHealth = switch ($true) {
            ($result.ServiceStatus -eq "Running" -and $result.ProcessStatus -eq "Running" -and 
             $result.ConfigValid -eq "Valid" -and $result.LogErrors -eq 0) { "Healthy" }
            ($result.ServiceStatus -eq "Running" -and $result.LogErrors -lt 5) { "Warning" }
            default { "Critical" }
        }
        
    } catch {
        $result.OverallHealth = "Error: $($_.Exception.Message)"
    }
    
    return $result
}

# Get computer list if not provided
if ($Computers.Count -eq 0) {
    $Computers = Get-ADComputer -Filter "OperatingSystem -like '*Windows*'" | 
                 Select-Object -ExpandProperty Name
}

# Monitor all computers
$results = @()
$total = $Computers.Count
$current = 0

foreach ($computer in $Computers) {
    $current++
    Write-Progress -Activity "Monitoring DexAgents Health" -Status "Processing $computer" `
        -PercentComplete (($current / $total) * 100)
    
    $results += Get-DexAgentsHealth -ComputerName $computer
}

# Export results
$results | Export-Csv -Path $OutputPath -NoTypeInformation
Write-Host "Health report saved to: $OutputPath"

# Summary
$summary = $results | Group-Object OverallHealth | Select-Object Name, Count
Write-Host "`nHealth Summary:"
$summary | Format-Table -AutoSize
```

### Log Management

#### Log Rotation Script
```powershell
# DexAgents Log Rotation
param(
    [string]$LogDirectory = "C:\ProgramData\DexAgents\logs",
    [int]$MaxFileSizeMB = 10,
    [int]$MaxFiles = 5
)

function Invoke-LogRotation {
    param(
        [string]$LogPath,
        [int]$MaxSizeMB,
        [int]$MaxFiles
    )
    
    if (-not (Test-Path $LogPath)) { return }
    
    $logFile = Get-Item $LogPath
    $sizeMB = [math]::Round($logFile.Length / 1MB, 2)
    
    if ($sizeMB -gt $MaxSizeMB) {
        # Rotate existing files
        for ($i = $MaxFiles - 1; $i -gt 0; $i--) {
            $oldFile = "$LogPath.$i"
            $newFile = "$LogPath.$($i + 1)"
            
            if (Test-Path $oldFile) {
                if ($i -eq ($MaxFiles - 1)) {
                    Remove-Item $oldFile -Force
                } else {
                    Move-Item $oldFile $newFile -Force
                }
            }
        }
        
        # Move current log
        Move-Item $LogPath "$LogPath.1" -Force
        
        # Create new log file
        New-Item $LogPath -ItemType File -Force
        
        Write-Host "Rotated log: $LogPath (was $sizeMB MB)"
    }
}

# Rotate all log files
Get-ChildItem $LogDirectory -Filter "*.log" | ForEach-Object {
    Invoke-LogRotation -LogPath $_.FullName -MaxSizeMB $MaxFileSizeMB -MaxFiles $MaxFiles
}

# Clean old backup files
Get-ChildItem $LogDirectory -Filter "*.log.*" | 
    Where-Object { $_.Name -match "\.log\.([6-9]|\d{2,})$" } | 
    Remove-Item -Force

Write-Host "Log rotation completed for $LogDirectory"
```

### Performance Monitoring

#### Performance Counter Collection
```powershell
# Collect DexAgents performance metrics
$counters = @(
    "\Process(DexAgents*)\% Processor Time",
    "\Process(DexAgents*)\Working Set",
    "\Process(DexAgents*)\IO Read Bytes/sec",
    "\Process(DexAgents*)\IO Write Bytes/sec",
    "\Process(DexAgents*)\Thread Count"
)

$samples = Get-Counter -Counter $counters -SampleInterval 5 -MaxSamples 12

$samples.CounterSamples | Group-Object Path | ForEach-Object {
    $counter = $_.Name
    $values = $_.Group | Select-Object -ExpandProperty CookedValue
    
    [PSCustomObject]@{
        Counter = $counter.Split('\')[-1]
        Average = [math]::Round(($values | Measure-Object -Average).Average, 2)
        Maximum = [math]::Round(($values | Measure-Object -Maximum).Maximum, 2)
        Minimum = [math]::Round(($values | Measure-Object -Minimum).Minimum, 2)
    }
} | Format-Table -AutoSize
```

## 🔧 Troubleshooting

### Common Issues

#### Agent Won't Start
```powershell
# Diagnostic script for startup issues
function Test-DexAgentsStartup {
    param([string]$ComputerName = $env:COMPUTERNAME)
    
    Write-Host "Diagnosing DexAgents startup issues on $ComputerName..." -ForegroundColor Yellow
    
    # Check if executable exists
    $exePath = "C:\Program Files\DexAgents\DexAgentsAgent.exe"
    if (Test-Path $exePath) {
        Write-Host "✓ Executable found: $exePath" -ForegroundColor Green
    } else {
        Write-Host "✗ Executable not found: $exePath" -ForegroundColor Red
        return
    }
    
    # Check dependencies
    $dependencies = @("msvcp140.dll", "vcruntime140.dll", "ucrtbase.dll")
    foreach ($dll in $dependencies) {
        $found = Get-Command $dll -ErrorAction SilentlyContinue
        if ($found) {
            Write-Host "✓ Dependency found: $dll" -ForegroundColor Green
        } else {
            Write-Host "✗ Dependency missing: $dll" -ForegroundColor Red
        }
    }
    
    # Check configuration
    $configPath = "C:\ProgramData\DexAgents\config.json"
    if (Test-Path $configPath) {
        try {
            $config = Get-Content $configPath | ConvertFrom-Json
            Write-Host "✓ Configuration file valid" -ForegroundColor Green
            
            # Test server connectivity
            $serverUrl = $config.server_url
            if ($serverUrl) {
                try {
                    $response = Invoke-WebRequest -Uri $serverUrl -TimeoutSec 10 -UseBasicParsing
                    Write-Host "✓ Server reachable: $serverUrl" -ForegroundColor Green
                } catch {
                    Write-Host "✗ Server unreachable: $serverUrl - $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        } catch {
            Write-Host "✗ Configuration file corrupt: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ Configuration file not found: $configPath" -ForegroundColor Red
    }
    
    # Check Windows Event Log
    $events = Get-WinEvent -FilterHashtable @{LogName='Application'; ProviderName='DexAgents*'} -MaxEvents 5 -ErrorAction SilentlyContinue
    if ($events) {
        Write-Host "Recent DexAgents events:" -ForegroundColor Yellow
        $events | ForEach-Object {
            $level = switch ($_.LevelDisplayName) {
                "Error" { "Red" }
                "Warning" { "Yellow" } 
                default { "White" }
            }
            Write-Host "  $($_.TimeCreated) [$($_.LevelDisplayName)] $($_.Message)" -ForegroundColor $level
        }
    }
}

Test-DexAgentsStartup
```

#### Connection Issues
```powershell
# Network connectivity troubleshooting
function Test-DexAgentsConnectivity {
    param(
        [string]$ServerUrl = "https://dexagents.company.com:8080",
        [string]$ConfigPath = "C:\ProgramData\DexAgents\config.json"
    )
    
    # Load server URL from config if available
    if (Test-Path $ConfigPath) {
        try {
            $config = Get-Content $ConfigPath | ConvertFrom-Json
            $ServerUrl = $config.server_url
        } catch {
            Write-Warning "Could not parse config file"
        }
    }
    
    if (-not $ServerUrl) {
        Write-Error "No server URL specified"
        return
    }
    
    Write-Host "Testing connectivity to: $ServerUrl" -ForegroundColor Yellow
    
    # Parse URL
    $uri = [System.Uri]$ServerUrl
    $hostname = $uri.Host
    $port = $uri.Port
    
    # DNS resolution
    try {
        $dnsResult = Resolve-DnsName -Name $hostname -ErrorAction Stop
        Write-Host "✓ DNS resolution successful: $hostname -> $($dnsResult.IPAddress -join ', ')" -ForegroundColor Green
    } catch {
        Write-Host "✗ DNS resolution failed: $hostname" -ForegroundColor Red
        return
    }
    
    # TCP connectivity
    try {
        $tcpResult = Test-NetConnection -ComputerName $hostname -Port $port -WarningAction SilentlyContinue
        if ($tcpResult.TcpTestSucceeded) {
            Write-Host "✓ TCP connection successful: $hostname`:$port" -ForegroundColor Green
        } else {
            Write-Host "✗ TCP connection failed: $hostname`:$port" -ForegroundColor Red
        }
    } catch {
        Write-Host "✗ TCP test error: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # HTTP/HTTPS test
    try {
        $response = Invoke-WebRequest -Uri $ServerUrl -TimeoutSec 10 -UseBasicParsing
        Write-Host "✓ HTTP response: $($response.StatusCode) $($response.StatusDescription)" -ForegroundColor Green
    } catch {
        Write-Host "✗ HTTP request failed: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    # Check proxy settings
    $proxy = [System.Net.WebRequest]::GetSystemWebProxy()
    $proxyUrl = $proxy.GetProxy([System.Uri]$ServerUrl)
    if ($proxyUrl -ne $ServerUrl) {
        Write-Host "ℹ Proxy detected: $proxyUrl" -ForegroundColor Cyan
    }
    
    # Check firewall
    $firewallRules = Get-NetFirewallRule | Where-Object { 
        $_.DisplayName -like "*DexAgents*" -and $_.Enabled -eq "True" 
    }
    if ($firewallRules) {
        Write-Host "✓ Firewall rules found: $($firewallRules.Count) rules" -ForegroundColor Green
    } else {
        Write-Host "⚠ No firewall rules found for DexAgents" -ForegroundColor Yellow
    }
}

Test-DexAgentsConnectivity
```

### Diagnostic Tools

#### System Information Collection
```powershell
# Comprehensive system diagnostic
function Get-DexAgentsSystemInfo {
    $info = [PSCustomObject]@{
        ComputerName = $env:COMPUTERNAME
        Timestamp = Get-Date
        OSVersion = (Get-CimInstance Win32_OperatingSystem).Caption
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        DotNetVersion = [System.Runtime.InteropServices.RuntimeInformation]::FrameworkDescription
        Architecture = $env:PROCESSOR_ARCHITECTURE
        Domain = $env:USERDOMAIN
        UserContext = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
        IsAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
    }
    
    # DexAgents specific info
    $exePath = "C:\Program Files\DexAgents\DexAgentsAgent.exe"
    if (Test-Path $exePath) {
        $version = (Get-ItemProperty $exePath).VersionInfo
        $info | Add-Member -NotePropertyName "DexAgentsVersion" -NotePropertyValue $version.FileVersion
        $info | Add-Member -NotePropertyName "DexAgentsDate" -NotePropertyValue (Get-Item $exePath).LastWriteTime
    }
    
    # Service info
    $service = Get-Service -Name "DexAgentsService" -ErrorAction SilentlyContinue
    if ($service) {
        $info | Add-Member -NotePropertyName "ServiceStatus" -NotePropertyValue $service.Status
        $info | Add-Member -NotePropertyName "ServiceStartType" -NotePropertyValue $service.StartType
    }
    
    # Network info
    $networkInfo = Get-NetIPConfiguration | Where-Object { $_.NetAdapter.Status -eq "Up" } | Select-Object -First 1
    if ($networkInfo) {
        $info | Add-Member -NotePropertyName "IPAddress" -NotePropertyValue $networkInfo.IPv4Address.IPAddress
        $info | Add-Member -NotePropertyName "DNSServers" -NotePropertyValue ($networkInfo.DNSServer.ServerAddresses -join ", ")
    }
    
    return $info
}

Get-DexAgentsSystemInfo | Format-List
```

## 📋 Best Practices

### Deployment Best Practices

#### Pre-deployment Checklist
- [ ] Server infrastructure sized appropriately
- [ ] Network connectivity tested
- [ ] Security certificates prepared
- [ ] Configuration templates created
- [ ] Deployment tools configured
- [ ] Pilot group identified
- [ ] Rollback plan prepared
- [ ] Monitoring tools ready

#### Staged Deployment
```
Phase 1: Pilot (10-20 computers)
├── Test basic functionality
├── Validate configuration
├── Monitor performance
└── Gather feedback

Phase 2: Limited Deployment (100-200 computers)  
├── Deploy to early adopters
├── Test scale performance
├── Refine configuration
└── Train support staff

Phase 3: Full Deployment (All computers)
├── Department-by-department rollout
├── Continuous monitoring
├── Issue resolution
└── User training
```

### Configuration Best Practices

#### Standardized Naming
```
Agent Names:
- Format: {Department}-{Location}-{ComputerName}
- Example: IT-NYC-DESKTOP001

Tags:
- Department: IT, HR, Finance, Sales
- Location: NYC, LAX, CHI, Remote
- Type: Desktop, Laptop, Server
- Environment: Prod, Dev, Test
```

#### Security Hardening
```json
{
  "security_config": {
    "verify_ssl": true,
    "log_level": "WARNING",
    "enable_debug_mode": false,
    "max_log_size_mb": 10,
    "max_log_files": 3,
    "enable_resource_limits": true,
    "max_cpu_percent": 25,
    "max_memory_mb": 256,
    "process_priority": "below_normal"
  }
}
```

### Monitoring Best Practices

#### Health Check Automation
```powershell
# Scheduled task for health monitoring
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" `
    -Argument "-File C:\Scripts\DexAgents-HealthCheck.ps1"

$trigger = New-ScheduledTaskTrigger -Daily -At 2AM

$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount

Register-ScheduledTask -TaskName "DexAgents Health Check" `
    -Action $action -Trigger $trigger -Principal $principal
```

#### Alerting Thresholds
```
Critical Alerts:
- Service stopped for >5 minutes
- Connection failed for >15 minutes  
- Memory usage >500MB
- Error rate >10 errors/hour

Warning Alerts:
- Service restarted
- Connection unstable
- Memory usage >200MB
- Log file >50MB
```

## 📚 Appendix

### Command Reference

#### Service Management
```batch
REM Install service
sc create DexAgentsService binPath= "C:\DexAgents\DexAgentsService.exe"

REM Configure service
sc config DexAgentsService start= auto
sc description DexAgentsService "DexAgents Windows Management Service"

REM Service operations
sc start DexAgentsService
sc stop DexAgentsService
sc query DexAgentsService

REM Remove service
sc delete DexAgentsService
```

#### Registry Operations
```batch
REM Export configuration
reg export HKLM\SOFTWARE\DexAgents C:\backup\dexagents-config.reg

REM Import configuration
reg import C:\config\dexagents-config.reg

REM Query settings
reg query HKLM\SOFTWARE\DexAgents /v ServerURL
```

#### Event Log Management
```powershell
# Create custom event log
New-EventLog -LogName "DexAgents" -Source "DexAgentsService"

# Query events
Get-WinEvent -FilterHashtable @{LogName='DexAgents'; Level=2} -MaxEvents 50

# Clear log
Clear-EventLog -LogName "DexAgents"
```

### API Reference

#### REST API Endpoints
```
GET    /api/v1/agents              # List all agents
GET    /api/v1/agents/{id}         # Get agent details
POST   /api/v1/agents              # Register agent
PUT    /api/v1/agents/{id}         # Update agent
DELETE /api/v1/agents/{id}         # Delete agent

GET    /api/v1/agents/{id}/status  # Agent status
POST   /api/v1/agents/{id}/command # Execute command
GET    /api/v1/agents/{id}/logs    # Get logs
```

#### WebSocket Events
```javascript
// Connection events
{
  "type": "connect",
  "agent_id": "desktop-001",
  "timestamp": "2024-01-15T10:30:00Z"
}

// System metrics
{
  "type": "metrics",
  "data": {
    "cpu_usage": 25.5,
    "memory_usage": 67.2,
    "disk_usage": 45.1
  }
}

// Command execution
{
  "type": "command_result",
  "command_id": "cmd-12345",
  "success": true,
  "output": "Command output"
}
```

### File Locations

#### Installation Paths
```
System Installation:
├── C:\Program Files\DexAgents\
│   ├── DexAgentsAgent.exe
│   ├── DexAgentsService.exe
│   └── DexAgentsInstaller.exe

Configuration:
├── C:\ProgramData\DexAgents\
│   ├── config.json
│   ├── logs\
│   └── certs\

User Installation:
├── %LOCALAPPDATA%\DexAgents\
│   ├── config.json
│   └── logs\
```

#### Registry Locations
```
System Settings:
├── HKLM\SOFTWARE\DexAgents\
│   ├── ServerURL
│   ├── AutoStart
│   └── RunAsService

User Settings:
├── HKCU\SOFTWARE\DexAgents\
│   ├── WindowPosition
│   ├── MinimizeToTray
│   └── UserPreferences
```

---

*DexAgents Administrator Guide v3.0*  
*Last updated: January 2024*