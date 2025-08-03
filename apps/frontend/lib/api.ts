// API Client for DexAgents Frontend

export interface SystemInfo {
  hostname: string
  os_version: string
  cpu_usage: number
  memory_usage: number
  disk_usage: Record<string, number>
}

export interface Agent {
  id?: string
  hostname: string
  ip?: string
  os?: string
  version?: string
  status: string
  last_seen?: string
  tags: string[]
  system_info?: Record<string, any>
  connection_id?: string
  is_connected: boolean
}

export interface AgentUpdate {
  hostname?: string
  ip?: string
  os?: string
  version?: string
  status?: string
  tags?: string[]
  system_info?: Record<string, any>
  connection_id?: string
  is_connected?: boolean
}

export interface AgentRegister {
  hostname: string
  ip?: string
  os?: string
  version?: string
  tags: string[]
  system_info?: Record<string, any>
}

export interface AgentInstallerConfig {
  server_url: string
  api_token: string
  agent_name?: string
  tags: string[]
  auto_start: boolean
  run_as_service: boolean
}

export interface InstallerConfig {
  server_url: string
  api_token: string
  agent_name?: string
  tags: string[]
  auto_start: boolean
  run_as_service: boolean
}

export interface WebSocketMessage {
  type: string
  data: Record<string, any>
  timestamp?: string
}

export interface AgentCommand {
  command: string
  timeout?: number
  working_directory?: string
}

export interface CommandResult {
  command: string
  success: boolean
  output?: string
  error?: string
  execution_time?: number
  exit_code?: number
}

export interface PowerShellCommand {
  command: string
  timeout?: number
  working_directory?: string
  run_as_admin?: boolean
}

export interface CommandResponse {
  success: boolean
  output?: string
  error?: string
  execution_time?: number
  timestamp: string
  command: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

export interface CommandCreate {
  name: string
  description?: string
  script: string
  category?: string
  parameters?: Record<string, any>
  tags?: string[]
  require_confirmation?: boolean
  timeout?: number
}

export interface Command {
  id: string
  name: string
  description?: string
  script: string
  category?: string
  parameters?: Record<string, any>
  tags?: string[]
  require_confirmation?: boolean
  timeout?: number
  created_at: string
  updated_at: string
}

export interface SavedPowerShellCommand {
  id: string
  name: string
  description?: string
  command: string
  category: string
  parameters?: CommandParameter[]
  tags?: string[]
  version?: string
  author?: string
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface CommandParameter {
  name: string
  type: string
  required: boolean
  default_value?: any
  description?: string
  validation?: string
}

export interface PowerShellCommandExecution {
  command_id: string
  command_name: string
  executed_command: string
  results: Array<{
    agent_id: string
    command_id?: string
    status: string
    message?: string
    success?: boolean
    error?: string
  }>
}

export interface AICommandRequest {
  message: string
  conversation_history?: Array<{role: string, content: string}>
}

export interface AICommandResponse {
  success: boolean
  command_data?: {
    command: string
    name: string
    description: string
    category: string
    parameters: CommandParameter[]
    tags: string[]
    explanation: string
  }
  raw_response?: string
  error?: string
  note?: string
}

export interface AITestRequest {
  command: string
  agent_id: string
  timeout?: number
}

export interface AITestResponse {
  success: boolean
  command_id?: string
  result?: any
  error?: string
}

export interface AIStatusResponse {
  available: boolean
  message: string
}

class ApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor() {
    // Use internal API URL on server-side, public API URL on client-side
    if (typeof window === 'undefined') {
      // Server-side: use internal Docker network URL
      this.baseUrl = process.env.NEXT_PUBLIC_INTERNAL_API_URL || process.env.BACKEND_URL || 'http://backend:8000'
    } else {
      // Client-side: use public URL
      this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
      this.token = localStorage.getItem('auth_token')
    }
  }

  setToken(token: string | null) {
    this.token = token
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('auth_token', token)
      } else {
        localStorage.removeItem('auth_token')
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>
    }

    // Always get fresh token from localStorage to ensure sync with AuthContext
    const currentToken = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : this.token
    if (currentToken) {
      headers['Authorization'] = `Bearer ${currentToken}`
    }

    const response = await fetch(url, {
      ...options,
      headers
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(error || `HTTP error! status: ${response.status}`)
    }

    return response.json()
  }

  // Auth endpoints
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>('/api/v1/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
    this.setToken(response.access_token)
    return response
  }

  async logout(): Promise<void> {
    this.setToken(null)
  }

  // System endpoints
  async getSystemInfo(): Promise<SystemInfo> {
    return this.request<SystemInfo>('/api/v1/system/info')
  }

  // Agent endpoints
  async getAgents(): Promise<Agent[]> {
    return this.request<Agent[]>('/api/v1/agents/')
  }

