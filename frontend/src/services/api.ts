import type { SearchRequest, SearchResponse } from '../types'

const API_BASE = '/api/v1'

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
}

export const api = new ApiService()
