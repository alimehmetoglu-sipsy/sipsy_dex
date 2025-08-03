"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Activity,
  Search,
  Filter,
  Download,
  Calendar,
  User,
  Terminal,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { DatePickerWithRange } from "@/components/ui/date-range-picker"

const mockAuditLogs = [
  {
    id: "1",
    timestamp: "2024-01-15 14:30:15",
    user: "admin",
    action: "Command Executed",
    target: "WS-001.domain.com",
    command: "Get-EventLog",
    parameters: "-LogName System -Newest 100",
    status: "success",
    duration: "2.3s",
    ipAddress: "192.168.1.100",
  },
  {
    id: "2",
    timestamp: "2024-01-15 14:25:42",
    user: "admin",
    action: "Schedule Created",
    target: "Production Servers",
    command: "Daily Health Check",
    parameters: "Schedule: 0 9 * * *",
    status: "success",
    duration: "-",
    ipAddress: "192.168.1.100",
  },
  {
    id: "3",
    timestamp: "2024-01-15 13:45:18",
    user: "soc_analyst",
    action: "Command Executed",
    target: "SRV-001.domain.com",
    command: "Get-Process",
    parameters: "-Name suspicious*",
    status: "failed",
    duration: "timeout",
    ipAddress: "192.168.1.105",
  },
  {
    id: "4",
    timestamp: "2024-01-15 13:30:05",
    user: "scheduler",
    action: "Scheduled Job Run",
    target: "All Workstations",
    command: "Disk Cleanup",
    parameters: "Auto-scheduled execution",
    status: "partial",
    duration: "45.2s",
    ipAddress: "system",
  },
  {
    id: "5",
    timestamp: "2024-01-15 12:15:33",
    user: "admin",
    action: "Agent Registration",
    target: "WS-099.domain.com",
    command: "-",
    parameters: "New agent registered",
    status: "success",
    duration: "-",
    ipAddress: "192.168.1.199",
  },
  {
    id: "6",
    timestamp: "2024-01-15 11:45:22",
    user: "security_admin",
    action: "Command Library Updated",
    target: "Security Audit v1.3",
    command: "Security Audit",
    parameters: "Command updated with new checks",
    status: "success",
    duration: "-",
    ipAddress: "192.168.1.102",
  },
]

export default function AuditLogsPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [actionFilter, setActionFilter] = useState("all")
  const [statusFilter, setStatusFilter] = useState("all")
  const [userFilter, setUserFilter] = useState("all")

  const filteredLogs = mockAuditLogs.filter((log) => {
    const matchesSearch =
      log.user.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.action.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.target.toLowerCase().includes(searchTerm.toLowerCase()) ||
      log.command.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesAction = actionFilter === "all" || log.action.toLowerCase().includes(actionFilter.toLowerCase())
    const matchesStatus = statusFilter === "all" || log.status === statusFilter
    const matchesUser = userFilter === "all" || log.user === userFilter
    return matchesSearch && matchesAction && matchesStatus && matchesUser
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "failed":
        return <XCircle className="h-4 w-4 text-red-600" />
      case "partial":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "success":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Success
          </Badge>
        )
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      case "partial":
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
            Partial
          </Badge>
        )
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getActionIcon = (action: string) => {
    if (action.includes("Command")) return <Terminal className="h-4 w-4" />
    if (action.includes("Schedule")) return <Calendar className="h-4 w-4" />
    if (action.includes("Agent")) return <User className="h-4 w-4" />
    return <Activity className="h-4 w-4" />
  }

  const uniqueUsers = [...new Set(mockAuditLogs.map((log) => log.user))]

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Audit Logs</h2>
            <p className="text-muted-foreground">Track all system activities and user actions</p>
          </div>
        </div>
        <Button>
          <Download className="mr-2 h-4 w-4" />
          Export Logs
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Search
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <div className="relative">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>

            <Select value={actionFilter} onValueChange={setActionFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by action" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Actions</SelectItem>
                <SelectItem value="command">Command Executed</SelectItem>
                <SelectItem value="schedule">Schedule Actions</SelectItem>
                <SelectItem value="agent">Agent Actions</SelectItem>
                <SelectItem value="library">Library Updates</SelectItem>
              </SelectContent>
            </Select>

            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="partial">Partial</SelectItem>
              </SelectContent>
            </Select>

            <Select value={userFilter} onValueChange={setUserFilter}>
              <SelectTrigger>
                <SelectValue placeholder="Filter by user" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Users</SelectItem>
                {uniqueUsers.map((user) => (
                  <SelectItem key={user} value={user}>
                    {user}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <DatePickerWithRange />
          </div>
        </CardContent>
      </Card>

      {/* Activity Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Activities</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{filteredLogs.length}</div>
            <p className="text-xs text-muted-foreground">In selected timeframe</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Successful</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {filteredLogs.filter((log) => log.status === "success").length}
            </div>
            <p className="text-xs text-muted-foreground">Completed successfully</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {filteredLogs.filter((log) => log.status === "failed").length}
            </div>
            <p className="text-xs text-muted-foreground">Failed executions</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <User className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{uniqueUsers.length}</div>
            <p className="text-xs text-muted-foreground">Unique users today</p>
          </CardContent>
        </Card>
      </div>

      {/* Audit Logs Table */}
      <Card>
        <CardHeader>
          <CardTitle>Activity Log ({filteredLogs.length})</CardTitle>
          <CardDescription>Detailed record of all system activities and user actions</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Timestamp</TableHead>
                <TableHead>User</TableHead>
                <TableHead>Action</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Command</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Duration</TableHead>
                <TableHead>IP Address</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map((log) => (
                <TableRow key={log.id}>
                  <TableCell className="font-mono text-sm">{log.timestamp}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4 text-muted-foreground" />
                      {log.user}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getActionIcon(log.action)}
                      {log.action}
                    </div>
                  </TableCell>
                  <TableCell className="font-medium">{log.target}</TableCell>
                  <TableCell>
                    <div>
                      <p className="font-mono text-sm">{log.command}</p>
                      {log.parameters && <p className="text-xs text-muted-foreground line-clamp-1">{log.parameters}</p>}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(log.status)}
                      {getStatusBadge(log.status)}
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-sm">{log.duration}</TableCell>
                  <TableCell className="font-mono text-sm">{log.ipAddress}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
