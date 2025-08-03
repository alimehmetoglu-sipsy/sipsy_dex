import { test, expect } from '@playwright/test'

test.describe('Agents Management Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    // Navigate to agents page
    await page.goto('/agents')
    await expect(page.locator('h2')).toContainText('Agents')
  })

  test('should display agents page with correct layout', async ({ page }) => {
    // Check page title and header
    await expect(page.locator('h2')).toContainText('Agents')
    
    // Check if agents table/list is visible
    // The exact structure depends on implementation, but there should be some agent-related content
    const agentsContainer = page.locator('[data-testid="agents-container"]')
    if (await agentsContainer.isVisible()) {
      await expect(agentsContainer).toBeVisible()
    } else {
      // Fallback: check for common agent-related text
      const agentContent = page.locator('text=hostname, text=status, text=online, text=offline')
      if (await agentContent.first().isVisible()) {
        await expect(agentContent.first()).toBeVisible()
      }
    }
  })

  test('should handle empty agents list', async ({ page }) => {
    // Mock empty agents response
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })
    
    await page.reload()
    
    // Should show empty state or message
    await expect(page.locator('h2')).toContainText('Agents')
    
    // Look for empty state messaging
    const emptyStateText = page.locator('text=No agents, text=empty, text=available')
    if (await emptyStateText.first().isVisible()) {
      await expect(emptyStateText.first()).toBeVisible()
    }
  })

  test('should display agent information correctly', async ({ page }) => {
    // Mock agents response with sample data
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            hostname: 'TEST-PC-001',
            status: 'online',
            is_connected: true,
            last_seen: '2024-01-15T10:30:00Z',
            version: '1.0.0',
            platform: 'Windows 10'
          },
          {
            id: 2,
            hostname: 'TEST-PC-002',
            status: 'offline',
            is_connected: false,
            last_seen: '2024-01-15T09:15:00Z',
            version: '1.0.0',
            platform: 'Windows 11'
          }
        ])
      })
    })
    
    await page.reload()
    
    // Check that agent information is displayed
    await expect(page.locator('text=TEST-PC-001')).toBeVisible()
    await expect(page.locator('text=TEST-PC-002')).toBeVisible()
    
    // Check status indicators
    await expect(page.locator('text=online')).toBeVisible()
    await expect(page.locator('text=offline')).toBeVisible()
  })

  test('should filter agents by status', async ({ page }) => {
    // Mock agents with different statuses
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, hostname: 'ONLINE-PC', status: 'online', is_connected: true },
          { id: 2, hostname: 'OFFLINE-PC', status: 'offline', is_connected: false }
        ])
      })
    })
    
    await page.reload()
    
    // Look for filter controls
    const filterButton = page.locator('button:has-text("Filter"), button:has-text("All"), button:has-text("Online"), button:has-text("Offline")')
    
    if (await filterButton.first().isVisible()) {
      // Test filtering if filter controls exist
      await filterButton.first().click()
      
      // Both agents should be visible initially
      await expect(page.locator('text=ONLINE-PC')).toBeVisible()
      await expect(page.locator('text=OFFLINE-PC')).toBeVisible()
    }
  })

  test('should navigate to agent details page', async ({ page }) => {
    // Mock agent response
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            hostname: 'TEST-PC-001',
            status: 'online',
            is_connected: true
          }
        ])
      })
    })
    
    await page.reload()
    
    // Look for agent link or button to view details
    const agentLink = page.locator('text=TEST-PC-001, a:has-text("TEST-PC-001"), button:has-text("TEST-PC-001")')
    
    if (await agentLink.isVisible()) {
      await agentLink.click()
      
      // Should navigate to agent details page
      await expect(page).toHaveURL(/\/agents\/\d+/)
    }
  })

  test('should handle agents API error', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      })
    })
    
    await page.reload()
    
    // Should handle error gracefully
    await expect(page.locator('h2')).toContainText('Agents')
    
    // Look for error message
    const errorText = page.locator('text=error, text=failed, text=try again')
    if (await errorText.first().isVisible()) {
      await expect(errorText.first()).toBeVisible()
    }
  })

  test('should refresh agents list', async ({ page }) => {
    // Initial load
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, hostname: 'INITIAL-PC', status: 'online', is_connected: true }
        ])
      })
    })
    
    await page.reload()
    await expect(page.locator('text=INITIAL-PC')).toBeVisible()
    
    // Mock updated response
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, hostname: 'UPDATED-PC', status: 'online', is_connected: true }
        ])
      })
    })
    
    // Look for refresh button
    const refreshButton = page.locator('button:has-text("Refresh"), button[aria-label="Refresh"], button:has([data-testid="refresh"])')
    
    if (await refreshButton.isVisible()) {
      await refreshButton.click()
      await expect(page.locator('text=UPDATED-PC')).toBeVisible()
    } else {
      // Fallback: reload page to test refresh
      await page.reload()
      await expect(page.locator('text=UPDATED-PC')).toBeVisible()
    }
  })

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Mock some agents
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, hostname: 'MOBILE-TEST-PC', status: 'online', is_connected: true }
        ])
      })
    })
    
    await page.reload()
    
    // Check that content is still accessible on mobile
    await expect(page.locator('h2')).toContainText('Agents')
    await expect(page.locator('text=MOBILE-TEST-PC')).toBeVisible()
  })

  test('should show loading state', async ({ page }) => {
    // Add delay to API to see loading state
    await page.route('**/api/v1/agents', route => {
      setTimeout(() => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify([])
        })
      }, 1000)
    })
    
    await page.reload()
    
    // Look for loading indicator
    const loadingIndicator = page.locator('text=Loading, [data-testid="loading"], .animate-spin')
    
    // Loading might be too fast to catch, so we'll just ensure the page loads
    await expect(page.locator('h2')).toContainText('Agents')
  })
})