# DexAgents Quick Reference

## 🚀 Quick Start

### Installation (5 minutes)
```batch
1. Run DexAgentsInstaller.exe as Administrator
2. Enter server URL: https://your-server:8080
3. Enter API token (from administrator)
4. Choose installation options
5. Click Install & Start
```

### First Configuration
```json
{
  "server_url": "https://server:8080",
  "api_token": "your-token-here",
  "agent_name": "computer-name",
  "auto_start": true
}
```

## 🔧 System Tray Actions

| Action | How To |
|--------|--------|
| **Show Dashboard** | Double-click tray icon |
| **Quick Status** | Hover over tray icon |
| **Configuration** | Right-click → Configuration |
| **Restart Agent** | Right-click → Restart Agent |
| **View Logs** | Right-click → View Logs |
| **Exit** | Right-click → Exit |

## ⚙️ Common Configurations

### Basic Setup
```json
{
  "server_url": "http://localhost:8080",
  "api_token": "demo-token",
  "agent_name": "my-computer"
}
```

### Enterprise Setup  
```json
{
  "server_url": "https://dexagents.company.com:8443",
  "api_token": "prod-token-xyz",
  "agent_name": "IT-NYC-DESKTOP001",
  "tags": ["production", "IT", "monitored"],
  "auto_start": true,
  "run_as_service": true
}
```

### Proxy Setup
```json
{
  "server_url": "https://server:8080",
  "use_proxy": true,
  "proxy_host": "proxy.company.com",
  "proxy_port": "8080"
}
```

## 🛠️ Troubleshooting

### Agent Won't Start
```
1. Check logs in: C:\ProgramData\DexAgents\logs\
2. Run as Administrator
3. Check antivirus exclusions
4. Verify configuration file
```

### Connection Failed
```
1. Test server URL in browser
2. Check firewall settings
3. Verify API token
4. Test network connectivity: ping server-name
```

### High Resource Usage
```
1. Increase update_interval to 60
2. Enable resource limits
3. Check for log errors
4. Restart agent
```

## 💻 Command Line

### Service Management
```batch
# Install service
sc create DexAgentsService binPath="C:\Program Files\DexAgents\DexAgentsService.exe"

# Start/Stop service
sc start DexAgentsService
sc stop DexAgentsService

# Check status
sc query DexAgentsService
```

### Configuration
```batch
# Edit config
notepad "C:\ProgramData\DexAgents\config.json"

# Test connectivity
telnet server-name 8080

# View logs
type "C:\ProgramData\DexAgents\logs\agent.log"
```

## 🔍 Status Indicators

### System Tray Icons
- 🟢 **Green**: Connected and healthy
- 🟡 **Yellow**: Connecting or warning
- 🔴 **Red**: Disconnected or error
- ⚪ **Gray**: Stopped

### GUI Status Colors
- **Green**: Success/Connected
- **Yellow**: Warning/Connecting  
- **Red**: Error/Disconnected
- **Blue**: Information

## 📁 File Locations

### Important Files
```
Configuration:   C:\ProgramData\DexAgents\config.json
Logs:           C:\ProgramData\DexAgents\logs\agent.log  
Executable:     C:\Program Files\DexAgents\DexAgentsAgent.exe
Service:        C:\Program Files\DexAgents\DexAgentsService.exe
```

### User Files
```
User Config:    %LOCALAPPDATA%\DexAgents\config.json
User Logs:      %LOCALAPPDATA%\DexAgents\logs\
Desktop Link:   %USERPROFILE%\Desktop\DexAgents Agent.lnk
```

## 🔐 Security Settings

### SSL Configuration
```json
{
  "verify_ssl": true,
  "ca_bundle_path": "C:\\certs\\ca-bundle.crt"
}
```

### Resource Limits
```json
{
  "enable_resource_limits": true,
  "max_cpu_percent": 25,
  "max_memory_mb": 256
}
```

## 📞 Getting Help

### Log Analysis
```
Look for these patterns:
- ERROR: Critical issues
- WARNING: Potential problems  
- Connection failed: Network issues
- Authentication failed: Token issues
```

### Support Information
```
When contacting support, provide:
1. Agent version (from GUI title)
2. Operating system version
3. Error messages from logs
4. Configuration (remove sensitive data)
5. Steps to reproduce issue
```

### Self-Help Checklist
- [ ] Agent service is running
- [ ] Configuration file is valid JSON
- [ ] Server URL is accessible
- [ ] API token is correct
- [ ] Firewall allows connections
- [ ] No antivirus blocking
- [ ] Log files show recent activity

## ⚡ Power User Tips

### Advanced Configuration
```json
{
  "update_interval": 30,
  "heartbeat_interval": 30,
  "connection_timeout": 10,
  "max_retries": 3,
  "log_level": "INFO"
}
```

### Performance Tuning
```json
{
  "low_resource_mode": {
    "update_interval": 60,
    "max_cpu_percent": 15,
    "max_memory_mb": 128,
    "log_level": "WARNING"
  }
}
```

### Automation
```powershell
# PowerShell: Restart agent
Restart-Service -Name "DexAgentsService"

# PowerShell: Check status
Get-Service -Name "DexAgentsService"

# PowerShell: Test connectivity
Test-NetConnection -ComputerName server -Port 8080
```

---

## 🔢 Version Information

**Current Version**: 3.0.0  
**Last Updated**: January 2024  
**Supported OS**: Windows 10/11, Server 2019/2022  
**Requirements**: .NET Framework 4.7.2+

---

*Keep this reference handy for quick DexAgents tasks!*