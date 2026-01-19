import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { SkeletonPage } from './ui/Skeleton'

interface ProtectedRouteProps {
  children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { user, loading } = useAuth()

  if (loading) {
    return <SkeletonPage />
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}
