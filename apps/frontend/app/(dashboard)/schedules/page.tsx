"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Search, Plus, Play, Pause, Edit, Trash2, Clock, CheckCircle, AlertCircle, MoreHorizontal } from "lucide-react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const mockSchedules = [
  {
    id: "1",
    name: "Daily System Health Check",
    description: "Comprehensive system health monitoring across all production servers",
    command: "System Health Audit",
    schedule: "0 9 * * *",
    scheduleText: "Daily at 09:00",
    targetGroup: "Production Servers",
    targetCount: 12,
    status: "active",
    lastRun: "2024-01-15 09:00:00",
    lastStatus: "success",
    nextRun: "2024-01-16 09:00:00",
    createdBy: "admin",
    createdAt: "2024-01-01",
  },
  {
    id: "2",
    name: "Weekly Disk Cleanup",
    description: "Automated disk cleanup and temporary file removal",
    command: "Disk Space Cleanup",
    schedule: "0 2 * * 0",
    scheduleText: "Weekly on Sunday at 02:00",
    targetGroup: "All Workstations",
    targetCount: 89,
    status: "active",
    lastRun: "2024-01-14 02:00:00",
    lastStatus: "success",
    nextRun: "2024-01-21 02:00:00",
    createdBy: "admin",
    createdAt: "2024-01-01",
  },
  {
    id: "3",
    name: "Security Audit Scan",
    description: "Monthly security compliance and vulnerability assessment",
    command: "Security Audit",
    schedule: "0 1 1 * *",
    scheduleText: "Monthly on 1st at 01:00",
    targetGroup: "Critical Systems",
    targetCount: 25,
    status: "paused",
    lastRun: "2024-01-01 01:00:00",
    lastStatus: "failed",
    nextRun: "2024-02-01 01:00:00",
    createdBy: "security",
    createdAt: "2023-12-15",
  },
  {
    id: "4",
    name: "Event Log Collection",
    description: "Collect and analyze system event logs for anomalies",
    command: "Get Event Logs",
    schedule: "0 */6 * * *",
    scheduleText: "Every 6 hours",
    targetGroup: "Domain Controllers",
    targetCount: 4,
    status: "active",
    lastRun: "2024-01-15 12:00:00",
    lastStatus: "success",
    nextRun: "2024-01-15 18:00:00",
    createdBy: "soc",
    createdAt: "2024-01-10",
  },
]

export default function SchedulesPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")

  const filteredSchedules = mockSchedules.filter((schedule) => {
    const matchesSearch =
      schedule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      schedule.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      schedule.targetGroup.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || schedule.status === statusFilter
    return matchesSearch && matchesStatus
  })

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "paused":
        return <Pause className="h-4 w-4 text-yellow-600" />
      case "failed":
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-400" />
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
            Active
          </Badge>
        )
      case "paused":
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
            Paused
          </Badge>
        )
      case "failed":
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const getLastRunBadge = (status: string) => {
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
        return <Badge variant="outline">-</Badge>
    }
  }

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div className="flex items-center gap-4">
          <SidebarTrigger />
          <div>
            <h2 className="text-3xl font-bold tracking-tight">Scheduled Jobs</h2>
            <p className="text-muted-foreground">Manage automated PowerShell command execution</p>
          </div>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Create Schedule
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search schedules, commands, or target groups..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="paused">Paused</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Schedules Table */}
      <Card>
        <CardHeader>
          <CardTitle>Scheduled Jobs ({filteredSchedules.length})</CardTitle>
          <CardDescription>Automated PowerShell command execution schedules</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Command</TableHead>
                <TableHead>Schedule</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Run</TableHead>
                <TableHead>Next Run</TableHead>
                <TableHead className="w-12"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSchedules.map((schedule) => (
                <TableRow key={schedule.id}>
                  <TableCell>
                    <div>
                      <p className="font-medium">{schedule.name}</p>
                      <p className="text-sm text-muted-foreground line-clamp-1">{schedule.description}</p>
                    </div>
                  </TableCell>
                  <TableCell className="font-mono text-sm">{schedule.command}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      {schedule.scheduleText}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="font-medium">{schedule.targetGroup}</p>
                      <p className="text-sm text-muted-foreground">{schedule.targetCount} agents</p>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getStatusIcon(schedule.status)}
                      {getStatusBadge(schedule.status)}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <p className="text-sm">{schedule.lastRun}</p>
                      {getLastRunBadge(schedule.lastStatus)}
                    </div>
                  </TableCell>
                  <TableCell className="text-sm">{schedule.nextRun}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 w-8 p-0">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuLabel>Actions</DropdownMenuLabel>
                        <DropdownMenuItem>
                          <Play className="mr-2 h-4 w-4" />
                          Run Now
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Edit className="mr-2 h-4 w-4" />
                          Edit Schedule
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>
                          {schedule.status === "active" ? (
                            <>
                              <Pause className="mr-2 h-4 w-4" />
                              Pause
                            </>
                          ) : (
                            <>
                              <Play className="mr-2 h-4 w-4" />
                              Resume
                            </>
                          )}
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem className="text-red-600">
                          <Trash2 className="mr-2 h-4 w-4" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Schedules</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {filteredSchedules.filter((s) => s.status === "active").length}
            </div>
            <p className="text-xs text-muted-foreground">Currently running schedules</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Paused Schedules</CardTitle>
            <Pause className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {filteredSchedules.filter((s) => s.status === "paused").length}
            </div>
            <p className="text-xs text-muted-foreground">Temporarily disabled</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Jobs</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {filteredSchedules.filter((s) => s.lastStatus === "failed").length}
            </div>
            <p className="text-xs text-muted-foreground">Require attention</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
