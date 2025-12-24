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
  two_yr_mean_citedness: number | null
}

// =============================================================================
// Trust & Safety Verification Types
// =============================================================================

/** Visual badge color for verification status */
export type BadgeColor = 'verified' | 'caution' | 'high_risk' | 'unverified'

/** Source of verification data */
export type VerificationSource =
  | 'medline'
  | 'doaj'
  | 'cope'
  | 'oaspa'
  | 'pmc'
  | 'blacklist'
  | 'heuristic'

/** A specific warning or verification flag */
export interface VerificationFlag {
  source: VerificationSource
  reason: string
  severity: 'low' | 'medium' | 'high' | 'critical'
}

/**
 * Journal verification status from Trust & Safety Engine.
 *
 * Uses factual, non-defamatory language:
 * - verified: "Verified Source" (not "Safe")
 * - caution: "Exercise Caution" or "Limited Indexing"
 * - high_risk: "Publication Risk Detected" (not "Predatory")
 * - unverified: "Unverified Source"
 */
export interface VerificationStatus {
  badge_color: BadgeColor
  status_text: string
  subtitle?: string
  reasons: string[]
  flags?: VerificationFlag[]
  sources_checked?: VerificationSource[]
  verified_by?: VerificationSource
  checked_at?: string
  cache_valid_until?: string
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
  is_in_doaj?: boolean
  apc_usd: number | null
  metrics: JournalMetrics
  topics: string[]
  relevance_score: number
  category: 'top_tier' | 'broad_audience' | 'niche' | 'emerging' | null
  match_reason: string | null
  /** Trust & Safety verification status */
  verification?: VerificationStatus
  /** Detailed reasons why this journal matches (Story 1.1) */
  match_details?: string[]
  /** Topics that matched between paper and journal (Story 1.2) */
  matched_topics?: string[]
}

export interface SearchRequest {
  title: string
  abstract: string
  keywords?: string[]
  prefer_open_access?: boolean
  min_works_count?: number
}

/** Auto-detected discipline with confidence (Story 2.1) */
export interface DisciplineDetection {
  name: string
  field: string | null
  confidence: number  // 0-1
  source: string
}

export interface SearchResponse {
  query: string
  discipline: string | null
  discipline_detection: DisciplineDetection | null  // Story 2.1
  total_found: number
  journals: Journal[]
  search_id: string | null
}

// =============================================================================
// AI Explanation Types
// =============================================================================

/** Request for AI-generated journal explanation */
export interface ExplanationRequest {
  abstract: string
  journal_id: string
  journal_title: string
  journal_topics: string[]
  journal_metrics: Record<string, number | null>
}

/** Response from AI explanation endpoint */
export interface ExplanationResponse {
  explanation: string
  is_ai_generated: boolean
  remaining_today: number | null
}
