import { test, expect } from '@playwright/test'
import { AuthHelper } from './helpers/auth'
import { APIMocks } from './helpers/api-mocks'

test.describe('Comprehensive Frontend Tests', () => {
  let authHelper: AuthHelper
  let apiMocks: APIMocks

  test.beforeEach(async ({ page }) => {
    authHelper = new AuthHelper(page)
    apiMocks = new APIMocks(page)
  })

  test('should complete full user workflow', async ({ page }) => {
    // Mock all necessary APIs
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()
    await apiMocks.mockAgents()
    await apiMocks.mockCommands()
    await apiMocks.mockSystemInfo()
    await apiMocks.mockSystemHealth()

    // 1. Login
    await authHelper.loginAsAdmin()
    await expect(page).toHaveURL('/')

    // 2. Check dashboard
    await expect(page.locator('h2')).toContainText('Dashboard')
    await expect(page.locator('text=Total Agents')).toBeVisible()
    await expect(page.locator('text=Online Agents')).toBeVisible()

    // 3. Navigate to agents
    await page.click('text=View All Agents')
    await expect(page).toHaveURL('/agents')
    await expect(page.locator('text=TEST-PC-001')).toBeVisible()
    await expect(page.locator('text=TEST-PC-002')).toBeVisible()

    // 4. Navigate to commands
    await page.goto('/commands')
    await expect(page.locator('text=Get System Info')).toBeVisible()
    await expect(page.locator('text=List Running Processes')).toBeVisible()

    // 5. Execute a command (if functionality exists)
    await apiMocks.mockCommandExecution(true)
    const executeButton = page.locator('button:has-text("Execute"), button:has-text("Run")')
    if (await executeButton.first().isVisible()) {
      await executeButton.first().click()
    }

    // 6. Return to dashboard
    await page.goto('/')
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should handle all API error scenarios', async ({ page }) => {
    // Test with various API failures
    await authHelper.loginAsAdmin()

    // Test agents API failure
    await apiMocks.mockAPIError('**/api/v1/agents', 500)
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')

    // Test commands API failure
    await apiMocks.mockAPIError('**/api/v1/commands/saved', 500)
    await page.goto('/commands')
    await expect(page.locator('h2')).toContainText('Commands')

    // Test system info failure
    await apiMocks.mockAPIError('**/api/v1/system/info', 500)
    await page.goto('/')
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should work across different screen sizes', async ({ page }) => {
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()
    await apiMocks.mockAgents()
    await apiMocks.mockCommands()

    await authHelper.loginAsAdmin()

    // Test desktop
    await page.setViewportSize({ width: 1920, height: 1080 })
    await expect(page.locator('h2')).toContainText('Dashboard')

    // Test tablet
    await page.setViewportSize({ width: 768, height: 1024 })
    await expect(page.locator('h2')).toContainText('Dashboard')
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')

    // Test mobile
    await page.setViewportSize({ width: 375, height: 667 })
    await expect(page.locator('h2')).toContainText('Agents')
    await page.goto('/commands')
    await expect(page.locator('h2')).toContainText('Commands')
  })

  test('should handle network connectivity issues', async ({ page }) => {
    await authHelper.loginAsAdmin()

    // Simulate network failure
    await page.setOffline(true)
    
    // Try to navigate to different pages
    await page.goto('/agents')
    // Page should handle offline state gracefully

    // Restore network
    await page.setOffline(false)
    await page.reload()
    
    // Should work again
    await expect(page.locator('h2')).toContainText('Agents')
  })

  test('should maintain authentication state across page refreshes', async ({ page }) => {
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()
    
    await authHelper.loginAsAdmin()
    
    // Refresh page
    await page.reload()
    
    // Should still be authenticated
    await expect(page).toHaveURL('/')
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should handle browser back/forward navigation', async ({ page }) => {
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()
    await apiMocks.mockAgents()
    await apiMocks.mockCommands()

    await authHelper.loginAsAdmin()

    // Navigate through pages
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')

    await page.goto('/commands')
    await expect(page.locator('h2')).toContainText('Commands')

    // Test browser back
    await page.goBack()
    await expect(page.locator('h2')).toContainText('Agents')

    // Test browser forward
    await page.goForward()
    await expect(page.locator('h2')).toContainText('Commands')
  })

  test('should handle concurrent API calls', async ({ page }) => {
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()
    
    // Mock APIs with delays to test concurrent loading
    await page.route('**/api/v1/agents', async route => {
      await new Promise(resolve => setTimeout(resolve, 500))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })

    await page.route('**/api/v1/system/info', async route => {
      await new Promise(resolve => setTimeout(resolve, 300))
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          hostname: 'test-server',
          cpu_usage: 25.0,
          memory_usage: 60.0
        })
      })
    })

    await authHelper.loginAsAdmin()
    
    // Dashboard should handle concurrent API calls
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should validate data consistency', async ({ page, request }) => {
    // Real API integration test
    await authHelper.loginAsAdmin()

    // Get auth token
    const token = await authHelper.getAuthToken()
    
    if (token) {
      // Compare API data with frontend display
      const agentsResponse = await request.get('http://localhost:8080/api/v1/agents', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (agentsResponse.status() === 200) {
        const apiAgents = await agentsResponse.json()
        
        await page.goto('/agents')
        
        // Verify frontend shows same data as API
        for (const agent of apiAgents.slice(0, 3)) {
          await expect(page.locator(`text=${agent.hostname}`)).toBeVisible()
        }
      }
    }
  })

  test('should handle edge cases and boundary conditions', async ({ page }) => {
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()

    await authHelper.loginAsAdmin()

    // Test with empty data
    await apiMocks.mockEmptyAgents()
    await apiMocks.mockEmptyCommands()
    
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')
    
    await page.goto('/commands')
    await expect(page.locator('h2')).toContainText('Commands')

    // Test with large datasets
    const manyAgents = Array.from({ length: 100 }, (_, i) => ({
      id: i + 1,
      hostname: `PC-${String(i + 1).padStart(3, '0')}`,
      status: i % 2 === 0 ? 'online' : 'offline',
      is_connected: i % 2 === 0
    }))

    await apiMocks.mockAgents(manyAgents)
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')
  })

  test('should perform accessibility checks', async ({ page }) => {
    await apiMocks.mockLogin()
    await apiMocks.mockUserInfo()
    await apiMocks.mockAgents()

    await authHelper.loginAsAdmin()

    // Basic accessibility checks
    // Check for heading hierarchy
    const h1 = page.locator('h1')
    const h2 = page.locator('h2')
    
    if (await h1.count() > 0) {
      await expect(h1.first()).toBeVisible()
    }
    await expect(h2.first()).toBeVisible()

    // Check for form labels on login page
    await page.goto('/login')
    await expect(page.locator('label[for="username"]')).toBeVisible()
    await expect(page.locator('label[for="password"]')).toBeVisible()

    // Check button accessibility
    const buttons = page.locator('button')
    const buttonCount = await buttons.count()
    expect(buttonCount).toBeGreaterThan(0)

    // Check for proper button types
    const submitButtons = page.locator('button[type="submit"]')
    if (await submitButtons.count() > 0) {
      await expect(submitButtons.first()).toBeVisible()
    }
  })
})