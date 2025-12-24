-- Migration: Create journal_feedback table for Story 5.1 (Feedback Rating)
-- Allows users to rate journal recommendations with thumbs up/down.

-- Create the journal_feedback table
CREATE TABLE IF NOT EXISTS journal_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    journal_id TEXT NOT NULL,
    rating VARCHAR(10) NOT NULL CHECK (rating IN ('up', 'down')),
    search_id UUID,  -- Optional reference to the search that produced this recommendation
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, journal_id)  -- One rating per user per journal
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_journal_feedback_user_id ON journal_feedback(user_id);
CREATE INDEX IF NOT EXISTS idx_journal_feedback_journal_id ON journal_feedback(journal_id);

-- Enable RLS
ALTER TABLE journal_feedback ENABLE ROW LEVEL SECURITY;

-- Policy: Users can create their own feedback
CREATE POLICY "Users can create own feedback"
ON journal_feedback FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- Policy: Users can view their own feedback
CREATE POLICY "Users can view own feedback"
ON journal_feedback FOR SELECT
USING (auth.uid() = user_id);

-- Policy: Users can update their own feedback
CREATE POLICY "Users can update own feedback"
ON journal_feedback FOR UPDATE
USING (auth.uid() = user_id);

-- Policy: Users can delete their own feedback
CREATE POLICY "Users can delete own feedback"
ON journal_feedback FOR DELETE
USING (auth.uid() = user_id);

-- Service role bypass for backend
CREATE POLICY "Service role full access to journal_feedback"
ON journal_feedback FOR ALL
USING (auth.jwt() ->> 'role' = 'service_role');

-- Trigger to update updated_at on change
CREATE OR REPLACE FUNCTION update_journal_feedback_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER journal_feedback_updated_at
    BEFORE UPDATE ON journal_feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_journal_feedback_updated_at();

-- Comments
COMMENT ON TABLE journal_feedback IS 'Stores user feedback (thumbs up/down) on journal recommendations';
COMMENT ON COLUMN journal_feedback.journal_id IS 'OpenAlex journal ID';
COMMENT ON COLUMN journal_feedback.rating IS 'User rating: up (good recommendation) or down (poor recommendation)';
