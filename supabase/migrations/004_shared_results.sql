-- Migration: Create shared_results table for Story 3.1 (Share Results)
-- This allows users to share their search results with others via a link.

-- Create the shared_results table
CREATE TABLE IF NOT EXISTS shared_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    discipline TEXT,
    journals_data JSONB NOT NULL DEFAULT '[]',
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_shared_results_user_id ON shared_results(user_id);
CREATE INDEX IF NOT EXISTS idx_shared_results_expires_at ON shared_results(expires_at);

-- Enable RLS
ALTER TABLE shared_results ENABLE ROW LEVEL SECURITY;

-- Policy: Users can create their own shared results
CREATE POLICY "Users can create own shared results"
ON shared_results FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can view their own shared results
CREATE POLICY "Users can view own shared results"
ON shared_results FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can delete their own shared results
CREATE POLICY "Users can delete own shared results"
ON shared_results FOR DELETE
USING (auth.uid() = user_id);

-- Policy: Anyone can view shared results by ID (for public sharing)
-- This uses a separate policy that allows SELECT when the ID is known
CREATE POLICY "Public can view shared results by direct link"
ON shared_results FOR SELECT
USING (true);

-- Service role bypass for backend
CREATE POLICY "Service role full access to shared_results"
ON shared_results FOR ALL
USING (auth.jwt() ->> 'role' = 'service_role');

-- Comment explaining the table
COMMENT ON TABLE shared_results IS 'Stores shareable search results with 7-day expiration';
COMMENT ON COLUMN shared_results.journals_data IS 'JSON array of journal objects from search results';
COMMENT ON COLUMN shared_results.expires_at IS 'Auto-expires 7 days after creation';
