import { useState, useMemo, useCallback } from 'react'
import { api } from '../services/api'
import type { SearchResponse, Journal } from '../types'
import {
  type FilterType,
  type AIAnalysis,
  buildAIAnalysis,
  groupJournalsByCategory,
  filterJournals,
} from '../utils/searchResultsMapper'

interface SearchFormData {
  title: string
  abstract: string
  keywords: string[]
  preferOA: boolean
}

interface UseJournalSearchOptions {
  sessionToken: string | null
  onSearchComplete?: () => void
}

interface UseJournalSearchReturn {
  // State
  results: SearchResponse | null
  loading: boolean
  error: string | null

  // Derived data
  aiAnalysis: AIAnalysis | null
  filteredJournals: Journal[]
  groupedJournals: Record<string, Journal[]>

  // Filter
  activeFilter: FilterType
  setActiveFilter: (filter: FilterType) => void

  // Expanded cards
  expandedCardIds: Set<string>
  toggleCard: (id: string) => void

  // Actions
  search: (data: SearchFormData) => Promise<void>
  reset: () => void

  // Export helpers
  exportCSV: () => void
}

/**
 * Custom hook for managing journal search state and operations.
 *
 * Extracts all search-related logic from the Search page component
 * for better separation of concerns and reusability.
 *
 * @example
 * ```tsx
 * const { search, results, loading, error, filteredJournals } = useJournalSearch({
 *   sessionToken: session?.access_token ?? null,
 *   onSearchComplete: refreshLimits,
 * })
 *
 * const handleSubmit = async (e: React.FormEvent) => {
 *   e.preventDefault()
 *   await search({ title, abstract, keywords: keywordList, preferOA })
 * }
 * ```
 */
export function useJournalSearch({
  sessionToken,
  onSearchComplete,
}: UseJournalSearchOptions): UseJournalSearchReturn {
  // Core state
  const [results, setResults] = useState<SearchResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // UI state
  const [expandedCardIds, setExpandedCardIds] = useState<Set<string>>(new Set())
  const [activeFilter, setActiveFilter] = useState<FilterType>('all')

  // Store form data for AI analysis
  const [lastFormData, setLastFormData] = useState<SearchFormData | null>(null)

  // Derived: AI Analysis
  const aiAnalysis = useMemo((): AIAnalysis | null => {
    if (!results || !lastFormData) return null
    return buildAIAnalysis(
      { title: lastFormData.title, keywords: lastFormData.keywords },
      results
    )
  }, [results, lastFormData])

  // Derived: Filtered journals
  const filteredJournals = useMemo((): Journal[] => {
    if (!results?.journals) return []
    return filterJournals(results.journals, activeFilter)
  }, [results?.journals, activeFilter])

  // Derived: Grouped journals by category
  const groupedJournals = useMemo(() => {
    return groupJournalsByCategory(filteredJournals)
  }, [filteredJournals])

  // Toggle card expansion
  const toggleCard = useCallback((id: string) => {
    setExpandedCardIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  // Search action
  const search = useCallback(async (data: SearchFormData): Promise<void> => {
    // Validation
    if (data.title.length < 5) {
      setError('Title must be at least 5 characters')
      return
    }

    if (data.abstract.length < 50) {
      setError('Abstract must be at least 50 characters')
      return
    }

    if (!sessionToken) {
      setError('Please log in to search')
      return
    }

    // Reset state
    setError(null)
    setResults(null)
    setExpandedCardIds(new Set())
    setActiveFilter('all')
    setLoading(true)
    setLastFormData(data)

    try {
      const response = await api.searchJournals(sessionToken, {
        title: data.title,
        abstract: data.abstract,
        keywords: data.keywords,
        prefer_open_access: data.preferOA,
      })

      setResults(response)
      onSearchComplete?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }, [sessionToken, onSearchComplete])

  // Reset all state
  const reset = useCallback(() => {
    setResults(null)
    setError(null)
    setExpandedCardIds(new Set())
    setActiveFilter('all')
    setLastFormData(null)
  }, [])

  // Export to CSV
  const exportCSV = useCallback(() => {
    if (!filteredJournals.length) return

    const headers = [
      'Name',
      'Publisher',
      'ISSN',
      'H-Index',
      'Category',
      'Open Access',
      'Match Score',
    ]

    const rows = filteredJournals.map((journal) => [
      `"${journal.name.replace(/"/g, '""')}"`,
      `"${(journal.publisher || '').replace(/"/g, '""')}"`,
      journal.issn || journal.issn_l || '',
      journal.metrics.h_index?.toString() || '',
      journal.category || '',
      journal.is_oa ? 'Yes' : 'No',
      `${Math.round(journal.relevance_score * 100)}%`,
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(',')),
    ].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'journal-results.csv'
    link.click()
    URL.revokeObjectURL(url)
  }, [filteredJournals])

  return {
    // State
    results,
    loading,
    error,

    // Derived
    aiAnalysis,
    filteredJournals,
    groupedJournals,

    // Filter
    activeFilter,
    setActiveFilter,

    // Expanded cards
    expandedCardIds,
    toggleCard,

    // Actions
    search,
    reset,
    exportCSV,
  }
}
