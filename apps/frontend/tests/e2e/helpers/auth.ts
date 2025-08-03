import { Page, expect } from '@playwright/test'

/**
 * Helper functions for authentication in tests
 */
export class AuthHelper {
  constructor(private page: Page) {}

  /**
   * Login with admin credentials
   */
  async loginAsAdmin() {
    await this.page.goto('/login')
    await this.page.fill('input[name="username"]', 'admin')
    await this.page.fill('input[name="password"]', 'admin123')
    await this.page.click('button[type="submit"]')
    
    // Wait for successful login
    await expect(this.page).toHaveURL('/')
    await expect(this.page.locator('h2')).toContainText('Dashboard')
  }

  /**
   * Login with custom credentials
   */
  async login(username: string, password: string) {
    await this.page.goto('/login')
    await this.page.fill('input[name="username"]', username)
    await this.page.fill('input[name="password"]', password)
    await this.page.click('button[type="submit"]')
  }

  /**
   * Check if user is logged in
   */
  async isLoggedIn(): Promise<boolean> {
    try {
      await this.page.goto('/')
      await expect(this.page.locator('h2')).toContainText('Dashboard')
      return true
    } catch {
      return false
    }
  }

  /**
   * Logout user (if logout functionality exists)
   */
  async logout() {
    // Look for logout button or menu
    const logoutButton = this.page.locator('button:has-text("Logout"), button:has-text("Sign out"), [data-testid="logout"]')
    
    if (await logoutButton.isVisible()) {
      await logoutButton.click()
      await expect(this.page).toHaveURL('/login')
    } else {
      // Fallback: clear storage and navigate to login
      await this.page.evaluate(() => {
        localStorage.clear()
        sessionStorage.clear()
      })
      await this.page.goto('/login')
    }
  }

  /**
   * Get auth token from browser storage
   */
  async getAuthToken(): Promise<string | null> {
    return await this.page.evaluate(() => {
      return localStorage.getItem('authToken') || 
             localStorage.getItem('token') ||
             sessionStorage.getItem('authToken') || 
             sessionStorage.getItem('token')
    })
  }
}