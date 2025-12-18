-- Migration: Add AI Explanation Cache and User Tracking
-- Run this in Supabase SQL Editor
-- =============================================================================

-- 1. Create explanation_cache table for caching Gemini responses
-- =============================================================================
CREATE TABLE IF NOT EXISTS explanation_cache (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    cache_key VARCHAR(32) UNIQUE NOT NULL,  -- MD5 hash of abstract + journal_id
    explanation TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Create indexes for efficient lookups
CREATE INDEX IF NOT EXISTS idx_explanation_cache_key ON explanation_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_explanation_cache_expires ON explanation_cache(expires_at);

-- Add comment for documentation
COMMENT ON TABLE explanation_cache IS 'Cache for AI-generated journal explanations (TTL: 7 days)';
COMMENT ON COLUMN explanation_cache.cache_key IS 'MD5 hash of abstract[:2000] + journal_id';

-- 2. Add explanation tracking columns to profiles table
-- =============================================================================
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS explanations_used_today INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS last_explanation_date DATE;

-- Add comments for documentation
COMMENT ON COLUMN profiles.explanations_used_today IS 'Daily AI explanation usage counter (resets daily)';
COMMENT ON COLUMN profiles.last_explanation_date IS 'Last date explanations were used (for counter reset)';

-- 3. Enable Row Level Security (RLS)
-- =============================================================================
ALTER TABLE explanation_cache ENABLE ROW LEVEL SECURITY;

-- Policy: Only service role can read/write (backend only)
DROP POLICY IF EXISTS "Service role full access" ON explanation_cache;
CREATE POLICY "Service role full access" ON explanation_cache
    FOR ALL
    USING (auth.role() = 'service_role');

-- 4. Create cleanup function for expired cache entries (optional)
-- =============================================================================
CREATE OR REPLACE FUNCTION cleanup_expired_explanations()
RETURNS void AS $$
BEGIN
    DELETE FROM explanation_cache
    WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- You can schedule this to run daily via pg_cron if available:
-- SELECT cron.schedule('cleanup-explanations', '0 3 * * *', 'SELECT cleanup_expired_explanations()');

-- =============================================================================
-- Verification queries (run after migration)
-- =============================================================================
-- Check explanation_cache table exists:
-- SELECT * FROM explanation_cache LIMIT 1;

-- Check profiles has new columns:
-- SELECT explanations_used_today, last_explanation_date FROM profiles LIMIT 1;

-- Check RLS is enabled:
-- SELECT tablename, rowsecurity FROM pg_tables WHERE tablename = 'explanation_cache';
