import { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import type { SearchResponse } from '../types'
import { SearchHeader } from '../components/search/SearchHeader'
import { SearchForm, type SearchFormData } from '../components/search/SearchForm'
import { SearchResults } from '../components/search/SearchResults'

export function Search() {
  const { user, session, limits, signOut, refreshLimits } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)

  // Store form data for results component
  const [lastSearch, setLastSearch] = useState<{
    title: string
    abstract: string
    keywords: string[]
  } | null>(null)

  const handleSearch = async (formData: SearchFormData) => {
    setError('')
    setResults(null)

    if (!session?.access_token) {
      setError('Please log in to search')
      return
    }

    setLoading(true)

    try {
      const response = await api.searchJournals(session.access_token, {
        title: formData.title,
        abstract: formData.abstract,
        keywords: formData.keywords,
        prefer_open_access: formData.preferOpenAccess,
      })

      setResults(response)
      setLastSearch({
        title: formData.title,
        abstract: formData.abstract,
        keywords: formData.keywords,
      })
      await refreshLimits()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveSearch = async (name: string) => {
    if (!session?.access_token || !results || !lastSearch) return

    await api.saveSearch(session.access_token, {
      name,
      title: lastSearch.title,
      abstract: lastSearch.abstract,
      keywords: lastSearch.keywords,
      discipline: results.discipline,
      results_count: results.total_found,
    })
  }

  const canSearch = limits?.can_search !== false

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <SearchHeader
        userEmail={user?.email}
        limits={limits}
        onSignOut={signOut}
      />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 dark:text-white mb-4">
            Find the Right Journal
          </h1>
          <p className="text-lg text-gray-600 dark:text-slate-400 max-w-2xl mx-auto">
            Paste your abstract below and we'll analyze it to find the most relevant
            academic journals for your research.
          </p>
        </div>

        {/* Search Form */}
        <SearchForm
          onSearch={handleSearch}
          loading={loading}
          error={error}
          canSearch={canSearch}
          onClearError={() => setError('')}
        />

        {/* Results */}
        {results && lastSearch && (
          <SearchResults
            results={results}
            title={lastSearch.title}
            abstract={lastSearch.abstract}
            keywords={lastSearch.keywords}
            sessionToken={session?.access_token || null}
            onSaveSearch={handleSaveSearch}
          />
        )}
      </main>
    </div>
  )
}
