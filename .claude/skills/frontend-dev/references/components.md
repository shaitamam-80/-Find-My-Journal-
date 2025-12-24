# Component Patterns Reference

## Skeleton Loading Components

```tsx
// components/ui/Skeleton.tsx
interface SkeletonProps {
  className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
  return (
    <div 
      className={`animate-pulse bg-slate-200 rounded ${className}`}
      aria-hidden="true"
    />
  )
}

// Specific skeletons
export function CardSkeleton() {
  return (
    <div className="bg-white rounded-xl border p-6 space-y-4">
      <Skeleton className="h-6 w-3/4" />
      <Skeleton className="h-4 w-1/2" />
      <div className="flex gap-2">
        <Skeleton className="h-6 w-16 rounded-full" />
        <Skeleton className="h-6 w-20 rounded-full" />
      </div>
    </div>
  )
}

export function TableRowSkeleton() {
  return (
    <tr className="border-b">
      <td className="p-4"><Skeleton className="h-4 w-32" /></td>
      <td className="p-4"><Skeleton className="h-4 w-24" /></td>
      <td className="p-4"><Skeleton className="h-4 w-16" /></td>
    </tr>
  )
}

// Usage pattern
function JournalList({ isLoading, data }) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => <CardSkeleton key={i} />)}
      </div>
    )
  }
  
  return data.map(journal => <JournalCard key={journal.id} {...journal} />)
}
```

## Advanced Component Patterns

### Modal Component

```tsx
// components/ui/Modal.tsx
import { useEffect, useRef } from 'react'
import { createPortal } from 'react-dom'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  children: React.ReactNode
}

export function Modal({ isOpen, onClose, title, children }: ModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    
    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }
    
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return createPortal(
    <div
      ref={overlayRef}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={(e) => e.target === overlayRef.current && onClose()}
    >
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-auto">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">{title}</h2>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded"
          >
            ✕
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </div>,
    document.body
  )
}
```

### Dropdown Menu

```tsx
// components/ui/Dropdown.tsx
import { useState, useRef, useEffect } from 'react'

interface DropdownProps {
  trigger: React.ReactNode
  items: { label: string; onClick: () => void }[]
}

export function Dropdown({ trigger, items }: DropdownProps) {
  const [isOpen, setIsOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  return (
    <div ref={ref} className="relative">
      <div onClick={() => setIsOpen(!isOpen)}>{trigger}</div>
      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border z-50">
          {items.map((item, i) => (
            <button
              key={i}
              onClick={() => { item.onClick(); setIsOpen(false) }}
              className="w-full px-4 py-2 text-left hover:bg-gray-100 first:rounded-t-lg last:rounded-b-lg"
            >
              {item.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
```

### Toast Notifications

```tsx
// hooks/useToast.tsx
import { createContext, useContext, useState, useCallback } from 'react'

type ToastType = 'success' | 'error' | 'info'

interface Toast {
  id: string
  message: string
  type: ToastType
}

interface ToastContextValue {
  toasts: Toast[]
  addToast: (message: string, type?: ToastType) => void
  removeToast: (id: string) => void
}

const ToastContext = createContext<ToastContextValue | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = Date.now().toString()
    setToasts(prev => [...prev, { id, message, type }])
    setTimeout(() => removeToast(id), 5000)
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast must be used within ToastProvider')
  return context
}

function ToastContainer({ toasts, onRemove }: { toasts: Toast[]; onRemove: (id: string) => void }) {
  const colors = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-blue-500'
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <div
          key={toast.id}
          className={`${colors[toast.type]} text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2`}
        >
          {toast.message}
          <button onClick={() => onRemove(toast.id)}>✕</button>
        </div>
      ))}
    </div>
  )
}
```

### Data Table with Sorting

```tsx
// components/ui/DataTable.tsx
import { useState, useMemo } from 'react'

interface Column<T> {
  key: keyof T
  header: string
  sortable?: boolean
  render?: (value: T[keyof T], row: T) => React.ReactNode
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  onRowClick?: (row: T) => void
}

export function DataTable<T extends { id: string | number }>({
  data,
  columns,
  onRowClick
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<keyof T | null>(null)
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc')

  const sortedData = useMemo(() => {
    if (!sortKey) return data
    return [...data].sort((a, b) => {
      const aVal = a[sortKey]
      const bVal = b[sortKey]
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1
      return 0
    })
  }, [data, sortKey, sortDir])

  const handleSort = (key: keyof T) => {
    if (sortKey === key) {
      setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    } else {
      setSortKey(key)
      setSortDir('asc')
    }
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="bg-gray-50 border-b">
            {columns.map(col => (
              <th
                key={String(col.key)}
                onClick={() => col.sortable && handleSort(col.key)}
                className={`px-4 py-3 text-left font-medium text-gray-600 ${col.sortable ? 'cursor-pointer hover:bg-gray-100' : ''}`}
              >
                {col.header}
                {sortKey === col.key && (sortDir === 'asc' ? ' ↑' : ' ↓')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {sortedData.map(row => (
            <tr
              key={row.id}
              onClick={() => onRowClick?.(row)}
              className={`border-b hover:bg-gray-50 ${onRowClick ? 'cursor-pointer' : ''}`}
            >
              {columns.map(col => (
                <td key={String(col.key)} className="px-4 py-3">
                  {col.render ? col.render(row[col.key], row) : String(row[col.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Infinite Scroll

```tsx
// hooks/useInfiniteScroll.ts
import { useEffect, useRef, useCallback } from 'react'