  async getAgent(id: string): Promise<Agent> {
    return this.request<Agent>(`/api/v1/agents/${id}`)
  }

  async updateAgent(id: string, data: AgentUpdate): Promise<Agent> {
    return this.request<Agent>(`/api/v1/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async deleteAgent(id: string): Promise<void> {
    await this.request(`/api/v1/agents/${id}`, {
      method: 'DELETE'
    })
  }

  async executeCommand(agentId: string, command: AgentCommand): Promise<CommandResult> {
    return this.request<CommandResult>(`/api/v1/agents/${agentId}/execute`, {
      method: 'POST',
      body: JSON.stringify(command)
    })
  }

  async refreshAgent(agentId: string): Promise<{ message: string; agent: Agent }> {
    return this.request<{ message: string; agent: Agent }>(`/api/v1/agents/${agentId}/refresh`, {
      method: 'POST'
    })
  }

  async executeAgentCommand(agentId: string, command: string): Promise<CommandResponse> {
    const commandData: PowerShellCommand = {
      command: command,
      timeout: 30
    }
    return this.request<CommandResponse>(`/api/v1/agents/${agentId}/command`, {
      method: 'POST',
      body: JSON.stringify(commandData)
    })
  }

  // Commands endpoints
  async getCommands(): Promise<Command[]> {
    return this.request<Command[]>('/api/v1/commands/')
  }

  async getCommand(id: string): Promise<Command> {
    return this.request<Command>(`/api/v1/commands/${id}`)
  }

  async createCommand(data: CommandCreate): Promise<Command> {
    return this.request<Command>('/api/v1/commands/', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateCommand(id: string, data: Partial<CommandCreate>): Promise<Command> {
    return this.request<Command>(`/api/v1/commands/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async deleteCommand(id: string): Promise<void> {
    await this.request(`/api/v1/commands/${id}`, {
      method: 'DELETE'
    })
  }

  // Saved PowerShell Commands endpoints
  async getSavedCommands(): Promise<SavedPowerShellCommand[]> {
    return this.request<SavedPowerShellCommand[]>('/api/v1/commands/saved')
  }

  async getSavedCommand(id: string): Promise<SavedPowerShellCommand> {
    return this.request<SavedPowerShellCommand>(`/api/v1/commands/saved/${id}`)
  }

  async createSavedCommand(data: Partial<SavedPowerShellCommand>): Promise<SavedPowerShellCommand> {
    return this.request<SavedPowerShellCommand>('/api/v1/commands/saved', {
      method: 'POST',
      body: JSON.stringify(data)
    })
  }

  async updateSavedCommand(id: string, data: Partial<SavedPowerShellCommand>): Promise<SavedPowerShellCommand> {
    return this.request<SavedPowerShellCommand>(`/api/v1/commands/saved/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    })
  }

  async deleteSavedCommand(id: string): Promise<void> {
    await this.request(`/api/v1/commands/saved/${id}`, {
      method: 'DELETE'
    })
  }

  async executeSavedCommand(
    commandId: string, 
    agentIds: string[], 
    parameters: Record<string, any> = {},
    timeout: number = 30
  ): Promise<PowerShellCommandExecution> {
    return this.request<PowerShellCommandExecution>(`/api/v1/commands/saved/${commandId}/execute`, {
      method: 'POST',
      body: JSON.stringify({
        agent_ids: agentIds,
        parameters,
        timeout
      })
    })
  }

  async getCommandResult(agentId: string, commandId: string): Promise<any> {
    return this.request(`/api/v1/commands/agent/${agentId}/result/${commandId}`)
  }

  // Installer endpoints
  async getInstallerConfig(): Promise<InstallerConfig> {
    return this.request<InstallerConfig>('/api/v1/installer/config')
  }

  async generateInstaller(config: AgentInstallerConfig): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/installer/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
      },
      body: JSON.stringify(config)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.blob()
  }

  async createPythonAgent(config: AgentInstallerConfig): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/installer/create-python`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { 'Authorization': `Bearer ${this.token}` } : {})
      },
      body: JSON.stringify(config)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    return response.blob()
  }

  // AI-Powered Command Generation
  async generateCommandWithAI(request: AICommandRequest): Promise<AICommandResponse> {
    return this.request<AICommandResponse>('/api/v1/commands/ai/generate', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  async testAICommand(request: AITestRequest): Promise<AITestResponse> {
    return this.request<AITestResponse>('/api/v1/commands/ai/test', {
      method: 'POST',
      body: JSON.stringify(request)
    })
  }

  async getAIStatus(): Promise<AIStatusResponse> {
    return this.request<AIStatusResponse>('/api/v1/commands/ai/status')
  }
}

export const apiClient = new ApiClient()