import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import { ProtectedRoute } from './components/ProtectedRoute'
import { ErrorBoundary } from './components/common/ErrorBoundary'
import { RouteErrorBoundary } from './components/common/RouteErrorBoundary'
import { LandingPage } from './pages/LandingPage'
import { Login } from './pages/Login'
import { SignUp } from './pages/SignUp'
import { Search } from './pages/Search'
import { Dashboard } from './pages/Dashboard'
import { Settings } from './pages/Settings'
import { Admin } from './pages/Admin'

function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<SignUp />} />
            <Route
              path="/search"
              element={
                <ProtectedRoute>
                  <RouteErrorBoundary fallbackPath="/dashboard">
                    <Search />
                  </RouteErrorBoundary>
                </ProtectedRoute>
              }
            />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <RouteErrorBoundary fallbackPath="/search">
                    <Dashboard />
                  </RouteErrorBoundary>
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute>
                  <RouteErrorBoundary fallbackPath="/dashboard">
                    <Settings />
                  </RouteErrorBoundary>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin"
              element={
                <ProtectedRoute>
                  <RouteErrorBoundary fallbackPath="/dashboard">
                    <Admin />
                  </RouteErrorBoundary>
                </ProtectedRoute>
              }
            />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ErrorBoundary>
  )
}

export default App
