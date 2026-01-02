import type {
  SearchRequest,
  SearchResponse,
  ExplanationResponse,
  Journal,
  ProfileResponse,
  ProfileUpdateRequest,
  UsageStats,
  UserListResponse,
  AdminUserUpdate,
  PlatformStats,
} from '../types'

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL.replace(/\/$/, '')}/api/v1`
  : '/api/v1'

class ApiService {
  private readonly DEFAULT_TIMEOUT = 30000 // 30 seconds

  private getAuthHeader(token: string): HeadersInit {
    return {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    }
  }

  /**
   * Fetch with timeout and abort support.
   * Prevents requests from hanging indefinitely and allows cancellation.
   */
  private async fetchWithTimeout(
    url: string,
    options: RequestInit & { timeout?: number } = {}
  ): Promise<Response> {
    const { timeout = this.DEFAULT_TIMEOUT, signal, ...fetchOptions } = options

    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), timeout)

    // Link external signal if provided
    const handleAbort = () => controller.abort()
    if (signal) {
      signal.addEventListener('abort', handleAbort, { once: true })
    }

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        signal: controller.signal,
      })
      return response
    } catch (error) {
      if (error instanceof Error && error.name === 'AbortError') {
        // Check if it was external abort or timeout
        if (signal?.aborted) {
          throw error // Re-throw for external abort
        }
        throw new Error('Request timed out. Please check your connection and try again.')
      }
      throw error
    } finally {
      clearTimeout(timeoutId)
      if (signal) {
        signal.removeEventListener('abort', handleAbort)
      }
    }
  }

  async searchJournals(
    token: string,
    request: SearchRequest,
    signal?: AbortSignal
  ): Promise<SearchResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE}/search`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(request),
      timeout: 60000, // 60s for search (can be slow)
      signal,
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

  async getSearchHistory(token: string, limit: number = 10, signal?: AbortSignal) {
    const response = await this.fetchWithTimeout(`${API_BASE}/search/history?limit=${limit}`, {
      headers: this.getAuthHeader(token),
      signal,
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
    journals: Journal[],
    signal?: AbortSignal
  ): Promise<{ share_id: string; share_url: string; expires_in_days: number }> {
    const response = await this.fetchWithTimeout(`${API_BASE}/share`, {
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
      signal,
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
  async getSharedResults(shareId: string, signal?: AbortSignal): Promise<{
    search_query: string
    discipline: string | null
    journals: Journal[]
    created_at: string
  }> {
    const response = await this.fetchWithTimeout(`${API_BASE}/share/${shareId}`, { signal })

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
    journal: Journal,
    signal?: AbortSignal
  ): Promise<ExplanationResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE}/explain`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({
        abstract,
        journal_id: journal.id,
        journal_title: journal.name,
        journal_topics: journal.topics,
        journal_metrics: journal.metrics,
      }),
      timeout: 45000, // 45s for AI explanation
      signal,
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
    },
    signal?: AbortSignal
  ): Promise<{ id: string; name: string }> {
    const response = await this.fetchWithTimeout(`${API_BASE}/saved-searches`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(data),
      signal,
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
  async getSavedSearches(token: string, signal?: AbortSignal): Promise<
    {
      id: string
      name: string
      title: string
      discipline: string | null
      results_count: number
      created_at: string
    }[]
  > {
    const response = await this.fetchWithTimeout(`${API_BASE}/saved-searches`, {
      headers: this.getAuthHeader(token),
      signal,
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
    searchId: string,
    signal?: AbortSignal
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
    const response = await this.fetchWithTimeout(`${API_BASE}/saved-searches/${searchId}`, {
      headers: this.getAuthHeader(token),
      signal,
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
  async deleteSavedSearch(token: string, searchId: string, signal?: AbortSignal): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE}/saved-searches/${searchId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
      signal,
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
    searchId?: string,
    signal?: AbortSignal
  ): Promise<{ id: string; rating: string }> {
    const response = await this.fetchWithTimeout(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      body: JSON.stringify({
        journal_id: journalId,
        rating,
        search_id: searchId,
      }),
      signal,
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
    journalIds: string[],
    signal?: AbortSignal
  ): Promise<Record<string, 'up' | 'down'>> {
    if (journalIds.length === 0) return {}

    const response = await this.fetchWithTimeout(
      `${API_BASE}/feedback?journal_ids=${journalIds.join(',')}`,
      {
        headers: this.getAuthHeader(token),
        signal,
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch feedback')
    }

    const data = await response.json()
    return data.feedback
  }

  // ==========================================================================
  // Dashboard (User Stats & Activity)
  // ==========================================================================

  /**
   * Get user dashboard statistics.
   */
  async getDashboardStats(token: string, signal?: AbortSignal): Promise<{
    searches_today: number
    searches_total: number
    saved_searches_count: number
    daily_limit: number | null
    tier: string
  }> {
    const response = await this.fetchWithTimeout(`${API_BASE}/dashboard/stats`, {
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      throw new Error('Failed to fetch dashboard stats')
    }

    return response.json()
  }

  /**
   * Get user's recent activity.
   */
  async getRecentActivity(
    token: string,
    limit: number = 10,
    signal?: AbortSignal
  ): Promise<{
    activities: {
      id: string
      type: 'search' | 'save' | 'feedback'
      description: string
      created_at: string
      metadata?: Record<string, unknown>
    }[]
    total: number
  }> {
    const response = await this.fetchWithTimeout(`${API_BASE}/dashboard/recent-activity?limit=${limit}`, {
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      throw new Error('Failed to fetch recent activity')
    }

    return response.json()
  }

  // ==========================================================================
  // User Profile Management
  // ==========================================================================

  /**
   * Get current user's full profile.
   */
  async getMyProfile(token: string, signal?: AbortSignal): Promise<ProfileResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE}/users/me/profile`, {
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      throw new Error('Failed to fetch profile')
    }

    return response.json()
  }

  /**
   * Update current user's profile.
   */
  async updateMyProfile(
    token: string,
    updates: ProfileUpdateRequest,
    signal?: AbortSignal
  ): Promise<ProfileResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE}/users/me/profile`, {
      method: 'PATCH',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(updates),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update profile')
    }

    return response.json()
  }

  /**
   * Get current user's usage statistics.
   */
  async getMyUsage(token: string, signal?: AbortSignal): Promise<UsageStats> {
    const response = await this.fetchWithTimeout(`${API_BASE}/users/me/usage`, {
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      throw new Error('Failed to fetch usage stats')
    }

    return response.json()
  }

  /**
   * Deactivate current user's account.
   */
  async deactivateMyAccount(token: string, signal?: AbortSignal): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE}/users/me/deactivate`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to deactivate account')
    }
  }

  /**
   * Delete current user's account permanently.
   */
  async deleteMyAccount(token: string, signal?: AbortSignal): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE}/users/me`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete account')
    }
  }

  /**
   * Update notification preferences.
   */
  async updateNotificationPreferences(
    token: string,
    emailNotifications: boolean,
    signal?: AbortSignal
  ): Promise<void> {
    const response = await this.fetchWithTimeout(
      `${API_BASE}/users/me/notifications?email_notifications=${emailNotifications}`,
      {
        method: 'PATCH',
        headers: this.getAuthHeader(token),
        signal,
      }
    )

    if (!response.ok) {
      throw new Error('Failed to update notification preferences')
    }
  }

  // ==========================================================================
  // Admin API
  // ==========================================================================

  /**
   * List all users (admin only).
   */
  async listUsers(
    token: string,
    params: {
      page?: number
      limit?: number
      tier?: string
      search?: string
      isActive?: boolean
    } = {},
    signal?: AbortSignal
  ): Promise<UserListResponse> {
    const searchParams = new URLSearchParams()
    if (params.page) searchParams.set('page', params.page.toString())
    if (params.limit) searchParams.set('limit', params.limit.toString())
    if (params.tier) searchParams.set('tier', params.tier)
    if (params.search) searchParams.set('search', params.search)
    if (params.isActive !== undefined) searchParams.set('is_active', params.isActive.toString())

    const response = await this.fetchWithTimeout(
      `${API_BASE}/admin/users?${searchParams.toString()}`,
      { headers: this.getAuthHeader(token), signal }
    )

    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('Admin access required')
      }
      throw new Error('Failed to fetch users')
    }

    return response.json()
  }

  /**
   * Get a specific user's profile (admin only).
   */
  async getUser(token: string, userId: string, signal?: AbortSignal): Promise<ProfileResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE}/admin/users/${userId}`, {
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('User not found')
      }
      throw new Error('Failed to fetch user')
    }

    return response.json()
  }

  /**
   * Update a user's settings (admin only).
   */
  async updateUser(
    token: string,
    userId: string,
    updates: AdminUserUpdate,
    signal?: AbortSignal
  ): Promise<ProfileResponse> {
    const response = await this.fetchWithTimeout(`${API_BASE}/admin/users/${userId}`, {
      method: 'PATCH',
      headers: this.getAuthHeader(token),
      body: JSON.stringify(updates),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to update user')
    }

    return response.json()
  }

  /**
   * Activate a user (admin only).
   */
  async activateUser(token: string, userId: string, signal?: AbortSignal): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE}/admin/users/${userId}/activate`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      throw new Error('Failed to activate user')
    }
  }

  /**
   * Deactivate a user (admin only).
   */
  async adminDeactivateUser(token: string, userId: string, signal?: AbortSignal): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE}/admin/users/${userId}/deactivate`, {
      method: 'POST',
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to deactivate user')
    }
  }

  /**
   * Delete a user permanently (admin only).
   */
  async adminDeleteUser(token: string, userId: string, signal?: AbortSignal): Promise<void> {
    const response = await this.fetchWithTimeout(`${API_BASE}/admin/users/${userId}`, {
      method: 'DELETE',
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Failed to delete user')
    }
  }

  /**
   * Get platform statistics (admin only).
   */
  async getPlatformStats(token: string, signal?: AbortSignal): Promise<PlatformStats> {
    const response = await this.fetchWithTimeout(`${API_BASE}/admin/stats`, {
      headers: this.getAuthHeader(token),
      signal,
    })

    if (!response.ok) {
      throw new Error('Failed to fetch platform stats')
    }

    return response.json()
  }
}

export const api = new ApiService()
