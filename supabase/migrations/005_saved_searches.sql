-- Migration: Create saved_searches table for Story 4.1 (Saved Searches)
-- Allows users to save searches to their profile for quick access.

-- Create the saved_searches table
CREATE TABLE IF NOT EXISTS saved_searches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    keywords TEXT[] DEFAULT ARRAY[]::TEXT[],
    discipline TEXT,
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster lookups by user
CREATE INDEX IF NOT EXISTS idx_saved_searches_user_id ON saved_searches(user_id);

-- Enable RLS
ALTER TABLE saved_searches ENABLE ROW LEVEL SECURITY;

-- Policy: Users can create their own saved searches
CREATE POLICY "Users can create own saved searches"
ON saved_searches FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can view their own saved searches
CREATE POLICY "Users can view own saved searches"
ON saved_searches FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can delete their own saved searches
CREATE POLICY "Users can delete own saved searches"
ON saved_searches FOR DELETE
USING (auth.uid() = user_id);

-- Service role bypass for backend
CREATE POLICY "Service role full access to saved_searches"
ON saved_searches FOR ALL
USING (auth.jwt() ->> 'role' = 'service_role');

-- Comment explaining the table
COMMENT ON TABLE saved_searches IS 'Stores saved searches for quick re-run access (max 20 per user)';
COMMENT ON COLUMN saved_searches.name IS 'User-given name for this saved search';
COMMENT ON COLUMN saved_searches.abstract IS 'Original abstract used in the search';
COMMENT ON COLUMN saved_searches.keywords IS 'Keywords array used in the search';