export function useInfiniteScroll(
  loadMore: () => void,
  hasMore: boolean,
  isLoading: boolean
) {
  const observerRef = useRef<IntersectionObserver | null>(null)
  
  const lastElementRef = useCallback((node: HTMLElement | null) => {
    if (isLoading) return
    if (observerRef.current) observerRef.current.disconnect()
    
    observerRef.current = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        loadMore()
      }
    })
    
    if (node) observerRef.current.observe(node)
  }, [isLoading, hasMore, loadMore])

  return lastElementRef
}

// Usage:
function JournalList() {
  const { data, loadMore, hasMore, isLoading } = useJournals()
  const lastRef = useInfiniteScroll(loadMore, hasMore, isLoading)

  return (
    <ul>
      {data.map((journal, i) => (
        <li
          key={journal.id}
          ref={i === data.length - 1 ? lastRef : undefined}
        >
          {journal.title}
        </li>
      ))}
      {isLoading && <LoadingSpinner />}
    </ul>
  )
}
```

### Debounced Search Input

```tsx
// hooks/useDebounce.ts
import { useState, useEffect } from 'react'

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value)

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])

  return debouncedValue
}

// Usage in component:
function SearchInput({ onSearch }: { onSearch: (q: string) => void }) {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 300)

  useEffect(() => {
    if (debouncedQuery) onSearch(debouncedQuery)
  }, [debouncedQuery, onSearch])

  return (
    <input
      value={query}
      onChange={e => setQuery(e.target.value)}
      placeholder="Search..."
    />
  )
}
```

## Form Patterns

### Controlled Form with React Hook Form

```tsx
// Using react-hook-form (recommended for complex forms)
import { useForm } from 'react-hook-form'

interface FormData {
  title: string
  abstract: string
  keywords: string
}

function JournalSearchForm({ onSubmit }: { onSubmit: (data: FormData) => void }) {
  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>()

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Title</label>
        <input
          {...register('title', { required: 'Title is required', minLength: { value: 10, message: 'Min 10 chars' } })}
          className="w-full px-4 py-2 border rounded-lg"
        />
        {errors.title && <p className="text-red-500 text-sm mt-1">{errors.title.message}</p>}
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Abstract</label>
        <textarea
          {...register('abstract', { required: 'Abstract is required', minLength: { value: 50, message: 'Min 50 chars' } })}
          rows={5}
          className="w-full px-4 py-2 border rounded-lg"
        />
        {errors.abstract && <p className="text-red-500 text-sm mt-1">{errors.abstract.message}</p>}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="px-6 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50"
      >
        {isSubmitting ? 'Searching...' : 'Find Journals'}
      </button>
    </form>
  )
}
```

## API Integration Patterns

### TanStack Query Setup

```tsx
// lib/queryClient.ts
import { QueryClient } from '@tanstack/react-query'

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1
    }
  }
})

// hooks/useJournals.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { searchJournals, saveJournal } from '@/services/journals'

export function useJournalSearch(query: string) {
  return useQuery({
    queryKey: ['journals', query],
    queryFn: () => searchJournals(query),
    enabled: query.length > 0
  })
}

export function useSaveJournal() {
  const queryClient = useQueryClient()
  
  return useMutation({
    mutationFn: saveJournal,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['saved-journals'] })
    }
  })
}
```


## Component Optimization

### memo Pattern

```tsx
import { memo, useCallback, useMemo } from 'react'

// Memoized component - only re-renders when props change
const JournalCard = memo(function JournalCard({ 
  journal, 
  onSave,
  onExpand 
}: JournalCardProps) {
  return (
    <div className="bg-white rounded-xl border p-6">
      <h3>{journal.title}</h3>
      <button onClick={() => onSave(journal.id)}>Save</button>
    </div>
  )
})

// Parent component with stable callbacks
function JournalList({ journals }: { journals: Journal[] }) {
  const [saved, setSaved] = useState<Set<string>>(new Set())

  // ✅ Stable callback reference
  const handleSave = useCallback((id: string) => {
    setSaved(prev => new Set(prev).add(id))
  }, [])

  // ✅ Memoized expensive computation
  const sortedJournals = useMemo(() => 
    [...journals].sort((a, b) => b.impactFactor - a.impactFactor),
    [journals]
  )

  return (
    <div className="space-y-4">
      {sortedJournals.map(journal => (
        <JournalCard 
          key={journal.id}
          journal={journal}
          onSave={handleSave}  // Stable reference
        />
      ))}
    </div>
  )
}
```

### When to Optimize

```
✅ DO use memo when:
- Component receives complex objects as props
- Parent re-renders frequently
- Component is expensive to render
- List items in a long list

❌ DON'T use memo when:
- Component is simple/cheap to render
- Props change on every render anyway
- Premature optimization
```

## Error Handling Patterns

### Error Boundary with Recovery

```tsx
import { ErrorBoundary } from 'react-error-boundary'

function ErrorFallback({ error, resetErrorBoundary }: FallbackProps) {
  return (
    <div className="p-6 bg-red-50 border border-red-200 rounded-xl text-center">
      <div className="text-red-500 text-4xl mb-4">⚠️</div>
      <h2 className="text-red-800 font-semibold text-lg">
        Something went wrong
      </h2>
      <p className="text-red-600 text-sm mt-2 mb-4">
        {error.message}
      </p>
      <button
        onClick={resetErrorBoundary}
        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
      >
        Try again
      </button>
    </div>
  )
}

// Usage - wrap risky components
function App() {
  return (
    <ErrorBoundary 
      FallbackComponent={ErrorFallback}
      onReset={() => window.location.reload()}
    >
      <SearchPage />
    </ErrorBoundary>
  )
}

// Per-component error boundary
function SafeJournalCard({ journal }: Props) {
  return (
    <ErrorBoundary fallback={<div>Failed to load journal</div>}>
      <JournalCard journal={journal} />
    </ErrorBoundary>
  )
}
```
