---
name: database
description: Supabase + PostgreSQL database specialist. Use when designing schemas, writing migrations, implementing RLS policies, optimizing queries, or debugging database issues. Includes Row Level Security patterns, indexing strategies, and Supabase-specific features like Auth integration, Storage, and Edge Functions.
---

# Database Skill

Supabase + PostgreSQL specialist for secure, scalable databases.

## Stack

| Layer | Technology |
|-------|------------|
| Database | PostgreSQL 15 |
| Platform | Supabase |
| Auth | Supabase Auth |
| Storage | Supabase Storage |
| Realtime | Supabase Realtime |

## Project Structure

```
supabase/
├── migrations/
│   ├── 20240101000000_create_users.sql
│   ├── 20240102000000_create_searches.sql
│   └── 20240103000000_add_rls_policies.sql
├── seed.sql
└── config.toml
```

## Schema Design

### Basic Table

```sql
-- migrations/20240101000000_create_profiles.sql
CREATE TABLE profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    name TEXT,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'premium', 'admin')),
    daily_searches INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

### Relations

```sql
-- migrations/20240102000000_create_searches.sql
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    query_title TEXT NOT NULL,
    query_abstract TEXT NOT NULL,
    query_hash TEXT,  -- For privacy
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for faster lookups
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_created_at ON search_history(created_at DESC);
```

### Many-to-Many

```sql
-- User saved journals
CREATE TABLE saved_journals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
    journal_id TEXT NOT NULL,  -- External ID from OpenAlex
    journal_title TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, journal_id)  -- Prevent duplicates
);

CREATE INDEX idx_saved_journals_user ON saved_journals(user_id);
```

## Row Level Security (RLS)

### Enable RLS

```sql
-- CRITICAL: Always enable RLS on user data tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE saved_journals ENABLE ROW LEVEL SECURITY;
```

### Basic Policies

```sql
-- Profiles: users can only see/edit their own
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
ON profiles FOR UPDATE
USING (auth.uid() = id);

-- No INSERT policy needed - handled by trigger
-- No DELETE policy - users shouldn't delete profiles
```

### CRUD Policies

```sql
-- Search History: full CRUD for own data
CREATE POLICY "Users can view own searches"
ON search_history FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Users can create own searches"
ON search_history FOR INSERT
WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own searches"
ON search_history FOR DELETE
USING (auth.uid() = user_id);
```

### Service Role Bypass

```sql
-- Allow service role (backend) to do anything
CREATE POLICY "Service role has full access"
ON profiles FOR ALL
USING (auth.jwt() ->> 'role' = 'service_role');
```

### Public Read Policies

```sql
-- Public data (e.g., journal metadata)
CREATE TABLE journals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    publisher TEXT,
    is_public BOOLEAN DEFAULT true
);

ALTER TABLE journals ENABLE ROW LEVEL SECURITY;

-- Anyone can read public journals
CREATE POLICY "Public journals are viewable"
ON journals FOR SELECT
USING (is_public = true);

