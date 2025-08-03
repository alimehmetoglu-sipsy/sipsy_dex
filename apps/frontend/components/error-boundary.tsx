'use client'

import React from 'react'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import Link from 'next/link'

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
  errorInfo?: React.ErrorInfo
}

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ComponentType<ErrorFallbackProps>
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface ErrorFallbackProps {
  error: Error
  resetError: () => void
  errorInfo?: React.ErrorInfo
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo,
    })

    // Call onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo)
    }

    // In production, you might want to log this to an error reporting service
    if (process.env.NODE_ENV === 'production') {
      // Example: logErrorToService(error, errorInfo)
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined })
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback
      
      return (
        <FallbackComponent
          error={this.state.error!}
          resetError={this.resetError}
          errorInfo={this.state.errorInfo}
        />
      )
    }

    return this.props.children
  }
}

// Default error fallback component
export const DefaultErrorFallback: React.FC<ErrorFallbackProps> = ({ 
  error, 
  resetError, 
  errorInfo 
}) => {
  const isDevelopment = process.env.NODE_ENV === 'development'

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-8 w-8 text-destructive" />
            <div>
              <CardTitle className="text-2xl">Something went wrong</CardTitle>
              <CardDescription>
                An unexpected error occurred. Our team has been notified.
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {isDevelopment && (
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Error Details (Development Only):</h4>
              <div className="bg-muted p-3 rounded-md">
                <p className="text-sm font-mono text-destructive">
                  {error.name}: {error.message}
                </p>
                {error.stack && (
                  <details className="mt-2">
                    <summary className="text-sm cursor-pointer hover:underline">
                      Stack Trace
                    </summary>
                    <pre className="text-xs mt-2 whitespace-pre-wrap break-all text-muted-foreground">
                      {error.stack}
                    </pre>
                  </details>
                )}
                {errorInfo && (
                  <details className="mt-2">
                    <summary className="text-sm cursor-pointer hover:underline">
                      Component Stack
                    </summary>
                    <pre className="text-xs mt-2 whitespace-pre-wrap break-all text-muted-foreground">
                      {errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            </div>
          )}
          
          <div className="flex gap-3">
            <Button onClick={resetError} variant="default">
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
            <Button asChild variant="outline">
              <Link href="/">
                <Home className="h-4 w-4 mr-2" />
                Go Home
              </Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// Page-level error boundary for specific pages
export const PageErrorBoundary: React.FC<ErrorBoundaryProps> = ({ children, ...props }) => {
  return (
    <ErrorBoundary 
      fallback={PageErrorFallback}
      onError={(error, errorInfo) => {
        console.error('Page error:', error, errorInfo)
        // You could send this to an error tracking service
      }}
      {...props}
    >
      {children}
    </ErrorBoundary>
  )
}

const PageErrorFallback: React.FC<ErrorFallbackProps> = ({ error, resetError }) => {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-center h-64">
        <div className="text-center space-y-4">
          <AlertTriangle className="h-16 w-16 text-destructive mx-auto" />
          <div>
            <h3 className="text-lg font-medium mb-2">Page Error</h3>
            <p className="text-muted-foreground mb-4">
              This page encountered an error and couldn't load properly.
            </p>
            {process.env.NODE_ENV === 'development' && (
              <p className="text-sm text-destructive font-mono mb-4">
                {error.message}
              </p>
            )}
          </div>
          <div className="flex gap-2 justify-center">
            <Button onClick={resetError}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
            <Button asChild variant="outline">
              <Link href="/">
                <Home className="h-4 w-4 mr-2" />
                Go Home
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Hook for error handling in components
export const useErrorHandler = () => {
  return React.useCallback((error: Error, errorInfo?: string) => {
    console.error('Component error:', error, errorInfo)
    
    // In production, send to error tracking service
    if (process.env.NODE_ENV === 'production') {
      // logErrorToService(error, { info: errorInfo })
    }
  }, [])
}

// Async error boundary hook
export const useAsyncError = () => {
  const [, setError] = React.useState()
  
  return React.useCallback((error: Error) => {
    setError(() => {
      throw error
    })
  }, [setError])
}