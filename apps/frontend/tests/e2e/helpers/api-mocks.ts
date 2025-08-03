import { Page } from '@playwright/test'

/**
 * Helper functions for mocking API responses in tests
 */
export class APIMocks {
  constructor(private page: Page) {}

  /**
   * Mock successful login response
   */
  async mockLogin(username = 'admin') {
    await this.page.route('**/api/v1/auth/login', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-jwt-token',
          token_type: 'bearer',
          user: {
            id: 1,
            username: username,
            email: `${username}@example.com`
          }
        })
      })
    })
  }

  /**
   * Mock failed login response
   */
  async mockLoginFailure() {
    await this.page.route('**/api/v1/auth/login', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Invalid username or password'
        })
      })
    })
  }

  /**
   * Mock user info response
   */
  async mockUserInfo(username = 'admin') {
    await this.page.route('**/api/v1/auth/me', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: username,
          email: `${username}@example.com`,
          is_active: true
        })
      })
    })
  }

  /**
   * Mock agents list response
   */
  async mockAgents(agents: any[] = []) {
    const defaultAgents = [
      {
        id: 1,
        hostname: 'TEST-PC-001',
        status: 'online',
        is_connected: true,
        last_seen: '2024-01-15T10:30:00Z',
        version: '1.0.0',
        platform: 'Windows 10',
        ip_address: '192.168.1.100'
      },
      {
        id: 2,
        hostname: 'TEST-PC-002',
        status: 'offline',
        is_connected: false,
        last_seen: '2024-01-15T09:15:00Z',
        version: '1.0.0',
        platform: 'Windows 11',
        ip_address: '192.168.1.101'
      }
    ]

    await this.page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(agents.length > 0 ? agents : defaultAgents)
      })
    })
  }

  /**
   * Mock empty agents list
   */
  async mockEmptyAgents() {
    await this.mockAgents([])
  }

  /**
   * Mock commands list response
   */
  async mockCommands(commands: any[] = []) {
    const defaultCommands = [
      {
        id: 1,
        name: 'Get System Info',
        command: 'Get-ComputerInfo | ConvertTo-Json',
        description: 'Retrieve detailed system information',
        category: 'System',
        created_at: '2024-01-15T10:00:00Z'
      },
      {
        id: 2,
        name: 'List Running Processes',
        command: 'Get-Process | Select-Object Name, CPU, WorkingSet | ConvertTo-Json',
        description: 'Get all currently running processes',
        category: 'Process',
        created_at: '2024-01-15T10:05:00Z'
      },
      {
        id: 3,
        name: 'Check Disk Space',
        command: 'Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, Size, FreeSpace | ConvertTo-Json',
        description: 'Check available disk space on all drives',
        category: 'System',
        created_at: '2024-01-15T10:10:00Z'
      }
    ]

    await this.page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(commands.length > 0 ? commands : defaultCommands)
      })
    })
  }

  /**
   * Mock empty commands list
   */
  async mockEmptyCommands() {
    await this.mockCommands([])
  }

  /**
   * Mock system health response
   */
  async mockSystemHealth(status = 'healthy') {
    await this.page.route('**/api/v1/system/health', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: status,
          timestamp: new Date().toISOString(),
          version: '1.0.0'
        })
      })
    })
  }

  /**
   * Mock system info response
   */
  async mockSystemInfo() {
    await this.page.route('**/api/v1/system/info', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          hostname: 'dexagents-server',
          cpu_usage: 25.5,
          memory_usage: 68.2,
          disk_usage: 45.0,
          uptime: 86400,
          platform: 'Linux',
          version: '1.0.0'
        })
      })
    })
  }

  /**
   * Mock command execution response
   */
  async mockCommandExecution(success = true) {
    await this.page.route('**/api/v1/commands/agent/*/execute', route => {
      if (success) {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Command sent successfully',
            execution_id: 'exec-' + Date.now()
          })
        })
      } else {
        route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Agent is not connected'
          })
        })
      }
    })
  }

  /**
   * Mock settings response
   */
  async mockSettings(settings: any[] = []) {
    const defaultSettings = [
      {
        id: 1,
        key: 'max_command_timeout',
        value: '300',
        description: 'Maximum command execution timeout in seconds'
      },
      {
        id: 2,
        key: 'auto_cleanup_logs',
        value: 'true',
        description: 'Automatically cleanup old log files'
      }
    ]

    await this.page.route('**/api/v1/settings', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(settings.length > 0 ? settings : defaultSettings)
      })
    })
  }

  /**
   * Mock API error responses
   */
  async mockAPIError(endpoint: string, status = 500, message = 'Internal server error') {
    await this.page.route(endpoint, route => {
      route.fulfill({
        status: status,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: message
        })
      })
    })
  }

  /**
   * Mock unauthorized response
   */
  async mockUnauthorized(endpoint: string) {
    await this.mockAPIError(endpoint, 401, 'Unauthorized')
  }

  /**
   * Clear all mocked routes
   */
  async clearMocks() {
    await this.page.unrouteAll()
  }
}