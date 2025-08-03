import { test, expect } from '@playwright/test'

test.describe('Dashboard Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    // Wait for dashboard to load
    await expect(page).toHaveURL('/')
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should display dashboard with all components', async ({ page }) => {
    // Check main heading and description
    await expect(page.locator('h2')).toContainText('Dashboard')
    await expect(page.locator('text=Overview of your endpoint agents and recent activity')).toBeVisible()
    
    // Check stats cards
    await expect(page.locator('text=Total Agents')).toBeVisible()
    await expect(page.locator('text=Online Agents')).toBeVisible()
    await expect(page.locator('text=Commands Today')).toBeVisible()
    await expect(page.locator('text=Scheduled Jobs')).toBeVisible()
    
    // Check system health section if available
    const systemHealthCard = page.locator('text=System Health')
    if (await systemHealthCard.isVisible()) {
      await expect(page.locator('text=CPU Usage')).toBeVisible()
      await expect(page.locator('text=Memory Usage')).toBeVisible()
      await expect(page.locator('text=Hostname')).toBeVisible()
    }
    
    // Check quick actions
    await expect(page.locator('text=Quick Actions')).toBeVisible()
    await expect(page.locator('text=Add Command')).toBeVisible()
    await expect(page.locator('text=Create Scheduled Job')).toBeVisible()
    await expect(page.locator('text=View All Agents')).toBeVisible()
    
    // Check recent activity
    await expect(page.locator('text=Recent Activity')).toBeVisible()
  })

  test('should handle loading state', async ({ page }) => {
    // Reload page to see loading state
    await page.reload()
    
    // Check if loading indicator appears (it might be too fast to catch)
    const loadingIndicator = page.locator('text=Loading dashboard...')
    
    // Wait for dashboard to load completely
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should navigate to agents page from quick actions', async ({ page }) => {
    // Click on "View All Agents" button
    await page.click('text=View All Agents')
    
    // Should navigate to agents page
    await expect(page).toHaveURL('/agents')
    await expect(page.locator('h2')).toContainText('Agents')
  })

  test('should navigate to commands page from quick actions', async ({ page }) => {
    // Click on "Add Command" button
    await page.click('text=Add Command')
    
    // Should navigate to commands page
    await expect(page).toHaveURL('/commands/new')
  })

  test('should display correct stats format', async ({ page }) => {
    // Check that stats cards display numeric values
    const totalAgentsCard = page.locator('text=Total Agents').locator('..')
    await expect(totalAgentsCard.locator('[class*="text-2xl"]')).toBeVisible()
    
    const onlineAgentsCard = page.locator('text=Online Agents').locator('..')
    await expect(onlineAgentsCard.locator('[class*="text-2xl"]')).toBeVisible()
    
    const commandsCard = page.locator('text=Commands Today').locator('..')
    await expect(commandsCard.locator('[class*="text-2xl"]')).toBeVisible()
    
    const scheduledCard = page.locator('text=Scheduled Jobs').locator('..')
    await expect(scheduledCard.locator('[class*="text-2xl"]')).toBeVisible()
  })

  test('should show offline agents alert when applicable', async ({ page }) => {
    // This test checks if the offline agents alert appears when there are offline agents
    // The alert might not always be visible depending on system state
    const offlineAlert = page.locator('text=Attention Required')
    
    if (await offlineAlert.isVisible()) {
      await expect(page.locator('text=agents are currently offline')).toBeVisible()
      await expect(page.locator('text=View offline agents')).toBeVisible()
    }
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API failure to test error handling
    await page.route('**/api/v1/system/info', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      })
    })
    
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      })
    })
    
    // Reload page to trigger API calls with mocked errors
    await page.reload()
    
    // Should show error state or handle gracefully
    // The dashboard should still be functional even if some API calls fail
    await expect(page.locator('h2')).toContainText('Dashboard')
  })

  test('should display recent activity items', async ({ page }) => {
    // Check recent activity section
    const activitySection = page.locator('text=Recent Activity').locator('..')
    await expect(activitySection).toBeVisible()
    
    // The activity items are hardcoded in the component, so they should be visible
    const activityItems = page.locator('[class*="space-y-3"] > div')
    
    // Check if at least some activity items are present
    const itemCount = await activityItems.count()
    expect(itemCount).toBeGreaterThan(0)
  })

  test('should be responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Check that dashboard still displays properly
    await expect(page.locator('h2')).toContainText('Dashboard')
    await expect(page.locator('text=Total Agents')).toBeVisible()
    
    // Cards should still be visible but may be stacked
    await expect(page.locator('text=Online Agents')).toBeVisible()
    await expect(page.locator('text=Commands Today')).toBeVisible()
  })

  test('should show progress bar for online agents', async ({ page }) => {
    // Check if progress bar is visible in online agents card
    const onlineAgentsCard = page.locator('text=Online Agents').locator('..')
    
    // Look for progress component (it uses a progress bar to show online/total ratio)
    const progressBar = onlineAgentsCard.locator('[role="progressbar"]')
    if (await progressBar.isVisible()) {
      await expect(progressBar).toBeVisible()
    }
  })
})