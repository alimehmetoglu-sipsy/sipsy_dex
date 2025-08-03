"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Activity, Monitor, Plus, Server, Terminal, Calendar, AlertTriangle, CheckCircle, Clock, Loader2 } from "lucide-react"
import { Progress } from "@/components/ui/progress"
import Link from "next/link"
import { apiClient, SystemInfo, Agent } from "@/lib/api"
import { useToast } from "@/hooks/use-toast"

function Dashboard() {
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null)
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const { toast } = useToast()

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        
        // Fetch system info and agents in parallel
        const [sysInfo, agentsData] = await Promise.all([
          apiClient.getSystemInfo().catch(() => null),
          apiClient.getAgents()
        ])
        
        setSystemInfo(sysInfo)
        setAgents(agentsData)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch data')
        toast({
          title: "Error",
          description: "Failed to load dashboard data",
          variant: "destructive",
        })
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [toast])

  const stats = {
    totalAgents: agents.length,
    onlineAgents: agents.filter(a => a.status === 'online').length,
    offlineAgents: agents.filter(a => a.status === 'offline').length,
    commandsToday: 89, // Mock data for now
    scheduledJobs: 23, // Mock data for now
    failedJobs: 3, // Mock data for now
  }

  const recentActivity = [
    {
      id: 1,
      action: "PowerShell command executed",
      target: "WS-001.domain.com",
      user: "admin",
      time: "2 minutes ago",
      status: "success",
    },
    {
      id: 2,
      action: "Agent went offline",
      target: "WS-045.domain.com",
      user: "system",
      time: "5 minutes ago",
      status: "warning",
    },
    {
      id: 3,
      action: "Scheduled job completed",
      target: "Group: Servers",
      user: "scheduler",
      time: "10 minutes ago",
      status: "success",
    },
  ]

  if (loading) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading dashboard...</span>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <AlertTriangle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-lg font-medium mb-2">Failed to load dashboard</h3>
            <p className="text-muted-foreground mb-4">{error}</p>
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
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Dashboard</h2>
            <p className="text-muted-foreground">Overview of your endpoint agents and recent activity</p>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Monitor className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalAgents}</div>
            <p className="text-xs text-muted-foreground">+12 from last month</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Online Agents</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.onlineAgents}</div>
            <Progress value={stats.totalAgents > 0 ? (stats.onlineAgents / stats.totalAgents) * 100 : 0} className="mt-2" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Commands Today</CardTitle>
            <Terminal className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.commandsToday}</div>
            <p className="text-xs text-muted-foreground">+23% from yesterday</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scheduled Jobs</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.scheduledJobs}</div>
            <div className="flex items-center gap-2 mt-2">
              <Badge variant="destructive" className="text-xs">
                {stats.failedJobs} failed
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      {systemInfo && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Server className="h-5 w-5" />
                System Health
              </CardTitle>
              <CardDescription>Current system status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm">CPU Usage</span>
                <Badge variant={systemInfo.cpu_usage > 80 ? "destructive" : "default"}>
                  {systemInfo.cpu_usage.toFixed(1)}%
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Memory Usage</span>
                <Badge variant={systemInfo.memory_usage > 80 ? "destructive" : "default"}>
                  {systemInfo.memory_usage.toFixed(1)}%
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm">Hostname</span>
                <Badge variant="secondary">{systemInfo.hostname}</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="h-5 w-5" />
                Quick Actions
              </CardTitle>
              <CardDescription>Common tasks and shortcuts</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button asChild className="w-full justify-start">
                <Link href="/commands/new">
                  <Terminal className="mr-2 h-4 w-4" />
                  Add Command
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start bg-transparent">
                <Link href="/schedules/new">
                  <Calendar className="mr-2 h-4 w-4" />
                  Create Scheduled Job
                </Link>
              </Button>
              <Button asChild variant="outline" className="w-full justify-start bg-transparent">
                <Link href="/agents">
                  <Monitor className="mr-2 h-4 w-4" />
                  View All Agents
                </Link>
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="h-5 w-5" />
                Recent Activity
              </CardTitle>
              <CardDescription>Latest system events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3">
                    <div className="mt-1">
                      {activity.status === "success" && <CheckCircle className="h-4 w-4 text-green-600" />}
                      {activity.status === "warning" && <AlertTriangle className="h-4 w-4 text-yellow-600" />}
                      {activity.status === "info" && <Clock className="h-4 w-4 text-blue-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">
                        {activity.target} • {activity.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Offline Agents Alert */}
      {stats.offlineAgents > 0 && (
        <Card className="border-yellow-200 bg-yellow-50 dark:border-yellow-800 dark:bg-yellow-950">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
              <AlertTriangle className="h-5 w-5" />
              Attention Required
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-yellow-700 dark:text-yellow-300">
              {stats.offlineAgents} agents are currently offline.
              <Button asChild variant="link" className="p-0 ml-1 text-yellow-800 dark:text-yellow-200">
                <Link href="/agents?filter=offline">View offline agents</Link>
              </Button>
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

// Export dashboard directly - protection handled by layout
export default Dashboard
