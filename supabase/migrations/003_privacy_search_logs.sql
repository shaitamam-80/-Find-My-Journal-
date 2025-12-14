-- Migration: Privacy-enhanced search_logs table
-- This migration modifies the search_logs table for better privacy/data minimization
-- Instead of storing full query text, we store only:
--   - discipline (for analytics)
--   - query_hash (SHA-256 of the abstract, for duplicate detection)
--   - is_incognito (flag indicating if user opted out of logging)

-- Step 1: Add new columns to search_logs
ALTER TABLE public.search_logs
  ADD COLUMN IF NOT EXISTS discipline TEXT,
  ADD COLUMN IF NOT EXISTS query_hash TEXT,
  ADD COLUMN IF NOT EXISTS is_incognito BOOLEAN DEFAULT FALSE;

-- Step 2: Create index on query_hash for efficient duplicate detection
CREATE INDEX IF NOT EXISTS idx_search_logs_query_hash ON public.search_logs(query_hash);

-- Step 3: Create index on discipline for analytics queries
CREATE INDEX IF NOT EXISTS idx_search_logs_discipline ON public.search_logs(discipline);

-- Step 4: Remove the old query column that stored raw text
-- Note: This is a destructive operation - uncomment only after verifying data migration
-- For safety, we'll first make query nullable, then drop in a future migration
ALTER TABLE public.search_logs
  ALTER COLUMN query DROP NOT NULL;

-- Step 5: Add comment explaining the privacy-focused schema
COMMENT ON COLUMN public.search_logs.discipline IS 'Academic discipline detected from search (e.g., Medicine, Computer Science)';
COMMENT ON COLUMN public.search_logs.query_hash IS 'SHA-256 hash of the abstract for duplicate detection without storing content';
COMMENT ON COLUMN public.search_logs.is_incognito IS 'When true, indicates user opted for incognito mode (no logging of personal search content)';
