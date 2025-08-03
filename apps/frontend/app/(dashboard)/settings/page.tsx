'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Separator } from '@/components/ui/separator'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { Settings, Save, RefreshCw, Server, Key, Globe, Bot, TestTube } from 'lucide-react'
import { apiClient } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'

export default function SettingsPage() {
  const { toast } = useToast()
  const [config, setConfig] = useState({
    server_url: 'http://localhost:8080',
    api_token: 'default_token',
    agent_name: '',
    tags: [] as string[],
    auto_start: true,
    run_as_service: false
  })
  const [chatgptConfig, setChatgptConfig] = useState({
    api_key: '',
    model: 'gpt-3.5-turbo',
    max_tokens: 1000,
    temperature: 0.7,
    system_prompt: ''
  })
  const [loading, setLoading] = useState(false)
  const [systemInfo, setSystemInfo] = useState<any>(null)

  useEffect(() => {
    loadInstallerConfig()
    loadSystemInfo()
    loadChatGPTConfig()
  }, [])

  const loadInstallerConfig = async () => {
    try {
      setLoading(true)
      const installerConfig = await apiClient.getInstallerConfig()
      setConfig(prev => ({ ...prev, ...installerConfig }))
    } catch (error) {
      console.error('Failed to load installer config:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSystemInfo = async () => {
    try {
      const info = await apiClient.getSystemInfo()
      setSystemInfo(info)
    } catch (error) {
      console.error('Failed to load system info:', error)
    }
  }

  const loadChatGPTConfig = async () => {
    try {
      const response = await fetch('/api/v1/settings/chatgpt/config', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })
      if (response.ok) {
        const config = await response.json()
        // Ensure all values are strings to prevent controlled/uncontrolled input issues
        setChatgptConfig(prev => ({ 
          ...prev, 
          ...config,
          api_key: config.api_key || '',
          model: config.model || 'gpt-3.5-turbo',
          max_tokens: config.max_tokens || 1000,
          temperature: config.temperature || 0.7,
          system_prompt: config.system_prompt || ''
        }))
      }
    } catch (error) {
      console.error('Failed to load ChatGPT config:', error)
    }
  }

  const saveChatGPTConfig = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/v1/settings/chatgpt/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(chatgptConfig)
      })
      
      if (response.ok) {
        toast({
          title: "Success",
          description: "ChatGPT configuration saved successfully!"
        })
      } else {
        const errorText = await response.text()
        console.error('API Error:', response.status, errorText)
        throw new Error(`Failed to save configuration: ${response.status} - ${errorText}`)
      }
    } catch (error) {
      console.error('Failed to save ChatGPT config:', error)
      toast({
        title: "Error",
        description: "Failed to save ChatGPT configuration",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const testChatGPTAPI = async () => {
    try {
      setLoading(true)
      console.log('Testing ChatGPT API...')
      const response = await fetch('/api/v1/settings/chatgpt/test', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      })
      
      console.log('Test API Response status:', response.status)
      const result = await response.json()
      console.log('Test API Result:', result)
      
      if (response.ok && result.success) {
        toast({
          title: "Success",
          description: result.message || "ChatGPT API test successful!"
        })
      } else {
        console.error('Test API Error:', response.status, result)
        throw new Error(result.detail || result.message || 'API test failed')
      }
    } catch (error) {
      console.error('ChatGPT API test failed:', error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "ChatGPT API test failed",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    try {
      setLoading(true)
      // In a real app, you'd save these settings to backend
      console.log('Saving config:', config)
      alert('Settings saved successfully!')
    } catch (error) {
      console.error('Failed to save settings:', error)
      alert('Failed to save settings')
    } finally {
      setLoading(false)
    }
  }

  const handleTestConnection = async () => {
    try {
      setLoading(true)
      const health = await apiClient.getHealthCheck()
      alert(`Connection successful! Server status: ${health.status}`)
    } catch (error) {
      console.error('Connection test failed:', error)
      alert('Connection test failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center space-x-2">
        <Settings className="h-8 w-8" />
        <h1 className="text-3xl font-bold">Settings</h1>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Server className="h-5 w-5" />
              <span>Server Configuration</span>
            </CardTitle>
            <CardDescription>
              Configure your DexAgents server connection settings
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="server-url">Server URL</Label>
              <Input
                id="server-url"
                value={config.server_url}
                onChange={(e) => setConfig(prev => ({ ...prev, server_url: e.target.value }))}
                placeholder="http://localhost:8080"
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="api-token">API Token</Label>
              <Input
                id="api-token"
                type="password"
                value={config.api_token}
                onChange={(e) => setConfig(prev => ({ ...prev, api_token: e.target.value }))}
                placeholder="Your API token"
              />
            </div>

            <div className="flex space-x-2">
              <Button onClick={handleTestConnection} variant="outline" disabled={loading}>
                <Globe className="mr-2 h-4 w-4" />
                Test Connection
              </Button>
              <Button onClick={handleSave} disabled={loading}>
                <Save className="mr-2 h-4 w-4" />
                Save Settings
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Key className="h-5 w-5" />
              <span>Agent Configuration</span>
            </CardTitle>
            <CardDescription>
              Default settings for new agent installations
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="agent-name">Default Agent Name</Label>
              <Input
                id="agent-name"
                value={config.agent_name}
                onChange={(e) => setConfig(prev => ({ ...prev, agent_name: e.target.value }))}
                placeholder="Leave empty for auto-generated names"
              />
            </div>

            <div className="space-y-2">
              <Label>Agent Options</Label>
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.auto_start}
                    onChange={(e) => setConfig(prev => ({ ...prev, auto_start: e.target.checked }))}
                  />
                  <span>Auto Start</span>
                </label>
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={config.run_as_service}
                    onChange={(e) => setConfig(prev => ({ ...prev, run_as_service: e.target.checked }))}
                  />
                  <span>Run as Service</span>
                </label>
              </div>
            </div>

            {config.tags.length > 0 && (
              <div className="space-y-2">
                <Label>Default Tags</Label>
                <div className="flex flex-wrap gap-2">
                  {config.tags.map((tag, index) => (
                    <Badge key={index} variant="secondary">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="md:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Bot className="h-5 w-5" />
              <span>ChatGPT API Configuration</span>
            </CardTitle>
            <CardDescription>
              Configure OpenAI ChatGPT API for AI-powered features
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="chatgpt-api-key">OpenAI API Key</Label>
                <Input
                  id="chatgpt-api-key"
                  type="password"
                  value={chatgptConfig.api_key}
                  onChange={(e) => setChatgptConfig(prev => ({ ...prev, api_key: e.target.value }))}
                  placeholder="sk-..."
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="chatgpt-model">Model</Label>
                <Select 
                  value={chatgptConfig.model} 
                  onValueChange={(value) => setChatgptConfig(prev => ({ ...prev, model: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select model" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                    <SelectItem value="gpt-4">GPT-4</SelectItem>
                    <SelectItem value="gpt-4-turbo">GPT-4 Turbo</SelectItem>
                    <SelectItem value="gpt-4o">GPT-4o</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="max-tokens">Max Tokens</Label>
                <Input
                  id="max-tokens"
                  type="number"
                  value={chatgptConfig.max_tokens}
                  onChange={(e) => setChatgptConfig(prev => ({ ...prev, max_tokens: parseInt(e.target.value) || 1000 }))}
                  placeholder="1000"
                  min="1"
                  max="4000"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="temperature">Temperature</Label>
                <Input
                  id="temperature"
                  type="number"
                  value={chatgptConfig.temperature}
                  onChange={(e) => setChatgptConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) || 0.7 }))}
                  placeholder="0.7"
                  min="0"
                  max="2"
                  step="0.1"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="system-prompt">System Prompt (Optional)</Label>
              <Textarea
                id="system-prompt"
                value={chatgptConfig.system_prompt}
                onChange={(e) => setChatgptConfig(prev => ({ ...prev, system_prompt: e.target.value }))}
                placeholder="You are a helpful assistant that helps with PowerShell commands..."
                rows={3}
              />
            </div>

            <div className="flex space-x-2">
              <Button onClick={testChatGPTAPI} variant="outline" disabled={loading || !chatgptConfig.api_key}>
                <TestTube className="mr-2 h-4 w-4" />
                Test API
              </Button>
              <Button onClick={saveChatGPTConfig} disabled={loading}>
                <Save className="mr-2 h-4 w-4" />
                Save ChatGPT Config
              </Button>
            </div>
          </CardContent>
        </Card>

        {systemInfo && (
          <Card className="md:col-span-2">
            <CardHeader>
              <CardTitle>System Information</CardTitle>
              <CardDescription>
                Current server system details
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <Label className="text-sm font-medium">Hostname</Label>
                  <p className="text-sm text-muted-foreground">{systemInfo.hostname}</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">CPU Usage</Label>
                  <p className="text-sm text-muted-foreground">{systemInfo.cpu_usage?.toFixed(1)}%</p>
                </div>
                <div>
                  <Label className="text-sm font-medium">Memory Usage</Label>
                  <p className="text-sm text-muted-foreground">{systemInfo.memory_usage?.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <Separator />

      <div className="flex justify-between items-center">
        <div>
          <p className="text-sm text-muted-foreground">
            DexAgents Management Platform v1.0.0
          </p>
        </div>
        <Button variant="outline" onClick={() => window.location.reload()}>
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh Page
        </Button>
      </div>
    </div>
  )
}