-- Only admins can modify
CREATE POLICY "Admins can modify journals"
ON journals FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid() AND plan = 'admin'
    )
);
```

## Auth Integration

### Auto-create Profile on Signup

```sql
-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO profiles (id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger on auth.users
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user();
```

### Get Current User Helper

```sql
-- Useful function for RLS policies
CREATE OR REPLACE FUNCTION current_user_id()
RETURNS UUID AS $$
BEGIN
    RETURN auth.uid();
END;
$$ LANGUAGE plpgsql STABLE;

-- Usage in policies
CREATE POLICY "Own data only"
ON my_table FOR ALL
USING (user_id = current_user_id());
```

## Migrations

### Migration Naming

```
YYYYMMDDHHMMSS_description.sql
20240115120000_create_users_table.sql
20240115120001_add_rls_policies.sql
20240116090000_add_search_history.sql
```

### Running Migrations

```bash
# Push migrations to Supabase
supabase db push

# Generate migration from diff
supabase db diff -f my_migration

# Reset database (development only!)
supabase db reset
```

### Safe Migration Patterns

```sql
-- Add column (safe)
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- Add column with default (safe)
ALTER TABLE profiles ADD COLUMN subscription_ends_at TIMESTAMPTZ;

-- Rename column (careful - breaks code)
ALTER TABLE profiles RENAME COLUMN name TO full_name;

-- Drop column (dangerous - backup first!)
ALTER TABLE profiles DROP COLUMN IF EXISTS old_column;
```

## Indexes

### When to Add Indexes

```sql
-- Foreign keys (almost always)
CREATE INDEX idx_searches_user_id ON search_history(user_id);

-- Frequently filtered columns
CREATE INDEX idx_profiles_plan ON profiles(plan);

-- Sorted queries
CREATE INDEX idx_searches_created_desc ON search_history(created_at DESC);

-- Full-text search
CREATE INDEX idx_journals_title_gin ON journals USING gin(to_tsvector('english', title));

-- Composite index for common query patterns
CREATE INDEX idx_searches_user_date ON search_history(user_id, created_at DESC);
```

### Check Index Usage

```sql
-- See if indexes are being used
EXPLAIN ANALYZE
SELECT * FROM search_history
WHERE user_id = 'xxx'
ORDER BY created_at DESC
LIMIT 10;
```

## Common Queries

### With Supabase Client (JavaScript)

```javascript
// Select with filter
const { data, error } = await supabase
    .from('search_history')
    .select('*')
    .eq('user_id', userId)
    .order('created_at', { ascending: false })
    .limit(10);

// Insert
const { data, error } = await supabase
    .from('saved_journals')
    .insert({ user_id: userId, journal_id: 'xxx', journal_title: 'Nature' })
    .select()
    .single();

// Update
const { data, error } = await supabase
    .from('profiles')
    .update({ name: 'New Name' })
    .eq('id', userId);

// Delete
const { error } = await supabase
    .from('saved_journals')
    .delete()
    .eq('id', journalId);

// Upsert (insert or update)
const { data, error } = await supabase
    .from('profiles')
    .upsert({ id: userId, name: 'Name' });
```

### With Supabase Client (Python)

```python
# Select
response = supabase.table("search_history") \
    .select("*") \
    .eq("user_id", user_id) \
    .order("created_at", desc=True) \
    .limit(10) \
    .execute()

# Insert
response = supabase.table("saved_journals") \
    .insert({"user_id": user_id, "journal_id": "xxx"}) \
    .execute()

# Update
response = supabase.table("profiles") \
    .update({"name": "New Name"}) \
    .eq("id", user_id) \
    .execute()

# Delete
response = supabase.table("saved_journals") \
    .delete() \
    .eq("id", journal_id) \
    .execute()
```

### Raw SQL (Edge Functions / Backend)

```sql
-- Aggregation
SELECT 
    DATE_TRUNC('day', created_at) as date,
    COUNT(*) as searches
FROM search_history
WHERE user_id = $1
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY date DESC
LIMIT 30;

-- Join
SELECT 
    s.*,
    p.name as user_name
FROM search_history s
JOIN profiles p ON s.user_id = p.id
WHERE s.created_at > NOW() - INTERVAL '7 days';
```

## Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| RLS blocking all queries | Check `auth.uid()` is set, use service_role for backend |
| "permission denied for table" | Enable RLS and add policies |
| Slow queries | Add indexes, check with EXPLAIN ANALYZE |
| Duplicate key error | Add UNIQUE constraint or use upsert |
| Foreign key violation | Ensure referenced row exists first |
| Migration failed | Check SQL syntax, run locally first |

## Security Checklist

- [ ] RLS enabled on ALL user data tables
- [ ] Policies use `auth.uid()` for user checks
- [ ] No `USING (true)` policies on sensitive data
- [ ] service_role key only in backend
- [ ] Sensitive columns excluded from SELECT *
- [ ] Indexes on foreign keys
- [ ] Migrations tested locally first

## File References

- **RLS Patterns**: See `references/rls-patterns.md`
- **Query Optimization**: See `references/optimization.md`
- **Migration Guide**: See `references/migrations.md`

## Quick Commands

```bash
# Supabase CLI
supabase start          # Start local
supabase db push        # Push migrations
supabase db reset       # Reset local DB
supabase db diff -f x   # Generate migration

# Generate types (TypeScript)
supabase gen types typescript --project-id YOUR_ID > types/database.ts
```
