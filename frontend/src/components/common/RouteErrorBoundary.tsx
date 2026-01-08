import { Component, type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { AlertTriangle, Home, RefreshCw } from 'lucide-react'

interface RouteErrorBoundaryProps {
  children: ReactNode
  fallbackPath?: string
}

interface RouteErrorBoundaryState {
  hasError: boolean
  error: Error | null
}

/**
 * Route-level Error Boundary component.
 * Catches errors within a specific route without crashing the entire app.
 * Provides retry and navigation options.
 */
export class RouteErrorBoundary extends Component<RouteErrorBoundaryProps, RouteErrorBoundaryState> {
  constructor(props: RouteErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): RouteErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error to console in development
    console.error('RouteErrorBoundary caught an error:', error, errorInfo)

    // TODO: Send error to logging service in production
  }

  handleRetry = (): void => {
    this.setState({ hasError: false, error: null })
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="min-h-[60vh] flex items-center justify-center p-6">
          <div className="max-w-md w-full bg-white dark:bg-slate-800 rounded-2xl shadow-sm border border-slate-200 dark:border-slate-700 p-8 text-center">
            <div className="w-14 h-14 bg-amber-100 dark:bg-amber-900/30 rounded-full flex items-center justify-center mx-auto mb-5">
              <AlertTriangle className="w-7 h-7 text-amber-600 dark:text-amber-400" />
            </div>

            <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">
              Something went wrong
            </h2>

            <p className="text-slate-600 dark:text-slate-400 mb-6">
              We encountered an error loading this page. Please try again.
            </p>

            {/* Show error details in development */}
            {import.meta.env.DEV && this.state.error && (
              <div className="bg-slate-50 dark:bg-slate-700 rounded-lg p-3 mb-6 text-left">
                <p className="text-xs font-mono text-red-600 dark:text-red-400 break-all">
                  {this.state.error.message}
                </p>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={this.handleRetry}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-slate-900 dark:bg-teal-600 text-white font-semibold rounded-xl hover:bg-slate-800 dark:hover:bg-teal-500 transition-colors"
              >
                <RefreshCw className="w-4 h-4" />
                Try Again
              </button>

              <Link
                to={this.props.fallbackPath || '/'}
                className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-semibold rounded-xl hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
              >
                <Home className="w-4 h-4" />
                Go Home
              </Link>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

export default RouteErrorBoundary
