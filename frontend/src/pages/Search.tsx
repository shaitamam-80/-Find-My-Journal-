import { useState, useMemo } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { api } from '../services/api'
import type { SearchResponse } from '../types'
import { JournalCard } from '../components/JournalCard'

export function Search() {
  const { user, session, limits, signOut, refreshLimits } = useAuth()
  const [title, setTitle] = useState('')
  const [abstract, setAbstract] = useState('')
  const [keywords, setKeywords] = useState('')
  const [preferOA, setPreferOA] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [results, setResults] = useState<SearchResponse | null>(null)

  // Filter state
  const [filterOAOnly, setFilterOAOnly] = useState(false)
  const [minCategory, setMinCategory] = useState<'all' | 'top_tier' | 'top_tier_broad'>('all')
  const [showFilters, setShowFilters] = useState(false)

  // Filtered results based on client-side filters
  const filteredJournals = useMemo(() => {
    if (!results?.journals) return []

    return results.journals.filter((journal) => {
      // Open Access filter
      if (filterOAOnly && !journal.is_oa) return false

      // Category filter (using category as proxy for quartile)
      if (minCategory === 'top_tier' && journal.category !== 'top_tier') return false
      if (minCategory === 'top_tier_broad' &&
          journal.category !== 'top_tier' &&
          journal.category !== 'broad_audience') return false

      return true
    })
  }, [results?.journals, filterOAOnly, minCategory])

  const handleClearForm = () => {
    setTitle('')
    setAbstract('')
    setKeywords('')
    setPreferOA(false)
    setError('')
  }

  const handleExportCSV = () => {
    if (!filteredJournals.length) return

    const headers = ['Name', 'Publisher', 'ISSN', 'H-Index', 'Category', 'Open Access']
    const rows = filteredJournals.map((journal) => [
      `"${journal.name.replace(/"/g, '""')}"`,
      `"${(journal.publisher || '').replace(/"/g, '""')}"`,
      journal.issn || journal.issn_l || '',
      journal.metrics.h_index?.toString() || '',
      journal.category || '',
      journal.is_oa ? 'Yes' : 'No',
    ])

    const csvContent = [headers.join(','), ...rows.map((row) => row.join(','))].join('\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'journal-results.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const handlePrint = () => {
    window.print()
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setResults(null)

    if (title.length < 5) {
      setError('Title must be at least 5 characters')
      return
    }

    if (abstract.length < 50) {
      setError('Abstract must be at least 50 characters')
      return
    }

    if (!session?.access_token) {
      setError('Please log in to search')
      return
    }

    setLoading(true)

    try {
      const keywordList = keywords
        .split(',')
        .map((k) => k.trim())
        .filter((k) => k.length > 0)

      const response = await api.searchJournals(session.access_token, {
        title,
        abstract,
        keywords: keywordList,
        prefer_open_access: preferOA,
      })

      setResults(response)
      await refreshLimits()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-lg border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: '#0ea5e9' }}>
                <span className="material-symbols-outlined text-white" style={{ fontSize: '20px' }}>menu_book</span>
              </div>
              <span className="text-lg font-bold text-neutral-800 tracking-tight">
                Find My Journal
              </span>
            </div>

            {/* Right side */}
            <div className="flex items-center gap-6">
              {/* Search limits */}
              {limits && (
                <div className="hidden sm:flex items-center gap-2 px-4 py-2 rounded-full" style={{ background: limits.daily_limit !== null ? '#fef3c7' : '#e0f2fe' }}>
                  {limits.daily_limit !== null ? (
                    <>
                      <span className="material-symbols-outlined" style={{ color: '#b45309', fontSize: '18px' }}>bolt</span>
                      <span className="text-sm font-medium" style={{ color: '#92400e' }}>
                        Searches today: {limits.used_today}/{limits.daily_limit}
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined" style={{ color: '#0284c7', fontSize: '18px' }}>all_inclusive</span>
                      <span className="text-sm font-medium" style={{ color: '#0369a1' }}>
                        Unlimited
                      </span>
                    </>
                  )}
                </div>
              )}

              {/* User menu */}
              <div className="flex items-center gap-3">
                <span className="hidden md:block text-sm text-neutral-500">
                  {user?.email}
                </span>
                <button
                  onClick={signOut}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg transition-all text-neutral-600 hover:bg-neutral-100 hover:text-neutral-800"
                  title="Sign out"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>logout</span>
                  <span className="hidden sm:inline text-sm font-medium">Sign out</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-10">
          <h1 className="text-4xl md:text-5xl font-bold text-neutral-800 mb-4">
            Find the Right Journal
          </h1>
          <p className="text-lg text-neutral-600 max-w-2xl mx-auto">
            Paste your abstract below and we'll analyze it to find the most relevant academic journals for your research.
          </p>
        </div>

        {/* Search Form */}
        <div className="bg-white rounded-2xl shadow-xl border border-neutral-100 p-8 mb-10">
          <form onSubmit={handleSearch} className="space-y-6">
            {error && (
              <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
                <span className="material-symbols-outlined text-red-500 shrink-0" style={{ fontSize: '20px' }}>error</span>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            )}

            {/* Title Field */}
            <div className="space-y-2">
              <label htmlFor="title" className="flex items-center gap-2 text-sm font-medium text-neutral-700">
                <span className="material-symbols-outlined text-neutral-400" style={{ fontSize: '18px' }}>description</span>
                Article Title
                <span className="text-red-500">*</span>
              </label>
              <input
                id="title"
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Enter your article title"
                className="w-full px-4 py-3.5 text-neutral-800 bg-white border-2 border-neutral-200 rounded-xl transition-all duration-200 placeholder:text-neutral-400 hover:border-neutral-300 focus:outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10"
                required
              />
            </div>

            {/* Abstract Field */}
            <div className="space-y-2">
              <label htmlFor="abstract" className="flex items-center gap-2 text-sm font-medium text-neutral-700">
                <span className="material-symbols-outlined text-neutral-400" style={{ fontSize: '18px' }}>auto_awesome</span>
                Abstract
                <span className="text-red-500">*</span>
              </label>
              <textarea
                id="abstract"
                value={abstract}
                onChange={(e) => setAbstract(e.target.value)}
                placeholder="Paste your article abstract here... We'll analyze it to find matching journals."
                rows={8}
                className="w-full px-4 py-3.5 text-neutral-800 bg-white border-2 border-neutral-200 rounded-xl transition-all duration-200 placeholder:text-neutral-400 hover:border-neutral-300 focus:outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10 resize-y"
                required
              />
              <div className="flex items-center justify-between">
                <p className="text-xs text-neutral-400">
                  Minimum 50 characters required
                </p>
                <p className="text-xs font-medium" style={{ color: abstract.length >= 50 ? '#22c55e' : '#a3a3a3' }}>
                  {abstract.length} characters
                </p>
              </div>
            </div>

            {/* Keywords Field */}
            <div className="space-y-2">
              <label htmlFor="keywords" className="flex items-center gap-2 text-sm font-medium text-neutral-700">
                <span className="material-symbols-outlined text-neutral-400" style={{ fontSize: '18px' }}>sell</span>
                Keywords
                <span className="text-xs font-normal text-neutral-400">(optional, comma-separated)</span>
              </label>
              <input
                id="keywords"
                type="text"
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="machine learning, neural networks, deep learning"
                className="w-full px-4 py-3.5 text-neutral-800 bg-white border-2 border-neutral-200 rounded-xl transition-all duration-200 placeholder:text-neutral-400 hover:border-neutral-300 focus:outline-none focus:border-sky-500 focus:ring-4 focus:ring-sky-500/10"
              />
            </div>

            {/* Options Row */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pt-2">
              <label className="flex items-center gap-3 cursor-pointer group">
                <div className="relative">
                  <input
                    type="checkbox"
                    checked={preferOA}
                    onChange={(e) => setPreferOA(e.target.checked)}
                    className="peer sr-only"
                  />
                  <div className="w-5 h-5 rounded-md border-2 border-neutral-300 transition-all peer-checked:border-sky-500 peer-checked:bg-sky-500">
                    {preferOA && (
                      <svg className="w-full h-full text-white p-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                        <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                    )}
                  </div>
                </div>
                <span className="text-sm text-neutral-600">
                  Prefer Open Access journals
                </span>
              </label>

              {/* Buttons */}
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={handleClearForm}
                  className="flex items-center gap-2 px-4 py-3 text-neutral-600 bg-white border-2 border-neutral-200 rounded-xl font-medium transition-all hover:border-neutral-300 hover:bg-neutral-50"
                >
                  <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>delete</span>
                  Clear
                </button>
                <button
                  type="submit"
                  disabled={loading || (limits?.can_search === false)}
                  className="flex items-center gap-2 px-6 py-3 text-white font-semibold rounded-xl transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed"
                  style={{
                    background: loading ? '#94a3b8' : '#0ea5e9',
                    boxShadow: loading ? 'none' : '0 4px 14px -3px rgba(14, 165, 233, 0.4)'
                  }}
                  onMouseEnter={(e) => !loading && (e.currentTarget.style.background = '#0284c7')}
                  onMouseLeave={(e) => !loading && (e.currentTarget.style.background = '#0ea5e9')}
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Searching...
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>search</span>
                      Find Journals
                    </>
                  )}
                </button>
              </div>
            </div>

            {limits?.can_search === false && (
              <div className="p-4 rounded-xl bg-amber-50 border border-amber-200">
                <p className="text-sm text-amber-700">
                  You've reached your daily search limit. Upgrade for unlimited searches!
                </p>
              </div>
            )}
          </form>
        </div>

        {/* Results */}
        {results && (
          <div>
            {/* Results Header */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
              <div>
                <h2 className="text-2xl font-bold text-neutral-800">
                  {results.total_found} Journals Found
                  {filteredJournals.length !== results.journals.length && (
                    <span className="text-base font-normal ml-2 text-neutral-500">
                      ({filteredJournals.length} shown)
                    </span>
                  )}
                </h2>
                {results.discipline && (
                  <p className="text-sm mt-1 text-neutral-500">
                    Detected field:{' '}
                    <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold capitalize" style={{ background: '#e0f2fe', color: '#0369a1' }}>
                      {results.discipline.replace('_', ' ')}
                    </span>
                  </p>
                )}
              </div>
            </div>

            {/* Actions Bar */}
            {results.journals.length > 0 && (
              <div className="bg-white rounded-xl border border-neutral-200 p-4 mb-6 no-print">
                <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                  {/* Filters Toggle */}
                  <button
                    type="button"
                    onClick={() => setShowFilters(!showFilters)}
                    className="flex items-center gap-2 text-sm font-medium text-neutral-600 hover:text-neutral-800 transition-colors"
                  >
                    <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>filter_list</span>
                    Filters
                    <span className={`material-symbols-outlined transition-transform ${showFilters ? 'rotate-180' : ''}`} style={{ fontSize: '18px' }}>expand_more</span>
                  </button>

                  {/* Export Actions */}
                  <div className="flex items-center gap-2">
                    <button
                      onClick={handleExportCSV}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-neutral-600 bg-white border border-neutral-200 rounded-lg font-medium transition-all hover:border-neutral-300 hover:bg-neutral-50"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>download</span>
                      Export CSV
                    </button>
                    <button
                      onClick={handlePrint}
                      className="flex items-center gap-2 px-3 py-2 text-sm text-neutral-600 bg-white border border-neutral-200 rounded-lg font-medium transition-all hover:border-neutral-300 hover:bg-neutral-50"
                    >
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>print</span>
                      Print
                    </button>
                  </div>
                </div>

                {/* Expanded Filters */}
                {showFilters && (
                  <div className="mt-4 pt-4 border-t border-neutral-200 flex flex-wrap items-center gap-6">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={filterOAOnly}
                        onChange={(e) => setFilterOAOnly(e.target.checked)}
                        className="w-4 h-4 rounded border-2 border-neutral-300 text-sky-500 focus:ring-sky-500"
                      />
                      <span className="text-sm text-neutral-600">Open Access Only</span>
                    </label>

                    <div className="flex items-center gap-2">
                      <label htmlFor="minCategory" className="text-sm text-neutral-600">
                        Category:
                      </label>
                      <select
                        id="minCategory"
                        value={minCategory}
                        onChange={(e) => setMinCategory(e.target.value as 'all' | 'top_tier' | 'top_tier_broad')}
                        className="text-sm rounded-lg px-3 py-2 border-2 border-neutral-200 text-neutral-700 focus:ring-2 focus:ring-sky-500 focus:border-sky-500"
                      >
                        <option value="all">All Categories</option>
                        <option value="top_tier">Top Tier Only</option>
                        <option value="top_tier_broad">Top Tier + Broad Audience</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Journal Cards */}
            {filteredJournals.length > 0 ? (
              <div className="grid gap-6 md:grid-cols-2 print:grid-cols-1">
                {filteredJournals.map((journal, index) => (
                  <div
                    key={journal.id}
                    className="animate-fade-in-up"
                    style={{ animationDelay: `${0.05 * Math.min(index, 10)}s` }}
                  >
                    <JournalCard journal={journal} />
                  </div>
                ))}
              </div>
            ) : results.journals.length > 0 ? (
              <div className="bg-white rounded-xl border border-neutral-200 p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-amber-100">
                  <span className="material-symbols-outlined" style={{ color: '#b45309', fontSize: '32px' }}>filter_list</span>
                </div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-2">
                  No journals match filters
                </h3>
                <p className="text-neutral-500">
                  Try adjusting your filter settings to see more results.
                </p>
              </div>
            ) : (
              <div className="bg-white rounded-xl border border-neutral-200 p-8 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-amber-100">
                  <span className="material-symbols-outlined" style={{ color: '#b45309', fontSize: '32px' }}>search</span>
                </div>
                <h3 className="text-lg font-semibold text-neutral-800 mb-2">
                  No journals found
                </h3>
                <p className="text-neutral-500">
                  Try adjusting your keywords or abstract for better matches.
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  )
}
