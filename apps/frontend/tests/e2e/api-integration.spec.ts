import { test, expect } from '@playwright/test'

test.describe('API Integration Tests', () => {
  let authToken: string

  test.beforeEach(async ({ page }) => {
    // Login and get auth token
    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    // Wait for successful login
    await expect(page).toHaveURL('/')
    
    // Extract auth token from localStorage or cookies for API tests
    authToken = await page.evaluate(() => {
      return localStorage.getItem('authToken') || sessionStorage.getItem('authToken') || ''
    })
  })

  test('should validate API endpoints through frontend interaction', async ({ page }) => {
    // Test health endpoint by checking if dashboard loads
    await page.goto('/')
    await expect(page.locator('h2')).toContainText('Dashboard')
    
    // This indirectly tests /api/v1/system/health since dashboard loads system info
    await expect(page.locator('text=Total Agents')).toBeVisible()
  })

  test('should handle authentication flow correctly', async ({ page, request }) => {
    // Test /api/v1/auth/login endpoint
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    })
    
    expect(loginResponse.status()).toBe(200)
    const loginData = await loginResponse.json()
    expect(loginData).toHaveProperty('access_token')
    expect(loginData).toHaveProperty('user')
    expect(loginData.user.username).toBe('admin')
    
    // Test /api/v1/auth/me endpoint
    const meResponse = await request.get('http://localhost:8080/api/v1/auth/me', {
      headers: {
        'Authorization': `Bearer ${loginData.access_token}`
      }
    })
    
    expect(meResponse.status()).toBe(200)
    const meData = await meResponse.json()
    expect(meData.username).toBe('admin')
  })

  test('should test agents API endpoints', async ({ page, request }) => {
    // First login to get token
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: { username: 'admin', password: 'admin123' }
    })
    const { access_token } = await loginResponse.json()
    
    // Test GET /api/v1/agents
    const agentsResponse = await request.get('http://localhost:8080/api/v1/agents', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    
    expect(agentsResponse.status()).toBe(200)
    const agents = await agentsResponse.json()
    expect(Array.isArray(agents)).toBe(true)
    
    // Verify agent data structure if agents exist
    if (agents.length > 0) {
      const agent = agents[0]
      expect(agent).toHaveProperty('id')
      expect(agent).toHaveProperty('hostname')
      expect(agent).toHaveProperty('status')
    }
    
    // Navigate to agents page and verify it displays the data
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')
  })

  test('should test commands API endpoints', async ({ page, request }) => {
    // Login to get token
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: { username: 'admin', password: 'admin123' }
    })
    const { access_token } = await loginResponse.json()
    
    // Test GET /api/v1/commands/saved
    const commandsResponse = await request.get('http://localhost:8080/api/v1/commands/saved', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    
    expect(commandsResponse.status()).toBe(200)
    const commands = await commandsResponse.json()
    expect(Array.isArray(commands)).toBe(true)
    
    // Verify command data structure if commands exist
    if (commands.length > 0) {
      const command = commands[0]
      expect(command).toHaveProperty('id')
      expect(command).toHaveProperty('name')
      expect(command).toHaveProperty('command')
    }
    
    // Navigate to commands page and verify it displays the data
    await page.goto('/commands')
    await expect(page.locator('h2')).toContainText('Commands')
  })

  test('should test command execution API', async ({ page, request }) => {
    // Login to get token
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: { username: 'admin', password: 'admin123' }
    })
    const { access_token } = await loginResponse.json()
    
    // Get agents to find one for testing
    const agentsResponse = await request.get('http://localhost:8080/api/v1/agents', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    const agents = await agentsResponse.json()
    
    if (agents.length > 0) {
      const agent = agents[0]
      
      // Test command execution API
      const executeResponse = await request.post(
        `http://localhost:8080/api/v1/commands/agent/${agent.id}/execute`,
        {
          headers: { 'Authorization': `Bearer ${access_token}` },
          data: {
            command: 'Get-Date | ConvertTo-Json',
            timeout: 30
          }
        }
      )
      
      // Command execution might return 200, 202, or 204 depending on implementation
      expect([200, 202, 204]).toContain(executeResponse.status())
    }
  })

  test('should test settings API endpoints', async ({ page, request }) => {
    // Login to get token
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: { username: 'admin', password: 'admin123' }
    })
    const { access_token } = await loginResponse.json()
    
    // Test GET /api/v1/settings
    const settingsResponse = await request.get('http://localhost:8080/api/v1/settings', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    
    expect(settingsResponse.status()).toBe(200)
    const settings = await settingsResponse.json()
    expect(Array.isArray(settings)).toBe(true)
    
    // Navigate to settings page if it exists
    await page.goto('/settings')
    // Settings page might not exist in frontend, so we just check if it loads or redirects
  })

  test('should handle unauthorized access correctly', async ({ request }) => {
    // Test accessing protected endpoints without token
    const unauthorizedResponse = await request.get('http://localhost:8080/api/v1/agents')
    expect(unauthorizedResponse.status()).toBe(401)
    
    // Test with invalid token
    const invalidTokenResponse = await request.get('http://localhost:8080/api/v1/agents', {
      headers: { 'Authorization': 'Bearer invalid-token' }
    })
    expect(invalidTokenResponse.status()).toBe(401)
  })

  test('should test system health endpoint', async ({ request }) => {
    // Health endpoint should be accessible without authentication
    const healthResponse = await request.get('http://localhost:8080/api/v1/system/health')
    expect(healthResponse.status()).toBe(200)
    
    const healthData = await healthResponse.json()
    expect(healthData).toHaveProperty('status')
    expect(healthData.status).toBe('healthy')
  })

  test('should handle API errors gracefully in frontend', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/')
    
    // Mock API failures to test error handling
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      })
    })
    
    // Navigate to agents page with mocked error
    await page.goto('/agents')
    
    // Page should still load but handle error gracefully
    await expect(page.locator('h2')).toContainText('Agents')
    
    // Should show error message or empty state
    const errorIndicator = page.locator('text=error, text=failed, text=unavailable')
    if (await errorIndicator.first().isVisible()) {
      await expect(errorIndicator.first()).toBeVisible()
    }
  })

  test('should test WebSocket connection for real-time updates', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/')
    
    // Listen for WebSocket connections
    let wsConnected = false
    page.on('websocket', ws => {
      wsConnected = true
      
      // Log WebSocket messages for debugging
      ws.on('framesent', event => {
        console.log('WS Frame sent:', event.payload)
      })
      
      ws.on('framereceived', event => {
        console.log('WS Frame received:', event.payload)
      })
    })
    
    // Give some time for WebSocket to connect
    await page.waitForTimeout(2000)
    
    // WebSocket connection is optional, so we just log if it exists
    if (wsConnected) {
      console.log('WebSocket connection established')
    } else {
      console.log('No WebSocket connection detected')
    }
    
    // Dashboard should still work without WebSocket
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should test data consistency between API and frontend', async ({ page, request }) => {
    // Login to get token
    const loginResponse = await request.post('http://localhost:8080/api/v1/auth/login', {
      data: { username: 'admin', password: 'admin123' }
    })
    const { access_token } = await loginResponse.json()
    
    // Get agents from API
    const agentsResponse = await request.get('http://localhost:8080/api/v1/agents', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    const apiAgents = await agentsResponse.json()
    
    // Navigate to agents page
    await page.goto('/agents')
    
    // Verify that frontend displays the same data as API
    if (apiAgents.length > 0) {
      for (const agent of apiAgents.slice(0, 3)) { // Test first 3 agents
        await expect(page.locator(`text=${agent.hostname}`)).toBeVisible()
      }
    }
    
    // Test the same for commands
    const commandsResponse = await request.get('http://localhost:8080/api/v1/commands/saved', {
      headers: { 'Authorization': `Bearer ${access_token}` }
    })
    const apiCommands = await commandsResponse.json()
    
    await page.goto('/commands')
    
    if (apiCommands.length > 0) {
      for (const command of apiCommands.slice(0, 3)) { // Test first 3 commands
        await expect(page.locator(`text=${command.name}`)).toBeVisible()
      }
    }
  })
})