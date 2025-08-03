# DexAgents Windows Agent User Guide

## 📚 Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements) 
3. [Installation Guide](#installation-guide)
4. [Configuration](#configuration)
5. [System Tray Usage](#system-tray-usage)
6. [GUI Interface](#gui-interface)
7. [Service Management](#service-management)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)
10. [FAQ](#faq)

## 🎯 Overview

DexAgents Windows Agent is a comprehensive system management tool that provides:

- **Real-time System Monitoring** - CPU, memory, disk, and network monitoring
- **Process Management** - View, monitor, and manage system processes
- **Remote Command Execution** - Secure PowerShell command execution
- **System Tray Integration** - Unobtrusive background operation
- **Service Management** - Run as Windows service with auto-start capabilities  
- **Advanced Configuration** - Extensive customization options

### Key Features

- ✅ **Modern GUI Interface** - Clean, intuitive user interface
- ✅ **System Tray Operation** - Minimize to tray for background operation
- ✅ **Auto-start Support** - Automatic startup with Windows
- ✅ **Service Installation** - Run as Windows service for enterprise environments
- ✅ **Real-time Monitoring** - Live system metrics and process information
- ✅ **Secure Communication** - WebSocket-based encrypted communication
- ✅ **Comprehensive Logging** - Detailed logs for troubleshooting
- ✅ **Process Control** - Kill processes and bulk operations

## 💻 System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (64-bit) or later
- **RAM**: 4GB minimum
- **Disk Space**: 100MB free space
- **Network**: Internet connection for server communication

### Recommended Requirements
- **Operating System**: Windows 11 (64-bit)
- **RAM**: 8GB or more
- **Disk Space**: 500MB free space
- **Network**: Stable broadband connection

### Supported Windows Versions
- ✅ Windows 11 (all editions)
- ✅ Windows 10 version 1903 or later
- ✅ Windows Server 2019/2022

## 🚀 Installation Guide

### Method 1: Interactive Installer (Recommended)

1. **Download** the DexAgents installer from your administrator
2. **Right-click** on `DexAgentsInstaller.exe` and select "Run as administrator"
3. **Follow** the installation wizard:
   - Accept the license agreement
   - Choose installation location (default: `C:\\Program Files\\DexAgents`)
   - Configure connection settings
   - Select installation options
4. **Complete** the installation and launch the agent

### Method 2: Automated Installation

1. **Extract** the installation package to a folder
2. **Right-click** on `install.bat` and select "Run as administrator"  
3. **Wait** for the automatic installation to complete
4. **Configure** the agent using the desktop shortcut

### Method 3: Manual Installation

1. **Create** installation directory: `C:\\DexAgents`
2. **Copy** all files from the package to the installation directory
3. **Edit** `config.json` with your server settings
4. **Create** desktop shortcut (optional)
5. **Run** `DexAgentsAgent.exe` to start the agent

### Installation Options

#### Desktop Integration
- ✅ **Desktop Shortcut** - Quick access from desktop
- ✅ **Start Menu Entry** - Access from Start Menu
- ✅ **System Tray Icon** - Background operation indicator

#### Auto-start Configuration  
- ✅ **Windows Startup** - Start with Windows login
- ✅ **Windows Service** - Run as system service (requires admin rights)
- ✅ **Task Scheduler** - Advanced scheduling options

## ⚙️ Configuration

### Basic Configuration

The agent requires minimal configuration to get started:

```json
{
  "server_url": "http://your-server:8080",
  "api_token": "your-api-token", 
  "agent_name": "your-computer-name"
}
```

#### Required Settings
- **Server URL**: The DexAgents server address
- **API Token**: Authentication token provided by your administrator
- **Agent Name**: Unique identifier for this agent

### Configuration File Location

The configuration file `config.json` is located at:
- **User Installation**: `%USERPROFILE%\\AppData\\Local\\DexAgents\\config.json`
- **System Installation**: `C:\\ProgramData\\DexAgents\\config.json`
- **Portable Installation**: Same directory as executable

### GUI Configuration

1. **Launch** the DexAgents Agent from desktop shortcut
2. **Enter** your server connection details:
   - Server URL (e.g., `http://company-server:8080`)
   - API Token (provided by administrator)
   - Agent Name (computer name or custom identifier)
3. **Configure** optional settings:
   - Tags for categorization
   - Auto-start preferences
   - System tray behavior
4. **Click** "Save Configuration" to apply settings
5. **Click** "Start Agent" to begin monitoring

## 🔧 System Tray Usage

### Accessing the System Tray

The DexAgents system tray icon appears in the Windows notification area (bottom-right corner). If you don't see it:

1. **Click** the "Show hidden icons" arrow (^) in the notification area
2. **Look** for the DexAgents icon
3. **Right-click** the icon to access the context menu

### System Tray Menu Options

Right-click the system tray icon to access these options:

#### 📊 **Show Dashboard**
- Opens the main GUI interface
- View real-time system metrics
- Access all agent features

#### ⚙️ **Configuration**
- Quick access to connection settings
- Modify server URL and API token
- Update agent name and tags

#### 📈 **System Status**
- View current connection status
- Check system performance metrics
- Monitor agent health

#### 🔄 **Restart Agent**
- Restart the agent service
- Useful for applying configuration changes
- Reconnects to server

#### 📝 **View Logs**
- Open the logs directory
- View recent activity logs
- Troubleshoot connection issues

#### 🌐 **Open Web Interface**
- Launch the web dashboard in browser
- Access advanced features remotely
- View centralized management interface

#### ❌ **Exit**
- Stop the agent and close application
- Will not restart automatically
- Use "Restart Agent" instead for temporary stops

### System Tray Notifications

The system tray provides visual feedback through notifications:

- 🟢 **Green Icon**: Agent connected and operational
- 🟡 **Yellow Icon**: Agent connecting or warning state
- 🔴 **Red Icon**: Agent disconnected or error state
- 💬 **Notifications**: Important status updates and alerts

### Minimizing to System Tray

The agent can be configured to minimize to the system tray:

1. **Enable** "Minimize to Tray" in configuration
2. **Close** the main window (it will minimize to tray)
3. **Double-click** the tray icon to restore the window
4. **Right-click** the tray icon for quick actions

## 🖥️ GUI Interface

### Main Window Components

#### Title Bar
- **Agent Name**: Current agent identifier
- **Connection Status**: Real-time connection indicator
- **Version**: Current agent version

#### Configuration Section
- **Server URL**: DexAgents server address
- **API Token**: Authentication credentials
- **Agent Name**: Agent identifier
- **Tags**: Categorization labels
- **Options**: Auto-start and service settings

#### System Status Section
- **Connection Status**: Server connectivity
- **Agent Status**: Current operational state
- **Last Seen**: Last successful server communication
- **System Metrics**: CPU, Memory, Disk usage
- **Auto-start Status**: Current auto-start configuration

#### Control Buttons
- **Start Agent**: Begin monitoring and communication
- **Stop Agent**: Stop monitoring (stays in tray)
- **Restart Agent**: Restart the agent process
- **Advanced Settings**: Open advanced configuration
- **Save Configuration**: Apply current settings
- **Open Logs**: View log files
- **Web Interface**: Launch web dashboard

#### Activity Log
- **Real-time Messages**: Live activity feed
- **Timestamp**: When each event occurred
- **Message Types**: Info, Warning, Error, Success
- **Auto-scroll**: Automatically shows latest messages

### Status Indicators

#### Connection Status Colors
- 🟢 **Green**: Successfully connected to server
- 🟡 **Yellow**: Connecting or authentication in progress  
- 🔴 **Red**: Disconnected or connection failed
- ⚪ **Gray**: Agent stopped or not started

#### System Metrics
- **CPU Usage**: Current processor utilization percentage
- **Memory Usage**: RAM utilization percentage  
- **Disk Usage**: Primary drive space utilization
- **Auto-start**: Current auto-start configuration status

## 🔧 Service Management

### Running as Windows Service

#### Installing as Service
1. **Run** installer as administrator
2. **Check** "Run as Windows Service" option
3. **Complete** installation process
4. **Service** will start automatically

#### Manual Service Installation
```batch
# Install service
sc create DexAgentsService binPath= "C:\DexAgents\DexAgentsService.exe"
sc description DexAgentsService "DexAgents Windows Management Service"

# Start service  
sc start DexAgentsService

# Configure auto-start
sc config DexAgentsService start= auto
```

#### Service Management Commands
```batch
# Check service status
sc query DexAgentsService

# Start service
sc start DexAgentsService

# Stop service
sc stop DexAgentsService

# Remove service
sc delete DexAgentsService
```

### Auto-start Configuration

#### Registry Entry (Current User)
The agent creates a registry entry for auto-start:
- **Location**: `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`
- **Value**: `DexAgents`
- **Data**: Path to executable with parameters

#### Task Scheduler (Advanced)
For advanced scheduling, the agent can create a scheduled task:
- **Task Name**: DexAgents
- **Trigger**: At user logon
- **Action**: Start DexAgents Agent
- **Settings**: Run with highest privileges

#### Service Mode (System-wide)
When running as a service:
- **Starts**: Automatically with Windows
- **User Context**: SYSTEM account
- **Permissions**: Full system access
- **Management**: Windows Service Manager

## 🛠️ Troubleshooting

### Common Issues

#### Agent Won't Start
**Symptoms**: Application fails to launch or crashes immediately

**Solutions**:
1. **Run as Administrator**: Right-click executable, select "Run as administrator"
2. **Check Dependencies**: Ensure all required DLLs are present
3. **Antivirus**: Add DexAgents to antivirus exclusions
4. **Compatibility**: Verify Windows version compatibility
5. **Logs**: Check `logs\\agent.log` for error messages

#### Connection Failed
**Symptoms**: Agent shows "Disconnected" status

**Solutions**:
1. **Server URL**: Verify server address is correct and reachable
2. **API Token**: Ensure token is valid and not expired
3. **Firewall**: Check Windows Firewall and corporate firewall settings
4. **Network**: Test network connectivity to server
5. **Proxy**: Configure proxy settings if required

#### High CPU/Memory Usage  
**Symptoms**: Agent consuming excessive system resources

**Solutions**:
1. **Update Interval**: Increase monitoring interval in advanced settings
2. **Resource Limits**: Enable resource limits in advanced configuration
3. **Process Count**: Reduce number of monitored processes
4. **Logs**: Check for error loops in log files
5. **Restart**: Restart agent to clear memory leaks

#### System Tray Icon Missing
**Symptoms**: Cannot find system tray icon

**Solutions**:
1. **Hidden Icons**: Click "^" arrow to show hidden icons
2. **Notification Settings**: Enable system tray notifications in Windows
3. **Tray Manager**: Check if tray manager service is running
4. **Restart**: Restart agent to recreate tray icon
5. **Alternative**: Use Start Menu or desktop shortcut

### Log Files

#### Log Locations
- **User Mode**: `%LOCALAPPDATA%\\DexAgents\\logs\\`
- **Service Mode**: `C:\\ProgramData\\DexAgents\\logs\\`
- **Portable**: `logs\\` directory next to executable

#### Log Types
- **agent.log**: Main application log
- **error.log**: Error-specific messages
- **service.log**: Windows service events
- **websocket.log**: Communication logs

#### Log Analysis
```text
# Example log entry
2024-01-15 10:30:45,123 - INFO - Agent started successfully
2024-01-15 10:30:46,456 - INFO - Connecting to server: http://server:8080
2024-01-15 10:30:47,789 - INFO - Authentication successful
2024-01-15 10:30:48,012 - INFO - System monitoring started
```

### Diagnostic Commands

#### System Information
```powershell
# Get system info
Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, TotalPhysicalMemory

# Check running processes
Get-Process | Where-Object {$_.ProcessName -like "*DexAgents*"}

# Test network connectivity
Test-NetConnection -ComputerName server-address -Port 8080
```

#### Service Diagnostics
```powershell
# Check service status
Get-Service -Name "DexAgentsService"

# View service logs
Get-EventLog -LogName Application -Source "DexAgentsService" -Newest 10
```

## 🔧 Advanced Configuration

### Configuration File Options

#### Network Settings
```json
{
  "connection_timeout": 30,
  "command_timeout": 120,
  "max_retries": 3,
  "retry_delay": 5,
  "heartbeat_interval": 30
}
```

#### Proxy Configuration
```json
{
  "use_proxy": true,
  "proxy_type": "http",
  "proxy_host": "proxy.company.com",
  "proxy_port": "8080",
  "proxy_username": "user",
  "proxy_password": "pass"
}
```

#### SSL/TLS Settings
```json
{
  "verify_ssl": true,
  "ca_bundle_path": "C:\\certs\\ca-bundle.crt",
  "client_cert_path": "C:\\certs\\client.crt",
  "client_key_path": "C:\\certs\\client.key"
}
```

#### Logging Configuration
```json
{
  "log_level": "INFO",
  "log_to_file": true,
  "log_file_path": "C:\\DexAgents\\logs\\agent.log",
  "max_log_size_mb": 10,
  "max_log_files": 5,
  "log_to_console": true
}
```

#### Resource Limits
```json
{
  "enable_resource_limits": true,
  "max_cpu_percent": 50,
  "max_memory_mb": 512,
  "process_priority": "normal"
}
```

### Performance Tuning

#### Optimize for Low Resource Usage
```json
{
  "update_interval": 60,
  "heartbeat_interval": 60,
  "enable_performance_monitoring": false,
  "max_cpu_percent": 25,
  "max_memory_mb": 256
}
```

#### Optimize for High Performance
```json
{
  "update_interval": 10,
  "heartbeat_interval": 15,
  "enable_performance_monitoring": true,
  "connection_timeout": 5,
  "command_timeout": 30
}
```

### Security Hardening

#### Secure Configuration
```json
{
  "verify_ssl": true,
  "enable_debug_mode": false,
  "log_level": "WARNING",
  "process_priority": "below_normal",
  "enable_resource_limits": true
}
```

## ❓ FAQ

### General Questions

**Q: What is DexAgents?**
A: DexAgents is a comprehensive Windows system management and monitoring solution that provides real-time system metrics, process management, and remote command execution capabilities.

**Q: Is DexAgents free?**
A: DexAgents licensing depends on your organization's agreement. Contact your system administrator for licensing information.

**Q: Can I run multiple agents on the same computer?**
A: No, only one DexAgents instance should run per computer to avoid conflicts.

### Installation Questions

**Q: Do I need administrator rights to install DexAgents?**
A: Administrator rights are required for:
- Installing to Program Files
- Setting up Windows Service
- Creating auto-start entries
- System-wide configuration

**Q: Can I install DexAgents on a virtual machine?**
A: Yes, DexAgents works on virtual machines. Ensure the VM has adequate resources and network connectivity.

**Q: Where should I install DexAgents?**
A: Recommended locations:
- `C:\\Program Files\\DexAgents` (system-wide)
- `C:\\Users\\{username}\\AppData\\Local\\DexAgents` (user-specific)
- Custom location of your choice

### Configuration Questions

**Q: Where do I get the API token?**
A: The API token is provided by your system administrator or can be generated from the DexAgents server web interface.

**Q: Can I change the agent name after installation?**
A: Yes, you can change the agent name in the configuration at any time. The change takes effect after restarting the agent.

**Q: What tags should I use?**
A: Common tags include:
- Department (IT, HR, Finance)
- Location (Office, Remote, DataCenter)  
- Environment (Production, Development, Test)
- Function (Server, Workstation, Laptop)

### Operation Questions

**Q: How much system resources does DexAgents use?**
A: Typical resource usage:
- CPU: 1-3% during normal operation
- Memory: 50-100 MB
- Disk: Minimal (log files grow over time)
- Network: Low bandwidth usage

**Q: Can I run DexAgents without the GUI?**
A: Yes, use `DexAgentsService.exe` for headless operation or run the main agent with `--service-mode` parameter.

**Q: How do I know if the agent is working?**
A: Check these indicators:
- System tray icon is green
- GUI shows "Connected" status
- Recent activity in logs
- Agent appears in web dashboard

### Troubleshooting Questions

**Q: The agent keeps disconnecting. What should I do?**
A: Common solutions:
1. Check network stability
2. Verify server availability  
3. Review firewall settings
4. Check proxy configuration
5. Examine log files for errors

**Q: I can't see the system tray icon. Where is it?**
A: The icon may be hidden. Click the "^" arrow in the notification area to show hidden icons. You can also access the agent via Start Menu or desktop shortcut.

**Q: How do I update DexAgents?**
A: Update methods:
1. Download new installer and run it
2. Use automatic update feature (if enabled)
3. Replace executable files manually
4. Contact administrator for enterprise updates

### Advanced Questions

**Q: Can I customize the monitoring interval?**
A: Yes, modify the `update_interval` setting in advanced configuration. Lower values provide more frequent updates but use more resources.

**Q: How do I enable debug logging?**
A: Set `log_level` to "DEBUG" in configuration and `enable_debug_mode` to true. This will generate detailed logs for troubleshooting.

**Q: Can DexAgents work behind a corporate firewall?**
A: Yes, configure proxy settings in advanced configuration. Ensure the following ports are allowed:
- HTTP: 80, 8080 (configurable)
- HTTPS: 443, 8443 (configurable)
- WebSocket: Same as HTTP/HTTPS ports

---

## 📞 Support

### Getting Help

1. **Check Logs**: Review log files for error messages
2. **Test Connection**: Verify server connectivity  
3. **Review Configuration**: Ensure settings are correct
4. **Contact Administrator**: Reach out to your system administrator
5. **Documentation**: Refer to this user guide

### Reporting Issues

When reporting issues, include:
- **Agent Version**: Found in GUI title bar
- **Operating System**: Windows version and edition
- **Error Messages**: Exact error text from logs
- **Configuration**: Relevant settings (remove sensitive data)
- **Steps to Reproduce**: How to recreate the issue

### Additional Resources

- **Web Dashboard**: Access advanced features and monitoring
- **Server Documentation**: Administrator guides and API reference
- **Update Notifications**: Automatic notifications for new versions
- **Community Forums**: User community and knowledge base

---

*DexAgents Windows Agent User Guide v3.0*  
*Last updated: January 2024*