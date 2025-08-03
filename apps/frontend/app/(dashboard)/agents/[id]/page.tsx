"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  Monitor, 
  Terminal, 
  Activity, 
  Settings, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Loader2, 
  AlertTriangle,
  HardDrive,
  Cpu,
  Network,
  Shield,
  RefreshCw,
  Play,
  FileText,
  Download,
  Upload,
  Trash2,
  Power,
  Wifi,
  Database,
  Calendar,
  Zap,
  BarChart3,
  History,
  Server
} from "lucide-react"
import { apiClient, Agent, SystemInfo, PowerShellCommand, CommandResponse } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"
import { useParams } from "next/navigation"
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
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

export default function AgentDetailPage() {
  const params = useParams()
  const agentId = params.id as string
  const [agent, setAgent] = useState<Agent | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [refreshing, setRefreshing] = useState(false)
  const [commandDialogOpen, setCommandDialogOpen] = useState(false)
  const [executingCommand, setExecutingCommand] = useState(false)
  const [commandResult, setCommandResult] = useState<CommandResponse | null>(null)
  const [commandInput, setCommandInput] = useState("")
  const [commandHistory, setCommandHistory] = useState<any[]>([])
  const [activeTab, setActiveTab] = useState("overview")
  const [autoRefresh, setAutoRefresh] = useState(false)
  const { toast } = useToast()

  const fetchAgent = async () => {
    try {
      setLoading(true)
      const agentData = await apiClient.getAgent(agentId)
      setAgent(agentData)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agent')
      toast({
        title: "Error",
        description: "Failed to load agent details",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleRefresh = async () => {
    if (!agent?.id) return
    
    try {
      setRefreshing(true)
      const result = await apiClient.refreshAgent(agent.id)
      
      // Preserve current system_info to prevent UI flickering
      const currentSystemInfo = agent.system_info
      
      // Wait longer for PowerShell command to complete and agent to send updated info
      setTimeout(async () => {
        try {
          if (agent?.id) {
            const updatedAgent = await apiClient.getAgent(agent.id)
            
            // If the updated agent doesn't have system_info, preserve the current one
            if (!updatedAgent.system_info || Object.keys(updatedAgent.system_info).length === 0) {
              updatedAgent.system_info = currentSystemInfo
            }
            
            setAgent(updatedAgent)
            
            toast({
              title: "Success",
              description: "Agent information refreshed successfully",
            })
          }
        } catch (err) {
          console.error("Error fetching updated agent:", err)
          toast({
            title: "Warning",
            description: "Agent refresh initiated, but updated data may take a moment to appear",
            variant: "default",
          })
        }
      }, 3000) // Wait 3 seconds for PowerShell command to complete
      
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to refresh agent information",
        variant: "destructive",
      })
    } finally {
      setTimeout(() => setRefreshing(false), 3100) // Stop refreshing after update
    }
  }

  const executeCommand = async () => {
    if (!commandInput.trim()) {
      toast({
        title: "Error",
        description: "Please enter a command",
        variant: "destructive",
      })
      return
    }

    try {
      setExecutingCommand(true)
      setCommandResult(null)

      // Execute command on the specific agent
      const result = await apiClient.executeAgentCommand(agentId, commandInput.trim())
      setCommandResult(result)
      
      // Add to command history
      const historyEntry = {
        id: Date.now(),
        command: commandInput.trim(),
        result: result,
        timestamp: new Date().toISOString(),
        agent_id: agentId
      }
      setCommandHistory(prev => [historyEntry, ...prev.slice(0, 9)]) // Keep last 10

      if (result.success) {
        toast({
          title: "Success",
          description: "Command executed successfully",
        })
      } else {
        toast({
          title: "Warning",
          description: "Command completed with errors",
          variant: "destructive",
        })
      }
    } catch (err) {
      toast({
        title: "Error",
        description: "Failed to execute command",
        variant: "destructive",
      })
    } finally {
      setExecutingCommand(false)
    }
  }

  const quickCommands = [
    {
      name: "System Info",
      command: "Get-ComputerInfo | Select-Object WindowsProductName, TotalPhysicalMemory, CsProcessors",
      icon: Activity,
      description: "Get basic system information"
    },
    {
      name: "Running Processes",
      command: "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name, CPU, WorkingSet",
      icon: FileText,
      description: "Show top 10 processes by CPU usage"
    },
    {
      name: "Running Services",
      command: "Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object Name, Status",
      icon: Settings,
      description: "List all running Windows services"
    },
    {
      name: "Disk Usage",
      command: "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID, @{Name='Size(GB)';Expression={[math]::Round($_.Size/1GB,2)}}, @{Name='FreeSpace(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}",
      icon: HardDrive,
      description: "Show disk space usage"
    },
    {
      name: "Network Info",
      command: "Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object Name, InterfaceDescription, LinkSpeed",
      icon: Network,
      description: "Show active network adapters"
    },
    {
      name: "Event Log Errors",
      command: "Get-EventLog -LogName System -EntryType Error -Newest 5 | Select-Object TimeGenerated, Source, Message",
      icon: AlertTriangle,
      description: "Show recent system errors"
    }
  ]

  useEffect(() => {
    if (agentId) {
      fetchAgent()
    }
  }, [agentId])

  // Auto-refresh effect
  useEffect(() => {
    if (!autoRefresh || !agent?.id || agent.status !== 'online') return

    const interval = setInterval(() => {
      handleRefresh()
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [autoRefresh, agent?.id, agent?.status])

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "online":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "offline":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-600" />
      default:
        return <XCircle className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "online":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            <Wifi className="w-3 h-3 mr-1" />
            Online
          </Badge>
        )
      case "offline":
        return (
          <Badge variant="destructive">
            <XCircle className="w-3 h-3 mr-1" />
            Offline
          </Badge>
        )
      case "pending":
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
            <Clock className="w-3 h-3 mr-1" />
            Pending
          </Badge>
        )
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / (24 * 3600))
    const hours = Math.floor((seconds % (24 * 3600)) / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    
    if (days > 0) return `${days}d ${hours}h ${minutes}m`
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  const formatLastSeen = (lastSeenStr: string) => {
    if (!lastSeenStr) return 'Never'
    
    const lastSeen = new Date(lastSeenStr)
    const now = new Date()
    const diffMs = now.getTime() - lastSeen.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading agent details...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error || !agent) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load agent</h3>
            <p className="text-muted-foreground mb-4">{error || 'Agent not found'}</p>
            <Button onClick={() => window.location.reload()}>
              Retry
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <div className="flex items-center gap-3">
              <Server className="h-8 w-8 text-blue-600" />
              <div>
                <h2 className="text-3xl font-bold tracking-tight">{agent.hostname}</h2>
                <p className="text-muted-foreground">Agent ID: {agent.id}</p>
              </div>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {getStatusIcon(agent.status)}
          {getStatusBadge(agent.status)}
          <div className="flex items-center gap-2">
            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            {agent.status === 'online' && (
              <Button
                onClick={() => setAutoRefresh(!autoRefresh)}
                variant={autoRefresh ? "default" : "outline"}
                size="sm"
              >
                <Zap className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-pulse' : ''}`} />
                {autoRefresh ? 'Auto' : 'Manual'}
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="grid gap-4 md:grid-cols-4 lg:grid-cols-6">
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-blue-600" />
            <div>
              <p className="text-xs text-muted-foreground">Status</p>
              <p className="text-sm font-medium capitalize">{agent.status}</p>
            </div>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-green-600" />
            <div>
              <p className="text-xs text-muted-foreground">Last Seen</p>
              <p className="text-sm font-medium">{formatLastSeen(agent.last_seen || '')}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Shield className="h-4 w-4 text-purple-600" />
            <div>
              <p className="text-xs text-muted-foreground">Version</p>
              <p className="text-sm font-medium">{agent.version || 'N/A'}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Network className="h-4 w-4 text-orange-600" />
            <div>
              <p className="text-xs text-muted-foreground">IP Address</p>
              <p className="text-sm font-medium">{agent.ip || 'N/A'}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2">
            <HardDrive className="h-4 w-4 text-indigo-600" />
            <div>
              <p className="text-xs text-muted-foreground">Platform</p>
              <p className="text-sm font-medium">{agent.os || 'Unknown'}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4 text-teal-600" />
            <div>
              <p className="text-xs text-muted-foreground">Tags</p>
              <p className="text-sm font-medium">{(agent.tags || []).length || 0}</p>
            </div>
          </div>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="system">System Info</TabsTrigger>
          <TabsTrigger value="commands">Commands</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {/* Agent Information */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Monitor className="h-5 w-5" />
                  Agent Information
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Hostname</span>
                    <span className="text-sm font-medium">{agent.hostname}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Agent ID</span>
                    <span className="text-sm font-mono text-xs bg-muted px-2 py-1 rounded">{agent.id}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">IP Address</span>
                    <span className="text-sm font-medium">{agent.ip || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Platform</span>
                    <span className="text-sm font-medium">{agent.os || 'Unknown'}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-muted-foreground">Version</span>
                    <span className="text-sm font-medium">{agent.version || 'N/A'}</span>
                  </div>
                </div>
                
                {agent.tags && agent.tags.length > 0 && (
                  <div className="space-y-2">
                    <span className="text-sm text-muted-foreground">Tags</span>
                    <div className="flex flex-wrap gap-1">
                      {agent.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Zap className="h-5 w-5" />
                  Quick Actions
                </CardTitle>
                <CardDescription>Execute common PowerShell commands</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2">
                <Dialog open={commandDialogOpen} onOpenChange={setCommandDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="w-full justify-start" disabled={agent.status !== 'online'}>
                      <Terminal className="mr-2 h-4 w-4" />
                      Custom Command
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-3xl">
                    <DialogHeader>
                      <DialogTitle>Execute PowerShell Command</DialogTitle>
                      <DialogDescription>
                        Execute a PowerShell command on {agent.hostname}
                      </DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label htmlFor="command">PowerShell Command</Label>
                        <Textarea
                          id="command"
                          placeholder="Enter PowerShell command..."
                          value={commandInput}
                          onChange={(e) => setCommandInput(e.target.value)}
                          rows={4}
                          className="font-mono"
                        />
                      </div>
                      
                      <div className="flex justify-end space-x-2">
                        <Button
                          variant="outline"
                          onClick={() => setCommandDialogOpen(false)}
                        >
                          Cancel
                        </Button>
                        <Button
                          onClick={executeCommand}
                          disabled={executingCommand || !commandInput.trim() || agent.status !== 'online'}
                        >
                          {executingCommand ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Executing...
                            </>
                          ) : (
                            <>
                              <Play className="mr-2 h-4 w-4" />
                              Execute
                            </>
                          )}
                        </Button>
                      </div>
                      
                      {commandResult && (
                        <div className="space-y-3 border-t pt-4">
                          <div className="flex items-center gap-2">
                            {commandResult.success ? (
                              <CheckCircle className="h-5 w-5 text-green-600" />
                            ) : (
                              <XCircle className="h-5 w-5 text-red-600" />
                            )}
                            <span className="font-medium">
                              {commandResult.success ? 'Command executed successfully' : 'Command failed'}
                            </span>
                            {commandResult.execution_time && (
                              <Badge variant="outline" className="ml-auto">
                                {commandResult.execution_time.toFixed(2)}s
                              </Badge>
                            )}
                          </div>
                          
                          {commandResult.output && (
                            <div className="space-y-2">
                              <Label className="text-sm font-medium">Output:</Label>
                              <pre className="text-xs bg-muted p-3 rounded-md border overflow-auto max-h-40 whitespace-pre-wrap">
                                {commandResult.output}
                              </pre>
                            </div>
                          )}
                          
                          {commandResult.error && (
                            <div className="space-y-2">
                              <Label className="text-sm font-medium text-red-600">Error:</Label>
                              <pre className="text-xs bg-red-50 dark:bg-red-950 p-3 rounded-md border overflow-auto max-h-40 whitespace-pre-wrap text-red-700 dark:text-red-300">
                                {commandResult.error}
                              </pre>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </DialogContent>
                </Dialog>

                {quickCommands.slice(0, 4).map((cmd, index) => (
                  <Button 
                    key={index}
                    variant="outline" 
                    className="w-full justify-start text-left h-auto py-2"
                    onClick={() => {
                      setCommandInput(cmd.command)
                      setCommandDialogOpen(true)
                    }}
                    disabled={agent.status !== 'online'}
                  >
                    <cmd.icon className="mr-2 h-4 w-4 flex-shrink-0" />
                    <div className="flex-1">
                      <div className="font-medium">{cmd.name}</div>
                      <div className="text-xs text-muted-foreground">{cmd.description}</div>
                    </div>
                  </Button>
                ))}
              </CardContent>
            </Card>

            {/* System Health */}
            {agent.system_info && (typeof agent.system_info === 'object') && Object.keys(agent.system_info).length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <BarChart3 className="h-5 w-5" />
                    System Health
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm flex items-center gap-2">
                        <Cpu className="h-4 w-4" />
                        CPU Usage
                      </span>
                      <span className="text-sm font-medium">{agent.system_info.cpu_usage ? agent.system_info.cpu_usage.toFixed(1) : '0.0'}%</span>
                    </div>
                    <Progress value={Number(agent.system_info.cpu_usage) || 0} className="h-2" />
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm flex items-center gap-2">
                        <Activity className="h-4 w-4" />
                        Memory Usage
                      </span>
                      <span className="text-sm font-medium">{agent.system_info.memory_usage ? agent.system_info.memory_usage.toFixed(1) : '0.0'}%</span>
                    </div>
                    <Progress value={Number(agent.system_info.memory_usage) || 0} className="h-2" />
                  </div>

                  {agent.system_info.uptime && (
                    <div className="flex items-center justify-between pt-2 border-t">
                      <span className="text-sm flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        Uptime
                      </span>
                      <span className="text-sm font-medium">{formatUptime(agent.system_info.uptime)}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="system" className="space-y-4">
          {agent.system_info && Object.keys(agent.system_info).length > 0 ? (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Cpu className="h-5 w-5" />
                    Processor
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Usage</span>
                      <span className="text-sm font-medium">{agent.system_info.cpu_usage ? agent.system_info.cpu_usage.toFixed(1) : '0.0'}%</span>
                    </div>
                    <Progress value={Number(agent.system_info.cpu_usage) || 0} className="h-2" />
                  </div>
                  {agent.system_info.cpu_name && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Model</span>
                      <span className="text-sm font-medium text-xs">{agent.system_info.cpu_name}</span>
                    </div>
                  )}
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Cores</span>
                    <span className="text-sm font-medium">{agent.system_info.cpu_count || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Architecture</span>
                    <span className="text-sm font-medium">{agent.system_info.architecture || 'N/A'}</span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Activity className="h-5 w-5" />
                    Memory
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Usage</span>
                      <span className="text-sm font-medium">{agent.system_info.memory_usage ? agent.system_info.memory_usage.toFixed(1) : '0.0'}%</span>
                    </div>
                    <Progress value={Number(agent.system_info.memory_usage) || 0} className="h-2" />
                  </div>
                  {agent.system_info.total_memory && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total</span>
                      <span className="text-sm font-medium">{(agent.system_info.total_memory / (1024 * 1024 * 1024)).toFixed(1)} GB</span>
                    </div>
                  )}
                  {agent.system_info.available_memory && (
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Available</span>
                      <span className="text-sm font-medium">{(agent.system_info.available_memory / (1024 * 1024 * 1024)).toFixed(1)} GB</span>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Network className="h-5 w-5" />
                    Network
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Hostname</span>
                    <span className="text-sm font-medium">{agent.hostname}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">IP Address</span>
                    <span className="text-sm font-medium">{agent.ip || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-muted-foreground">Platform</span>
                    <span className="text-sm font-medium">{agent.system_info.platform || agent.os || 'N/A'}</span>
                  </div>
                  {agent.system_info.network_adapters && agent.system_info.network_adapters.length > 0 && (
                    <div className="border-t pt-2 mt-2">
                      <span className="text-xs text-muted-foreground block mb-1">Active Adapters</span>
                      {agent.system_info.network_adapters.slice(0, 2).map((adapter, index) => (
                        <div key={index} className="text-xs">
                          <span className="font-medium">{adapter.name}:</span> {adapter.ip}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {agent.system_info.disk_usage && (
                <Card className="md:col-span-2 lg:col-span-3">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <HardDrive className="h-5 w-5" />
                      Disk Usage
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                      {Object.entries(agent.system_info.disk_usage).map(([drive, usage]) => (
                        <div key={drive} className="space-y-2">
                          <div className="flex justify-between">
                            <span className="text-sm text-muted-foreground">Drive {drive}</span>
                            <span className="text-sm font-medium">{usage && typeof usage === 'number' ? usage.toFixed(1) : '0.0'}%</span>
                          </div>
                          <Progress value={Number(usage) || 0} className="h-2" />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {agent.system_info.services && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Settings className="h-5 w-5" />
                      Services
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total</span>
                      <span className="text-sm font-medium">{agent.system_info.services.total || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Running</span>
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        {agent.system_info.services.running || 0}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Stopped</span>
                      <Badge variant="secondary">
                        {agent.system_info.services.stopped || 0}
                      </Badge>
                    </div>
                  </CardContent>
                </Card>
              )}

              {agent.system_info.process_count && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Processes
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Total Running</span>
                      <span className="text-sm font-medium">{agent.system_info.process_count}</span>
                    </div>
                  </CardContent>
                </Card>
              )}

              {agent.system_info.top_processes && agent.system_info.top_processes.length > 0 && (
                <Card className="md:col-span-2 lg:col-span-3">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <BarChart3 className="h-5 w-5" />
                      Top Processes by CPU
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {agent.system_info.top_processes.map((proc, index) => (
                        <div key={index} className="flex items-center justify-between p-2 border rounded">
                          <div className="flex items-center gap-3">
                            <Badge variant="outline">{index + 1}</Badge>
                            <div>
                              <div className="font-medium">{proc.name}</div>
                              <div className="text-xs text-muted-foreground">PID: {proc.id}</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-4">
                            <div className="text-right">
                              <div className="text-sm">CPU: {proc.cpu}s</div>
                              <div className="text-xs text-muted-foreground">RAM: {proc.memory_mb} MB</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Activity className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No system information available</h3>
                <p className="text-muted-foreground mb-4">System information is not available for this agent.</p>
                <Button onClick={handleRefresh} disabled={refreshing}>
                  <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                  Refresh
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="commands" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {quickCommands.map((cmd, index) => (
              <Card key={index} className="cursor-pointer hover:shadow-md transition-shadow">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <cmd.icon className="h-8 w-8 text-blue-600 flex-shrink-0 mt-1" />
                    <div className="flex-1">
                      <h3 className="font-medium mb-1">{cmd.name}</h3>
                      <p className="text-sm text-muted-foreground mb-3">{cmd.description}</p>
                      <Button 
                        size="sm" 
                        className="w-full"
                        onClick={() => {
                          setCommandInput(cmd.command)
                          setCommandDialogOpen(true)
                        }}
                        disabled={agent.status !== 'online'}
                      >
                        <Play className="h-3 w-3 mr-2" />
                        Execute
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Command History
              </CardTitle>
              <CardDescription>Recent commands executed on this agent</CardDescription>
            </CardHeader>
            <CardContent>
              {commandHistory.length > 0 ? (
                <div className="space-y-4">
                  {commandHistory.map((entry) => (
                    <div key={entry.id} className="border rounded-lg p-4 space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {entry.result.success ? (
                            <CheckCircle className="h-4 w-4 text-green-600" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-600" />
                          )}
                          <span className="font-mono text-sm">{entry.command}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">
                            {entry.result.execution_time?.toFixed(2) || '0.00'}s
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {new Date(entry.timestamp).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      
                      {entry.result.output && (
                        <pre className="text-xs bg-muted p-2 rounded overflow-auto max-h-32 whitespace-pre-wrap">
                          {entry.result.output}
                        </pre>
                      )}
                      
                      {entry.result.error && (
                        <pre className="text-xs bg-red-50 dark:bg-red-950 p-2 rounded overflow-auto max-h-32 whitespace-pre-wrap text-red-700 dark:text-red-300">
                          {entry.result.error}
                        </pre>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <History className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">No command history</h3>
                  <p className="text-muted-foreground">Commands executed on this agent will appear here.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}