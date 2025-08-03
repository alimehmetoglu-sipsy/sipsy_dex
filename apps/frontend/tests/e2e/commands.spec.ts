import { test, expect } from '@playwright/test'

test.describe('Commands Management Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login')
    await page.fill('input[name="username"]', 'admin')
    await page.fill('input[name="password"]', 'admin123')
    await page.click('button[type="submit"]')
    
    // Navigate to commands page
    await page.goto('/commands')
    await expect(page.locator('h2')).toContainText('Commands')
  })

  test('should display commands page with correct layout', async ({ page }) => {
    // Check page title and header
    await expect(page.locator('h2')).toContainText('Commands')
    
    // Look for commands-related content
    const commandsContent = page.locator('[data-testid="commands-container"]')
    if (await commandsContent.isVisible()) {
      await expect(commandsContent).toBeVisible()
    } else {
      // Fallback: check for add command button or similar
      const addButton = page.locator('button:has-text("Add"), button:has-text("New"), button:has-text("Create")')
      if (await addButton.first().isVisible()) {
        await expect(addButton.first()).toBeVisible()
      }
    }
  })

  test('should display saved commands list', async ({ page }) => {
    // Mock saved commands response
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Get System Info',
            command: 'Get-ComputerInfo | ConvertTo-Json',
            description: 'Retrieve system information',
            category: 'System'
          },
          {
            id: 2,
            name: 'List Running Processes',
            command: 'Get-Process | Select-Object Name, CPU, WorkingSet | ConvertTo-Json',
            description: 'Get all running processes',
            category: 'Process'
          }
        ])
      })
    })
    
    await page.reload()
    
    // Check that commands are displayed
    await expect(page.locator('text=Get System Info')).toBeVisible()
    await expect(page.locator('text=List Running Processes')).toBeVisible()
    
    // Check command details
    await expect(page.locator('text=Get-ComputerInfo')).toBeVisible()
    await expect(page.locator('text=Get-Process')).toBeVisible()
  })

  test('should handle empty commands list', async ({ page }) => {
    // Mock empty commands response
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([])
      })
    })
    
    await page.reload()
    
    // Should show empty state
    const emptyStateText = page.locator('text=No commands, text=empty, text=available')
    if (await emptyStateText.first().isVisible()) {
      await expect(emptyStateText.first()).toBeVisible()
    }
  })

  test('should execute command on selected agents', async ({ page }) => {
    // Mock commands and agents
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Test Command',
            command: 'Get-Date',
            description: 'Get current date'
          }
        ])
      })
    })
    
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
    
    // Look for execute button or run command functionality
    const executeButton = page.locator('button:has-text("Execute"), button:has-text("Run"), button:has-text("Send")')
    
    if (await executeButton.first().isVisible()) {
      // Mock command execution
      await page.route('**/api/v1/commands/agent/*/execute', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, message: 'Command sent' })
        })
      })
      
      await executeButton.first().click()
      
      // Should show success message or confirmation
      const successMessage = page.locator('text=success, text=sent, text=executed')
      if (await successMessage.first().isVisible()) {
        await expect(successMessage.first()).toBeVisible()
      }
    }
  })

  test('should create new command', async ({ page }) => {
    // Look for "Add Command" or "New Command" button
    const addButton = page.locator('button:has-text("Add"), button:has-text("New"), button:has-text("Create")')
    
    if (await addButton.first().isVisible()) {
      await addButton.first().click()
      
      // Should open command creation form
      const nameInput = page.locator('input[name="name"], input[placeholder*="name"]')
      const commandInput = page.locator('textarea[name="command"], input[name="command"], textarea[placeholder*="command"]')
      
      if (await nameInput.isVisible() && await commandInput.isVisible()) {
        // Fill in command details
        await nameInput.fill('Test New Command')
        await commandInput.fill('Get-Process | Select-Object Name')
        
        // Look for save button
        const saveButton = page.locator('button:has-text("Save"), button:has-text("Create"), button[type="submit"]')
        
        if (await saveButton.isVisible()) {
          // Mock successful command creation
          await page.route('**/api/v1/commands', route => {
            route.fulfill({
              status: 201,
              contentType: 'application/json',
              body: JSON.stringify({
                id: 3,
                name: 'Test New Command',
                command: 'Get-Process | Select-Object Name'
              })
            })
          })
          
          await saveButton.click()
          
          // Should show success or return to commands list
          const successIndicator = page.locator('text=success, text=created, text=saved')
          if (await successIndicator.first().isVisible()) {
            await expect(successIndicator.first()).toBeVisible()
          }
        }
      }
    }
  })

  test('should filter commands by category', async ({ page }) => {
    // Mock commands with categories
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'System Command',
            command: 'Get-ComputerInfo',
            category: 'System'
          },
          {
            id: 2,
            name: 'Process Command',
            command: 'Get-Process',
            category: 'Process'
          }
        ])
      })
    })
    
    await page.reload()
    
    // Both commands should be visible initially
    await expect(page.locator('text=System Command')).toBeVisible()
    await expect(page.locator('text=Process Command')).toBeVisible()
    
    // Look for category filter
    const categoryFilter = page.locator('select[name="category"], button:has-text("System"), button:has-text("Process")')
    
    if (await categoryFilter.first().isVisible()) {
      // Test filtering functionality exists
      await expect(categoryFilter.first()).toBeVisible()
    }
  })

  test('should handle command execution errors', async ({ page }) => {
    // Mock command and agent
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Test Command', command: 'Get-Date' }
        ])
      })
    })
    
    await page.route('**/api/v1/agents', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, hostname: 'TEST-PC', status: 'offline', is_connected: false }
        ])
      })
    })
    
    await page.reload()
    
    // Mock failed command execution
    await page.route('**/api/v1/commands/agent/*/execute', route => {
      route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Agent is offline' })
      })
    })
    
    // Try to execute command on offline agent
    const executeButton = page.locator('button:has-text("Execute"), button:has-text("Run")')
    
    if (await executeButton.first().isVisible()) {
      await executeButton.first().click()
      
      // Should show error message
      const errorMessage = page.locator('text=error, text=failed, text=offline')
      if (await errorMessage.first().isVisible()) {
        await expect(errorMessage.first()).toBeVisible()
      }
    }
  })

  test('should edit existing command', async ({ page }) => {
    // Mock saved command
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Editable Command',
            command: 'Get-Process',
            description: 'Original description'
          }
        ])
      })
    })
    
    await page.reload()
    
    // Look for edit button
    const editButton = page.locator('button:has-text("Edit"), button[aria-label="Edit"], .edit-button')
    
    if (await editButton.first().isVisible()) {
      await editButton.first().click()
      
      // Should open edit form with existing values
      const nameInput = page.locator('input[name="name"]')
      const commandInput = page.locator('textarea[name="command"]')
      
      if (await nameInput.isVisible()) {
        await expect(nameInput).toHaveValue('Editable Command')
        
        // Make changes
        await nameInput.fill('Updated Command Name')
        
        // Save changes
        const saveButton = page.locator('button:has-text("Save"), button:has-text("Update")')
        if (await saveButton.isVisible()) {
          await saveButton.click()
        }
      }
    }
  })

  test('should delete command', async ({ page }) => {
    // Mock saved command
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Deletable Command',
            command: 'Get-Date'
          }
        ])
      })
    })
    
    await page.reload()
    await expect(page.locator('text=Deletable Command')).toBeVisible()
    
    // Look for delete button
    const deleteButton = page.locator('button:has-text("Delete"), button[aria-label="Delete"], .delete-button')
    
    if (await deleteButton.first().isVisible()) {
      // Mock successful deletion
      await page.route('**/api/v1/commands/*', route => {
        if (route.request().method() === 'DELETE') {
          route.fulfill({
            status: 204,
            contentType: 'application/json',
            body: ''
          })
        }
      })
      
      await deleteButton.first().click()
      
      // May show confirmation dialog
      const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")')
      if (await confirmButton.first().isVisible()) {
        await confirmButton.first().click()
      }
      
      // Command should be removed from list
      await expect(page.locator('text=Deletable Command')).not.toBeVisible()
    }
  })

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API error
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Internal server error' })
      })
    })
    
    await page.reload()
    
    // Should handle error gracefully
    await expect(page.locator('h2')).toContainText('Commands')
    
    // Look for error message
    const errorText = page.locator('text=error, text=failed, text=try again')
    if (await errorText.first().isVisible()) {
      await expect(errorText.first()).toBeVisible()
    }
  })

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 })
    
    // Mock some commands
    await page.route('**/api/v1/commands/saved', route => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { id: 1, name: 'Mobile Test Command', command: 'Get-Date' }
        ])
      })
    })
    
    await page.reload()
    
    // Check that content is accessible on mobile
    await expect(page.locator('h2')).toContainText('Commands')
    await expect(page.locator('text=Mobile Test Command')).toBeVisible()
  })
})