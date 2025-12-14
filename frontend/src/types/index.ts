export interface User {
  id: string
  email: string
  tier: 'free' | 'paid' | 'super_admin'
  credits_used_today: number
  has_unlimited_searches: boolean
  is_admin: boolean
}

export interface UserLimits {
  tier: string
  daily_limit: number | null
  used_today: number
  remaining: number | null
  can_search: boolean
}

export interface JournalMetrics {
  cited_by_count: number | null
  works_count: number | null
  h_index: number | null
  i10_index: number | null
}

export interface Journal {
  id: string
  name: string
  issn: string | null
  issn_l: string | null
  publisher: string | null
  homepage_url: string | null
  type: string | null
  is_oa: boolean
  apc_usd: number | null
  metrics: JournalMetrics
  topics: string[]
  relevance_score: number
  category: 'top_tier' | 'broad_audience' | 'niche' | 'emerging' | null
  match_reason: string | null
}

export interface SearchRequest {
  title: string
  abstract: string
  keywords?: string[]
  prefer_open_access?: boolean
  min_works_count?: number
}

export interface SearchResponse {
  query: string
  discipline: string | null
  total_found: number
  journals: Journal[]
  search_id: string | null
}
