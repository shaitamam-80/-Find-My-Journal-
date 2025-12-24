import type { SearchRequest, SearchResponse, ExplanationResponse, Journal } from '../types'

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`
  : '/api/v1'

class ApiService {
  private getAuthHeader(token: string): HeadersInit {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    }
  }

  async searchJournals(
    token: string,
    request: SearchRequest
  ): Promise<SearchResponse> {
    const response = await fetch(`${API_BASE}/search`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(request),
    })

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error('Daily search limit reached. Please upgrade or try again tomorrow.')
      }
      if (response.status === 401) {
        throw new Error('Please log in to search.')
      }
      const error = await response.json()
      throw new Error(error.detail || 'Search failed')
    }

    return response.json()
  }

  async getSearchHistory(token: string, limit: number = 10) {
    const response = await fetch(`${API_BASE}/search/history?limit=${limit}`, {
      headers: this.getAuthHeader(token),
    })

    if (!response.ok) {
      throw new Error('Failed to fetch search history')
    }

    return response.json()
  }

  // ==========================================================================
  // Share Results (Story 3.1)
  // ==========================================================================

  /**
   * Create a shareable link for search results.
   */
  async createShareLink(
    token: string,
    searchQuery: string,
    discipline: string | null,
    journals: Journal[]
  ): Promise<{ share_id: string; share_url: string; expires_in_days: number }> {
    const response = await fetch(`${API_BASE}/share`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({
        search_query: searchQuery,
        discipline,
        journals: journals.map((j) => ({
          id: j.id,
          name: j.name,
          publisher: j.publisher,
          homepage_url: j.homepage_url,
          is_oa: j.is_oa,
          metrics: j.metrics,
          topics: j.topics,
          relevance_score: j.relevance_score,
          category: j.category,
          match_reason: j.match_reason,
          match_details: j.match_details,
          matched_topics: j.matched_topics,
        })),
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to create share link')
    }

    return response.json()
  }

  /**
   * Get shared search results (public, no auth required).
   */
  async getSharedResults(shareId: string): Promise<{
    search_query: string
    discipline: string | null
    journals: Journal[]
    created_at: string
  }> {
    const response = await fetch(`${API_BASE}/share/${shareId}`)

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Shared results not found or expired')
      }
      throw new Error('Failed to load shared results')
    }

    return response.json()
  }

  /**
   * Get AI-generated explanation for why a journal matches the user's abstract.
   * Uses Google Gemini to generate personalized explanations.
   */
  async getJournalExplanation(
    token: string,
    abstract: string,
    journal: Journal
  ): Promise<ExplanationResponse> {
    const response = await fetch(`${API_BASE}/explain`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({
        abstract,
        journal_id: journal.id,
        journal_title: journal.name,
        journal_topics: journal.topics,
        journal_metrics: journal.metrics,
      }),
    })

    if (!response.ok) {
      if (response.status === 429) {
        throw new Error('Daily explanation limit reached. Upgrade for unlimited AI insights.')
      }
      if (response.status === 401) {
        throw new Error('Please log in to get AI explanations.')
      }
      const error = await response.json()
      throw new Error(error.detail?.message || error.detail || 'Failed to generate explanation')
    }

    return response.json()
  }

  // ==========================================================================
  // Saved Searches (Story 4.1)
  // ==========================================================================

  /**
   * Save a search to user's profile.
   */
  async saveSearch(
    token: string,
    data: {
      name: string
      title: string
      abstract: string
      keywords: string[]
      discipline: string | null
      results_count: number
    }
  ): Promise<{ id: string; name: string }> {
    const response = await fetch(`${API_BASE}/saved-searches`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(data),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to save search')
    }

    return response.json()
  }

  /**
   * Get user's saved searches.
   */
  async getSavedSearches(token: string): Promise<
    {
      id: string
      name: string
      title: string
      discipline: string | null
      results_count: number
      created_at: string
    }[]
  > {
    const response = await fetch(`${API_BASE}/saved-searches`, {
      headers: this.getAuthHeader(token),
    })

    if (!response.ok) {
      throw new Error('Failed to fetch saved searches')
    }

    return response.json()
  }

  /**
   * Get a specific saved search with full details.
   */
  async getSavedSearch(
    token: string,
    searchId: string
  ): Promise<{
    id: string
    name: string
    title: string
    abstract: string
    keywords: string[]
    discipline: string | null
    results_count: number
    created_at: string
  }> {
    const response = await fetch(`${API_BASE}/saved-searches/${searchId}`, {
      headers: this.getAuthHeader(token),
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Saved search not found')
      }
      throw new Error('Failed to load saved search')
    }

    return response.json()
  }

  /**
   * Delete a saved search.
   */
  async deleteSavedSearch(token: string, searchId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/saved-searches/${searchId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
    })

    if (!response.ok) {
      throw new Error('Failed to delete saved search')
    }
  }

  // ==========================================================================
  // Feedback Rating (Story 5.1)
  // ==========================================================================

  /**
   * Submit feedback (thumbs up/down) for a journal recommendation.
   */
  async submitFeedback(
    token: string,
    journalId: string,
    rating: 'up' | 'down',
    searchId?: string
  ): Promise<{ id: string; rating: string }> {
    const response = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({
        journal_id: journalId,
        rating,
        search_id: searchId,
      }),
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to submit feedback')
    }

    return response.json()
  }

  /**
   * Get user's feedback for multiple journals.
   */
  async getUserFeedback(
    token: string,
    journalIds: string[]
  ): Promise<Record<string, 'up' | 'down'>> {
    if (journalIds.length === 0) return {}

    const response = await fetch(
      `${API_BASE}/feedback?journal_ids=${journalIds.join(',')}`,
      {
        headers: this.getAuthHeader(token),
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch feedback')
    }

    const data = await response.json()
    return data.feedback
  }
}

export const api = new ApiService()
