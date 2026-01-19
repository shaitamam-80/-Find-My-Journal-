import { cn } from '../../lib/utils'

interface SkeletonProps {
  className?: string
}

/**
 * Animated skeleton placeholder for loading states.
 * Use instead of spinners for a more polished UX.
 */
export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={cn(
        'animate-pulse rounded-md bg-slate-200 dark:bg-slate-700',
        className
      )}
    />
  )
}

/**
 * Skeleton for text content - a single line placeholder
 */
export function SkeletonText({ className }: SkeletonProps) {
  return <Skeleton className={cn('h-4 w-full', className)} />
}

/**
 * Skeleton for a card component
 */
export function SkeletonCard({ className }: SkeletonProps) {
  return (
    <div className={cn('bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6', className)}>
      <div className="space-y-4">
        <Skeleton className="h-6 w-3/4" />
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
        <div className="flex gap-2 pt-2">
          <Skeleton className="h-8 w-20 rounded-full" />
          <Skeleton className="h-8 w-24 rounded-full" />
        </div>
      </div>
    </div>
  )
}

/**
 * Skeleton for stats cards (Dashboard)
 */
export function SkeletonStats() {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {[...Array(4)].map((_, i) => (
        <div key={i} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
          <div className="flex items-center justify-between mb-4">
            <Skeleton className="h-10 w-10 rounded-lg" />
            <Skeleton className="h-5 w-16 rounded-full" />
          </div>
          <Skeleton className="h-8 w-20 mb-2" />
          <Skeleton className="h-4 w-24" />
        </div>
      ))}
    </div>
  )
}

/**
 * Skeleton for a table row (Admin)
 */
export function SkeletonTableRow() {
  return (
    <tr className="border-b border-slate-100 dark:border-slate-700">
      <td className="px-6 py-4">
        <div className="space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-3 w-48" />
        </div>
      </td>
      <td className="px-6 py-4">
        <Skeleton className="h-6 w-16 rounded-full" />
      </td>
      <td className="px-6 py-4">
        <Skeleton className="h-6 w-20 rounded-full" />
      </td>
      <td className="px-6 py-4">
        <Skeleton className="h-4 w-8" />
      </td>
      <td className="px-6 py-4">
        <Skeleton className="h-4 w-24" />
      </td>
      <td className="px-6 py-4 text-end">
        <Skeleton className="h-8 w-20 ms-auto" />
      </td>
    </tr>
  )
}

/**
 * Skeleton for Admin table
 */
export function SkeletonTable() {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead className="bg-slate-50 dark:bg-slate-700/50">
          <tr>
            {['User', 'Tier', 'Status', 'Searches', 'Joined', 'Actions'].map((header) => (
              <th key={header} className="px-6 py-3 text-start text-xs font-semibold text-slate-600 dark:text-slate-300 uppercase tracking-wider">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {[...Array(5)].map((_, i) => (
            <SkeletonTableRow key={i} />
          ))}
        </tbody>
      </table>
    </div>
  )
}

/**
 * Skeleton for Settings form
 */
export function SkeletonForm() {
  return (
    <div className="space-y-6">
      {[...Array(5)].map((_, i) => (
        <div key={i} className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-12 w-full rounded-xl" />
        </div>
      ))}
      <Skeleton className="h-14 w-full rounded-xl mt-8" />
    </div>
  )
}

/**
 * Skeleton for journal search results
 */
export function SkeletonJournalCard() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 space-y-2">
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </div>
        <Skeleton className="h-12 w-12 rounded-full ms-4" />
      </div>
      <div className="space-y-3">
        <Skeleton className="h-4 w-full" />
        <Skeleton className="h-4 w-5/6" />
      </div>
      <div className="flex gap-2 mt-4">
        <Skeleton className="h-6 w-16 rounded-full" />
        <Skeleton className="h-6 w-20 rounded-full" />
        <Skeleton className="h-6 w-14 rounded-full" />
      </div>
    </div>
  )
}

/**
 * Skeleton for search results list
 */
export function SkeletonSearchResults() {
  return (
    <div className="space-y-4">
      {[...Array(3)].map((_, i) => (
        <SkeletonJournalCard key={i} />
      ))}
    </div>
  )
}

/**
 * Skeleton for full page loading
 */
export function SkeletonPage() {
  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
      <div className="text-center space-y-4">
        <Skeleton className="h-12 w-12 rounded-full mx-auto" />
        <Skeleton className="h-4 w-32 mx-auto" />
      </div>
    </div>
  )
}
