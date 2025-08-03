"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import {
  Terminal,
  Search,
  Plus,
  Play,
  Edit,
  Copy,
  Filter,
  Settings,
  Network,
  HardDrive,
  Shield,
  Activity,
  Loader2,
  CheckCircle,
  XCircle,
  Trash2,
  Users,
  Bot,
  Wand2,
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { 
  apiClient, 
  SavedPowerShellCommand, 
  PowerShellCommandExecution,
  CommandParameter,
  Agent,
  AICommandRequest,
  AICommandResponse,
  AITestRequest,
  AIStatusResponse
} from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import CreateCommandForm from "@/components/CreateCommandForm"

const getCategoriesWithCounts = (commands: SavedPowerShellCommand[]) => {
  const categoryCounts = commands.reduce((acc, cmd) => {
    acc[cmd.category] = (acc[cmd.category] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const baseCategories = [
    { id: "all", name: "All Commands", icon: Terminal, count: commands.length },
    { id: "system", name: "System Info", icon: Settings, count: categoryCounts.system || 0 },
    { id: "network", name: "Network", icon: Network, count: categoryCounts.network || 0 },
    { id: "disk", name: "Disk & Storage", icon: HardDrive, count: categoryCounts.disk || 0 },
    { id: "security", name: "Security", icon: Shield, count: categoryCounts.security || 0 },
    { id: "monitoring", name: "Monitoring", icon: Activity, count: categoryCounts.monitoring || 0 },
    { id: "general", name: "General", icon: Terminal, count: categoryCounts.general || 0 },
  ]

  return baseCategories.filter(cat => cat.id === "all" || cat.count > 0)
}

export default function CommandLibraryPage() {
  const router = useRouter()
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedCommand, setSelectedCommand] = useState<SavedPowerShellCommand | null>(null)
  const [executing, setExecuting] = useState(false)
  const [executionResult, setExecutionResult] = useState<any>(null)
  const [commands, setCommands] = useState<SavedPowerShellCommand[]>([])
  const [agents, setAgents] = useState<Agent[]>([])
  const [selectedAgents, setSelectedAgents] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [parameterValues, setParameterValues] = useState<Record<string, any>>({})
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [editingCommand, setEditingCommand] = useState<SavedPowerShellCommand | null>(null)
  const [aiDialogOpen, setAiDialogOpen] = useState(false)
  const [aiStatus, setAiStatus] = useState<AIStatusResponse | null>(null)
  const [chatMessages, setChatMessages] = useState<Array<{role: string, content: string}>>([])
  const [currentMessage, setCurrentMessage] = useState("")
  const [aiGenerating, setAiGenerating] = useState(false)
  const [generatedCommand, setGeneratedCommand] = useState<AICommandResponse | null>(null)
  const [testingCommand, setTestingCommand] = useState(false)
  const [selectedTestAgent, setSelectedTestAgent] = useState<string>("")
  const [retryCount, setRetryCount] = useState(0)
  const { toast } = useToast()

  const categories = getCategoriesWithCounts(commands)

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true)
        const [commandsData, agentsData, aiStatusData] = await Promise.all([
          apiClient.getSavedCommands(),
          apiClient.getAgents(),
          apiClient.getAIStatus()
        ])
        setCommands(commandsData)
        setAgents(agentsData)
        setAiStatus(aiStatusData)
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load data",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }
    loadData()
  }, [toast])

  const filteredCommands = commands.filter((command) => {
    const matchesCategory = selectedCategory === "all" || command.category === selectedCategory
    const matchesSearch =
      command.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (command.description && command.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
      command.tags.some((tag) => tag.toLowerCase().includes(searchTerm.toLowerCase()))
    return matchesCategory && matchesSearch
  })

  const getCategoryIcon = (categoryId: string) => {
    const category = categories.find((cat) => cat.id === categoryId)
    return category ? category.icon : Terminal
  }

  const pollCommandResult = async (agentId: string, commandId: string, maxAttempts = 10): Promise<any> => {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const result = await apiClient.getCommandResult(agentId, commandId)
        
        if (result.status === 'pending') {
          // Wait 2 seconds before next attempt
          await new Promise(resolve => setTimeout(resolve, 2000))
          continue
        }
        
        return result
      } catch (error) {
        if (attempt === maxAttempts - 1) {
          throw error
        }
        await new Promise(resolve => setTimeout(resolve, 2000))
      }
    }
    
    throw new Error('Command execution timeout')
  }

  const executeCommand = async (command: SavedPowerShellCommand) => {
    if (selectedAgents.length === 0) {
      toast({
        title: "Error",
        description: "Please select at least one agent",
        variant: "destructive",
      })
      return
    }

    try {
      setExecuting(true)
      setExecutionResult(null)
      
      console.log('=== COMMAND EXECUTION DEBUG START ===')
      console.log('Command:', command.name)
      console.log('Selected agents:', selectedAgents)
      console.log('Parameter values:', parameterValues)
      
      // Backend now handles parameter defaults comprehensively
      // Just pass the parameters as provided by the user
      const result = await apiClient.executeSavedCommand(
        command.id!, 
        selectedAgents, 
        parameterValues, 
        30
      )
      
      console.log('Backend result:', result)
      console.log('Result.results:', result.results)
      
      toast({
        title: "Success", 
        description: `Command sent to ${selectedAgents.length} agent(s). Waiting for results...`,
      })

      // Poll for command execution results
      const agentResults: Record<string, any> = {}
      
      await Promise.all(selectedAgents.map(async (agentId, index) => {
        try {
          console.log(`Processing agent ${agentId} (index ${index})`)
          
          // Find the result for this specific agent
          const agentResult = result.results.find((r: any) => r.agent_id === agentId) || result.results[index]
          console.log(`Agent ${agentId} result:`, agentResult)
          
          // Check if this agent's result has an error
          if (agentResult?.success === false || agentResult?.error) {
            console.error(`Agent ${agentId} has error:`, agentResult.error)
            throw new Error(agentResult.error || 'Agent execution failed')
          }
          
          const commandId = agentResult?.command_id
          console.log(`Agent ${agentId} command ID:`, commandId)
          
          if (!commandId) {
            console.error(`No command ID for agent ${agentId}`)
            throw new Error('No command ID received')
          }
          
          console.log(`Polling command result for agent ${agentId}, command ${commandId}`)
          
          // Add small delay to allow WebSocket response to be processed
          await new Promise(resolve => setTimeout(resolve, 1000))
          
          const commandResult = await pollCommandResult(agentId, commandId)
          console.log(`Command result for agent ${agentId}:`, commandResult)
          
          if (commandResult.status === 'completed' && commandResult.result) {
            // Handle successful execution
            if (commandResult.result.success) {
              agentResults[agentId] = {
                success: true,
                output: typeof commandResult.result.output === 'string' 
                  ? JSON.parse(commandResult.result.output) 
                  : commandResult.result.output,
                execution_time: commandResult.result.execution_time || 0,
                timestamp: commandResult.result.timestamp || new Date().toISOString()
              }
            } else {
              // Command completed but failed
              console.error(`Command failed for agent ${agentId}:`, commandResult.result)
              
              // Handle PowerShell errors with empty error messages
              let errorMessage = commandResult.result.error || ''
              
              // Check if we have an error object with empty error field
              if (!errorMessage && commandResult.result.output) {
                // Check if output is an object with error field
                if (typeof commandResult.result.output === 'object' && 
                    commandResult.result.output !== null && 
                    'error' in commandResult.result.output) {
                  errorMessage = commandResult.result.output.error || ''
                } else {
                  // Try to extract error from output
                  errorMessage = typeof commandResult.result.output === 'string' 
                    ? commandResult.result.output 
                    : JSON.stringify(commandResult.result.output)
                }
              }
              
              // Provide user-friendly message for empty errors
              if (!errorMessage || errorMessage === '{"error":""}' || errorMessage === '{}') {
                errorMessage = 'PowerShell command failed. Possible causes:\n' +
                  '• The Get-EventLog cmdlet requires administrator privileges\n' +
                  '• The command may not be available on PowerShell Core (use Get-WinEvent instead)\n' +
                  '• The Windows Event Log service may not be running'
              }
              
              // Instead of throwing, we can store the error result
              agentResults[agentId] = {
                success: false,
                error: errorMessage,
                execution_time: commandResult.result.execution_time || 0,
                timestamp: commandResult.result.timestamp || new Date().toISOString(),
                note: 'Command executed but returned failure status'
              }
            }
          } else if (commandResult.status === 'pending') {
            // Command still pending after polling
            throw new Error('Command execution timeout - still pending after maximum polling attempts')
          } else {
            // Command not completed or no result
            console.error(`Unexpected command result for agent ${agentId}:`, commandResult)
            const errorMessage = commandResult.result?.error || commandResult.error || 'Command execution failed or timed out'
            throw new Error(errorMessage)
          }
        } catch (error) {
          console.error(`=== Error getting result for agent ${agentId} ===`)
          console.error('Error object:', error)
          console.error('Error type:', typeof error)
          console.error('Error stack:', error instanceof Error ? error.stack : 'No stack')
          
          agentResults[agentId] = {
            success: false,
            error: error instanceof Error ? error.message : "Failed to get command result",
            execution_time: 0,
            timestamp: new Date().toISOString()
          }
        }
      }))
      
      setExecutionResult(agentResults)
      
      toast({
        title: "Completed",
        description: `Results received from ${Object.keys(agentResults).length} agent(s)`,
      })
      
    } catch (error) {
      console.error('Execute command error:', error)
      toast({
        title: "Error",
        description: "Failed to execute command",
        variant: "destructive",
      })
    } finally {
      setExecuting(false)
    }
  }

  const deleteCommand = async (commandId: string) => {
    try {
      await apiClient.deleteSavedCommand(commandId)
      setCommands(commands.filter(cmd => cmd.id !== commandId))
      toast({
        title: "Success",
        description: "Command deleted successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to delete command",
        variant: "destructive",
      })
    }
  }

  const updateCommand = async (updatedCommand: SavedPowerShellCommand) => {
    try {
      const updated = await apiClient.updateSavedCommand(updatedCommand.id!, updatedCommand)
      setCommands(commands.map(cmd => cmd.id === updated.id ? updated : cmd))
      setEditDialogOpen(false)
      setEditingCommand(null)
      toast({
        title: "Success",
        description: "Command updated successfully",
      })
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to update command",
        variant: "destructive",
      })
    }
  }

  const sendAIMessage = async () => {
    if (!currentMessage.trim() || aiGenerating) return

    const userMessage = currentMessage.trim()
    setCurrentMessage("")
    
    const newMessages = [...chatMessages, { role: "user", content: userMessage }]
    setChatMessages(newMessages)
    setAiGenerating(true)

    try {
      const response = await apiClient.generateCommandWithAI({
        message: userMessage,
        conversation_history: newMessages.slice(-10) // Keep last 10 messages for context
      })

      if (response.success && response.command_data) {
        setGeneratedCommand(response)
        setChatMessages([...newMessages, { 
          role: "assistant", 
          content: `I've generated a PowerShell command for you:\n\n**${response.command_data.name}**\n\n${response.command_data.explanation}\n\n\`\`\`powershell\n${response.command_data.command}\n\`\`\``
        }])
        setRetryCount(0)
      } else {
        throw new Error(response.error || "Failed to generate command")
      }
    } catch (error) {
      setChatMessages([...newMessages, { 
        role: "assistant", 
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : "Unknown error"}`
      }])
      
      if (retryCount < 2) {
        setRetryCount(retryCount + 1)
        toast({
          title: "Error",
          description: `Generation failed. Retry ${retryCount + 1}/3`,
          variant: "destructive",
        })
      } else {
        toast({
          title: "Error",
          description: "Failed to generate command after 3 attempts. Please try a different request.",
          variant: "destructive",
        })
        setRetryCount(0)
      }
    } finally {
      setAiGenerating(false)
    }
  }

  const testGeneratedCommand = async () => {
    if (!generatedCommand?.command_data?.command || !selectedTestAgent || testingCommand) return

    setTestingCommand(true)
    try {
      const response = await apiClient.testAICommand({
        command: generatedCommand.command_data.command,
        agent_id: selectedTestAgent,
        timeout: 30
      })

      if (response.success && response.result) {
        const result = response.result
        if (result.success) {
          let outputDisplay = ""
          if (result.output) {
            try {
              // Try to format JSON output nicely
              const parsedOutput = typeof result.output === 'string' ? JSON.parse(result.output) : result.output
              outputDisplay = JSON.stringify(parsedOutput, null, 2)
            } catch {
              // If not JSON, display as is
              outputDisplay = typeof result.output === 'string' ? result.output : JSON.stringify(result.output, null, 2)
            }
          }

          toast({
            title: "Test Successful",
            description: "Command executed successfully on agent",
          })
          
          setChatMessages(prev => [...prev, {
            role: "assistant",
            content: `✅ **Test Result: Success**\n\nThe command ran successfully on the agent${result.execution_time ? ` in ${result.execution_time.toFixed(2)}s` : ''}.\n\n**Command Output:**\n\`\`\`json\n${outputDisplay}\n\`\`\`\n\nYou can now create this command using the "Create Command" button below.`
          }])
        } else {
          throw new Error(result.error || "Command execution failed")
        }
      } else {
        throw new Error(response.error || "Test failed")
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error"
      toast({
        title: "Test Failed",
        description: errorMessage,
        variant: "destructive",
      })
      setChatMessages(prev => [...prev, {
        role: "assistant",
        content: `❌ **Test Result: Failed**\n\nError: ${errorMessage}\n\nLet me try to generate a different command for you.`
      }])
      
      // Auto-retry with error feedback if under retry limit
      if (retryCount < 2) {
        setTimeout(() => {
          setCurrentMessage(`The previous command failed with error: ${errorMessage}. Please generate a different approach.`)
          sendAIMessage()
        }, 1000)
      }
    } finally {
      setTestingCommand(false)
    }
  }

  const handleAiButtonClick = () => {
    // Check if AI is available (ChatGPT configured)
    if (!aiStatus?.available) {
      // Redirect to settings page if ChatGPT is not configured
      toast({
        title: "ChatGPT Not Configured",
        description: "Please configure your ChatGPT API key in settings first.",
        variant: "destructive",
      })
      router.push('/settings')
      return
    }
    
    // If AI is available, open the AI dialog
    setAiDialogOpen(true)
  }

  const createCommandFromAI = () => {
    if (!generatedCommand?.command_data) return

    const commandData = generatedCommand.command_data
    setGeneratedCommand(null)
    setAiDialogOpen(false)
    setChatMessages([])
    setCurrentMessage("")
    setRetryCount(0)
    
    // Open the create command dialog with pre-filled data
    setCreateDialogOpen(true)
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Command Library</h2>
            <p className="text-muted-foreground">Manage and execute commands across your agents</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create Command
              </Button>
            </DialogTrigger>
          </Dialog>
          
          <Dialog open={aiDialogOpen} onOpenChange={setAiDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" onClick={handleAiButtonClick}>
                <Wand2 className="mr-2 h-4 w-4" />
                Create Command with AI
              </Button>
            </DialogTrigger>
          </Dialog>
        </div>
        
        {/* AI Chat Dialog */}
        <Dialog open={aiDialogOpen} onOpenChange={setAiDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Create Command with AI
              </DialogTitle>
              <DialogDescription>
                Describe what you want to do and AI will generate a PowerShell command for you
              </DialogDescription>
            </DialogHeader>
            
            <div className="flex-1 flex flex-col space-y-4 min-h-0">
              {/* Chat Messages */}
              <div className="flex-1 border rounded-lg p-4 overflow-y-auto bg-muted/30 dark:bg-muted/10 min-h-[300px]">
                {chatMessages.length === 0 ? (
                  <div className="text-center text-muted-foreground">
                    <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>Start by describing what you want to accomplish...</p>
                    <p className="text-sm mt-2">Example: "Show me system information" or "List all running services"</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {chatMessages.map((msg, index) => (
                      <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg p-3 ${
                          msg.role === 'user' 
                            ? 'bg-primary text-primary-foreground shadow-sm' 
                            : 'bg-card dark:bg-card border shadow-sm'
                        }`}>
                          <div className="whitespace-pre-wrap text-sm">{msg.content}</div>
                        </div>
                      </div>
                    ))}
                    {aiGenerating && (
                      <div className="flex justify-start">
                        <div className="max-w-[80%] bg-card dark:bg-card border rounded-lg p-3 shadow-sm">
                          <div className="flex items-center gap-2 text-muted-foreground">
                            <Loader2 className="h-4 w-4 animate-spin" />
                            <span className="text-sm">Generating command...</span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Command Generation Results */}
              {generatedCommand?.command_data && (
                <div className="border rounded-lg p-4 bg-green-50 dark:bg-green-950/30 dark:border-green-800/50">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-green-800 dark:text-green-200">Generated Command</h4>
                    <div className="flex gap-2">
                      <Select value={selectedTestAgent} onValueChange={setSelectedTestAgent}>
                        <SelectTrigger className="w-40">
                          <SelectValue placeholder="Select agent to test" />
                        </SelectTrigger>
                        <SelectContent>
                          {agents.filter(agent => agent.status === 'online' && agent.id).map((agent) => (
                            <SelectItem key={agent.id} value={agent.id!}>
                              {agent.hostname}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={testGeneratedCommand}
                        disabled={!selectedTestAgent || testingCommand}
                      >
                        {testingCommand ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Testing...
                          </>
                        ) : (
                          <>
                            <Play className="mr-2 h-4 w-4" />
                            Test Command
                          </>
                        )}
                      </Button>
                      <Button size="sm" onClick={createCommandFromAI}>
                        <Plus className="mr-2 h-4 w-4" />
                        Create Command
                      </Button>
                    </div>
                  </div>
                  <div className="text-sm text-green-700 dark:text-green-300 mb-2">{generatedCommand.command_data.description}</div>
                  <Textarea 
                    value={generatedCommand.command_data.command} 
                    readOnly 
                    className="font-mono text-sm bg-background border-input" 
                    rows={3}
                  />
                </div>
              )}

              {/* Message Input */}
              <div className="flex gap-2">
                <Input 
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  placeholder="Describe what you want to do..."
                  onKeyPress={(e) => e.key === 'Enter' && sendAIMessage()}
                  disabled={aiGenerating}
                />
                <Button 
                  onClick={sendAIMessage}
                  disabled={!currentMessage.trim() || aiGenerating}
                >
                  {aiGenerating ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <span className="font-bold">→</span>
                  )}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        {/* Create Command Dialog */}
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Command</DialogTitle>
              <DialogDescription>
                Create a reusable command template with parameters
              </DialogDescription>
            </DialogHeader>
            <CreateCommandForm 
              onSubmit={async (command) => {
                try {
                  const newCommand = await apiClient.createSavedCommand(command)
                  setCommands([newCommand, ...commands])
                  setCreateDialogOpen(false)
                  toast({
                    title: "Success",
                    description: "Command created successfully",
                  })
                } catch (error) {
                  toast({
                    title: "Error",
                    description: "Failed to create command",
                    variant: "destructive",
                  })
                }
              }}
              onCancel={() => setCreateDialogOpen(false)}
            />
          </DialogContent>
        </Dialog>

        {editDialogOpen && (
          <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>Edit Command</DialogTitle>
                <DialogDescription>
                  Modify the command template and parameters
                </DialogDescription>
              </DialogHeader>
              {editingCommand ? (
                <CreateCommandForm 
                  initialData={editingCommand}
                  onSubmit={updateCommand}
                  onCancel={() => {
                    setEditDialogOpen(false)
                    setEditingCommand(null)
                  }}
                />
              ) : (
                <div>Loading command data...</div>
              )}
            </DialogContent>
          </Dialog>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Categories
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {categories.map((category) => {
              const Icon = category.icon
              return (
                <Button
                  key={category.id}
                  variant={selectedCategory === category.id ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => setSelectedCategory(category.id)}
                >
                  <Icon className="mr-2 h-4 w-4" />
                  <span className="flex-1 text-left">{category.name}</span>
                  <Badge variant="secondary" className="ml-auto">
                    {category.count}
                  </Badge>
                </Button>
              )
            })}
          </CardContent>
        </Card>

        <div className="lg:col-span-3 space-y-4">
          <Card>
            <CardContent className="pt-6">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search commands, descriptions, or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </CardContent>
          </Card>

          {loading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin" />
              <span className="ml-2">Loading commands...</span>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {filteredCommands.map((command) => {
                const CategoryIcon = getCategoryIcon(command.category)
                return (
                  <Card key={command.id} className="hover:shadow-md transition-shadow">
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex items-center gap-2">
                          <CategoryIcon className="h-5 w-5 text-muted-foreground" />
                          <CardTitle className="text-lg">{command.name}</CardTitle>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">v{command.version}</Badge>
                          {command.is_system && (
                            <Badge variant="secondary" className="text-xs">System</Badge>
                          )}
                        </div>
                      </div>
                      <CardDescription className="line-clamp-2">{command.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex flex-wrap gap-1">
                        {command.tags.map((tag) => (
                          <Badge key={tag} variant="secondary" className="text-xs">
                            {tag}
                          </Badge>
                        ))}
                      </div>

                      <div className="text-xs text-muted-foreground">
                        <p>
                          By {command.author} • {command.updated_at ? new Date(command.updated_at).toLocaleDateString() : 'Unknown'}
                        </p>
                        {command.parameters.length > 0 && <p>{command.parameters.length} parameter(s)</p>}
                      </div>

                    <div className="flex gap-2">
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button size="sm" onClick={() => {
                            setSelectedCommand(command)
                            setParameterValues({})
                            setSelectedAgents([])
                            setExecutionResult(null)
                          }}>
                            <Play className="mr-2 h-4 w-4" />
                            Run
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
                          <DialogHeader>
                            <DialogTitle>Run Command: {command.name}</DialogTitle>
                            <DialogDescription>Configure parameters, select agents and execute the command</DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label>Command</Label>
                              <Textarea value={command.command} readOnly className="font-mono text-sm" rows={3} />
                            </div>
                            
                            {command.parameters.length > 0 && (
                              <div className="space-y-2">
                                <Label>Parameters</Label>
                                {command.parameters.map((param) => (
                                  <div key={param.name} className="grid grid-cols-3 gap-2 items-center">
                                    <Label className="text-sm font-medium">
                                      ${param.name}
                                      {param.required && <span className="text-red-500 ml-1">*</span>}
                                    </Label>
                                    <div className="col-span-2">
                                      <Input 
                                        placeholder={param.default || `Enter ${param.name}`}
                                        value={parameterValues[param.name] || ''}
                                        onChange={(e) => setParameterValues(prev => ({
                                          ...prev,
                                          [param.name]: e.target.value
                                        }))}
                                      />
                                      {param.description && (
                                        <p className="text-xs text-muted-foreground mt-1">{param.description}</p>
                                      )}
                                    </div>
                                  </div>
                                ))}
                              </div>
                            )}

                            <div className="space-y-2">
                              <Label>Select Agents</Label>
                              <div className="border rounded-lg p-3 space-y-2 max-h-32 overflow-y-auto">
                                {agents.filter(agent => agent.status === 'online' && agent.id).map((agent) => (
                                  <div key={agent.id} className="flex items-center space-x-2">
                                    <Checkbox
                                      id={agent.id!}
                                      checked={selectedAgents.includes(agent.id!)}
                                      onCheckedChange={(checked) => {
                                        if (checked) {
                                          setSelectedAgents(prev => [...prev, agent.id!])
                                        } else {
                                          setSelectedAgents(prev => prev.filter(id => id !== agent.id))
                                        }
                                      }}
                                    />
                                    <Label htmlFor={agent.id!} className="flex items-center gap-2 cursor-pointer">
                                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                                      <span>{agent.hostname}</span>
                                      <Badge variant="outline" className="text-xs">{agent.os}</Badge>
                                    </Label>
                                  </div>
                                ))}
                                {agents.filter(agent => agent.status === 'online' && agent.id).length === 0 && (
                                  <p className="text-sm text-muted-foreground">No connected agents available</p>
                                )}
                              </div>
                            </div>

                            <div className="flex justify-end gap-2">
                              <Button 
                                variant="outline" 
                                onClick={() => setSelectedCommand(null)}
                              >
                                Cancel
                              </Button>
                              <Button 
                                onClick={() => executeCommand(command)}
                                disabled={executing || selectedAgents.length === 0}
                              >
                                {executing ? (
                                  <>
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                    Executing & Polling Results...
                                  </>
                                ) : (
                                  <>
                                    <Play className="mr-2 h-4 w-4" />
                                    Execute on {selectedAgents.length} agent(s)
                                  </>
                                )}
                              </Button>
                            </div>
                            
                            {executionResult && (
                              <div className="mt-4 space-y-4">
                                <Label className="text-lg font-medium">Execution Results</Label>
                                {Object.entries(executionResult).map(([agentId, result]: [string, any]) => {
                                  const agent = agents.find(a => a.id === agentId)
                                  return (
                                    <div key={agentId} className="p-4 border rounded-lg">
                                      <div className="flex items-center gap-2 mb-2">
                                        <Users className="h-4 w-4" />
                                        <span className="font-medium">{agent?.hostname || agentId}</span>
                                        {result.success ? (
                                          <CheckCircle className="h-4 w-4 text-green-600" />
                                        ) : (
                                          <XCircle className="h-4 w-4 text-red-600" />
                                        )}
                                        <Badge variant={result.success ? "default" : "destructive"} className="text-xs">
                                          {result.success ? "Success" : "Failed"}
                                        </Badge>
                                        <span className="text-sm text-muted-foreground ml-auto">
                                          {result.execution_time?.toFixed(2) || '0.00'}s
                                        </span>
                                      </div>
                                      {result.note && (
                                        <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded">
                                          <Label className="text-sm text-blue-700">Note:</Label>
                                          <p className="text-xs text-blue-600 mt-1">{result.note}</p>
                                        </div>
                                      )}
                                      {result.output && (
                                        <div className="mt-2">
                                          <Label className="text-sm">Output (JSON):</Label>
                                          <Textarea 
                                            value={typeof result.output === 'string' ? result.output : JSON.stringify(result.output, null, 2)} 
                                            readOnly 
                                            className="font-mono text-sm mt-1" 
                                            rows={6}
                                          />
                                        </div>
                                      )}
                                      {result.error && (
                                        <div className="mt-2">
                                          <Label className="text-sm text-red-600">Error:</Label>
                                          <Textarea 
                                            value={result.error} 
                                            readOnly 
                                            className="font-mono text-sm mt-1 text-red-600" 
                                            rows={2}
                                          />
                                        </div>
                                      )}
                                    </div>
                                  )
                                })}
                              </div>
                            )}
                          </div>
                        </DialogContent>
                      </Dialog>

                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => {
                          setEditingCommand(command)
                          setEditDialogOpen(true)
                        }}
                        disabled={command.is_system}
                      >
                        <Edit className="mr-2 h-4 w-4" />
                        Edit
                      </Button>

                      <Button size="sm" variant="outline">
                        <Copy className="mr-2 h-4 w-4" />
                        Clone
                      </Button>
                      
                      {!command.is_system && (
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => deleteCommand(command.id!)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
                )
              })}
            </div>
          )}

          {filteredCommands.length === 0 && !loading && (
            <Card>
              <CardContent className="text-center py-8">
                <Terminal className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No commands found</h3>
                <p className="text-muted-foreground mb-4">No commands match your current filters.</p>
                <Button onClick={() => setCreateDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Create New Command
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}