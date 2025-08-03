"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Plus, X } from "lucide-react"
import { SavedPowerShellCommand, CommandParameter } from "@/lib/api"

interface CreateCommandFormProps {
  onSubmit: (command: SavedPowerShellCommand) => void
  onCancel: () => void
  initialData?: SavedPowerShellCommand
}

const categories = [
  { id: "general", name: "General" },
  { id: "system", name: "System Information" },
  { id: "network", name: "Network" },
  { id: "disk", name: "Disk & Storage" },
  { id: "security", name: "Security" },
  { id: "monitoring", name: "Monitoring" },
]

const parameterTypes = [
  { id: "string", name: "Text" },
  { id: "number", name: "Number" },
  { id: "boolean", name: "Boolean" },
]

export default function CreateCommandForm({ onSubmit, onCancel, initialData }: CreateCommandFormProps) {
  const [formData, setFormData] = useState<SavedPowerShellCommand>(
    initialData || {
      name: "",
      description: "",
      category: "general", 
      command: "",
      parameters: [],
      tags: [],
      version: "1.0",
      author: "User",
    }
  )
  
  const [currentTag, setCurrentTag] = useState("")
  const [newParameter, setNewParameter] = useState<CommandParameter>({
    name: "",
    type: "string",
    default: "",
    description: "",
    required: false
  })

  const addTag = () => {
    if (currentTag.trim() && !formData.tags.includes(currentTag.trim())) {
      setFormData({
        ...formData,
        tags: [...formData.tags, currentTag.trim()]
      })
      setCurrentTag("")
    }
  }

  const removeTag = (tagToRemove: string) => {
    setFormData({
      ...formData,
      tags: formData.tags.filter(tag => tag !== tagToRemove)
    })
  }

  const addParameter = () => {
    if (newParameter.name.trim()) {
      setFormData({
        ...formData,
        parameters: [...formData.parameters, { ...newParameter }]
      })
      setNewParameter({
        name: "",
        type: "string",
        default: "",
        description: "",
        required: false
      })
    }
  }

  const removeParameter = (index: number) => {
    setFormData({
      ...formData,
      parameters: formData.parameters.filter((_, i) => i !== index)
    })
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (formData.name.trim() && formData.command.trim()) {
      onSubmit(formData)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="name">Command Name *</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Get System Information"
            required
          />
        </div>
        <div>
          <Label htmlFor="category">Category</Label>
          <Select 
            value={formData.category} 
            onValueChange={(value) => setFormData({ ...formData, category: value })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {categories.map(cat => (
                <SelectItem key={cat.id} value={cat.id}>{cat.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      <div>
        <Label htmlFor="description">Description</Label>
        <Textarea
          id="description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="Describe what this command does..."
          rows={2}
        />
      </div>

      <div>
        <Label htmlFor="command">PowerShell Command *</Label>
        <Textarea
          id="command"
          value={formData.command}
          onChange={(e) => setFormData({ ...formData, command: e.target.value })}
          placeholder="Get-ComputerInfo | ConvertTo-Json"
          className="font-mono"
          rows={4}
          required
        />
        <p className="text-xs text-muted-foreground mt-1">
          Use $ParameterName for parameters. Always include | ConvertTo-Json for structured output.
        </p>
      </div>

      {/* Parameters Section */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Parameters</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.parameters.length > 0 && (
            <div className="space-y-2">
              {formData.parameters.map((param, index) => (
                <div key={index} className="flex items-center justify-between p-2 border rounded">
                  <div>
                    <span className="font-medium">${param.name}</span>
                    <Badge variant="outline" className="ml-2 text-xs">{param.type}</Badge>
                    {param.required && <Badge variant="destructive" className="ml-1 text-xs">Required</Badge>}
                    {param.description && (
                      <p className="text-xs text-muted-foreground">{param.description}</p>
                    )}
                  </div>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeParameter(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          <div className="grid grid-cols-3 gap-2">
            <Input
              placeholder="Parameter name"
              value={newParameter.name}
              onChange={(e) => setNewParameter({ ...newParameter, name: e.target.value })}
            />
            <Select
              value={newParameter.type}
              onValueChange={(value: 'string' | 'number' | 'boolean') => 
                setNewParameter({ ...newParameter, type: value })
              }
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {parameterTypes.map(type => (
                  <SelectItem key={type.id} value={type.id}>{type.name}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Input
              placeholder="Default value"
              value={newParameter.default}
              onChange={(e) => setNewParameter({ ...newParameter, default: e.target.value })}
            />
          </div>
          <Input
            placeholder="Parameter description"
            value={newParameter.description}
            onChange={(e) => setNewParameter({ ...newParameter, description: e.target.value })}
          />
          <Button type="button" onClick={addParameter} size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Add Parameter
          </Button>
        </CardContent>
      </Card>

      {/* Tags Section */}
      <div>
        <Label>Tags</Label>
        <div className="flex gap-2 mb-2">
          <Input
            value={currentTag}
            onChange={(e) => setCurrentTag(e.target.value)}
            placeholder="Add a tag..."
            onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
          />
          <Button type="button" onClick={addTag} size="sm">
            <Plus className="h-4 w-4" />
          </Button>
        </div>
        <div className="flex flex-wrap gap-1">
          {formData.tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="ml-1 h-auto p-0 hover:bg-transparent"
                onClick={() => removeTag(tag)}
              >
                <X className="h-3 w-3" />
              </Button>
            </Badge>
          ))}
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit">
          {initialData ? "Update Command" : "Create Command"}
        </Button>
      </div>
    </form>
  )
}