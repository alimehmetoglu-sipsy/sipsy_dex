import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://backend:8000'

export async function POST(request: NextRequest) {
  try {
    // Get agent configuration from request body
    const body = await request.json()
    
    // Forward request to backend installer endpoint
    const response = await fetch(`${BACKEND_URL}/api/v1/installer/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body)
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    // Get the exe file from backend
    const exeBuffer = await response.arrayBuffer()
    
    // Generate filename
    const agentName = body.agent_name || 'Windows'
    const filename = `DexAgent_${agentName}.exe`
    
    // Return exe file as download
    return new NextResponse(exeBuffer, {
      status: 200,
      headers: {
        'Content-Type': 'application/octet-stream',
        'Content-Disposition': `attachment; filename="${filename}"`,
        'Content-Length': exeBuffer.byteLength.toString(),
      },
    })

  } catch (error) {
    console.error('Agent download error:', error)
    return NextResponse.json({
      error: 'Failed to create agent installer',
      message: error instanceof Error ? error.message : 'Unknown error',
    }, { status: 500 })
  }
}

export async function GET() {
  return NextResponse.json({
    message: 'Direct .exe agent download endpoint',
    method: 'POST',
    description: 'Downloads a pre-built .exe file ready to run (requires Python + dependencies on target machine)',
    example: {
      server_url: 'ws://your-server:8080',
      api_token: 'your-api-token',
      agent_name: 'MyWindowsAgent',
      tags: ['windows', 'production'],
      auto_start: true,
      run_as_service: false
    }
  })
}