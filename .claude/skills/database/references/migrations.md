# Migrations Reference

## Migration Basics

### File Naming

```
YYYYMMDDHHMMSS_description.sql
```

Examples:
```
20240115120000_create_users_table.sql
20240115120001_add_rls_policies.sql
20240116090000_add_indexes.sql
20240120140000_add_subscriptions.sql
```

### Migration Structure

```sql
-- migrations/20240115120000_create_users_table.sql

-- Description: Create users table with basic fields
-- Author: Your Name
-- Date: 2024-01-15

-- Up Migration
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Note: Supabase doesn't have built-in down migrations
-- Document rollback in comments:
-- Rollback: DROP TABLE users;
```

---

## Supabase CLI Commands

```bash
# Start local Supabase
supabase start

# Stop local Supabase
supabase stop

# Push migrations to remote
supabase db push

# Pull remote changes to local
supabase db pull

# Generate migration from diff
supabase db diff -f migration_name

# Reset local database (runs all migrations fresh)
supabase db reset

# Check migration status
supabase migration list
```

---

## Safe Migration Patterns

### Adding Columns

```sql
-- ✅ Safe: Add nullable column
ALTER TABLE users ADD COLUMN avatar_url TEXT;

-- ✅ Safe: Add column with default
ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT true;

-- ⚠️ Careful: Add NOT NULL column
-- Step 1: Add nullable
ALTER TABLE users ADD COLUMN name TEXT;
-- Step 2: Backfill data
UPDATE users SET name = 'Unknown' WHERE name IS NULL;
-- Step 3: Add constraint
ALTER TABLE users ALTER COLUMN name SET NOT NULL;
```

### Renaming Columns

```sql
-- ⚠️ Breaking change! Update code first
ALTER TABLE users RENAME COLUMN name TO full_name;

-- Safer approach: 
-- 1. Add new column
ALTER TABLE users ADD COLUMN full_name TEXT;
-- 2. Copy data
UPDATE users SET full_name = name;
-- 3. Update code to use full_name
-- 4. Drop old column (later migration)
ALTER TABLE users DROP COLUMN name;
```

### Dropping Columns

```sql
-- ⚠️ Dangerous! Ensure no code uses it
ALTER TABLE users DROP COLUMN IF EXISTS old_column;
```

### Adding Indexes

```sql
-- ✅ Safe: Create index concurrently (no table lock)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Note: CONCURRENTLY not supported in Supabase migrations
-- Use regular CREATE INDEX for small tables
CREATE INDEX idx_users_email ON users(email);
```

### Modifying Types

```sql
-- ✅ Safe: Expand varchar
ALTER TABLE users ALTER COLUMN name TYPE VARCHAR(500);

-- ⚠️ Careful: Shrink varchar (may fail if data too long)
ALTER TABLE users ALTER COLUMN name TYPE VARCHAR(100);

-- ✅ Safe: Change to text
ALTER TABLE users ALTER COLUMN name TYPE TEXT;
```

---

## RLS Migration Pattern

```sql
-- migrations/20240115120001_add_users_rls.sql

-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Drop existing policies (if re-running)
DROP POLICY IF EXISTS "Users can view own data" ON users;
DROP POLICY IF EXISTS "Users can update own data" ON users;

-- Create policies
CREATE POLICY "Users can view own data"
ON users FOR SELECT
USING (auth.uid() = id);

CREATE POLICY "Users can update own data"
ON users FOR UPDATE
USING (auth.uid() = id)
WITH CHECK (auth.uid() = id);
```

---

## Trigger Migration Pattern

```sql
-- migrations/20240115120002_add_updated_at_trigger.sql

-- Create function (if not exists)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop existing trigger (if re-running)
DROP TRIGGER IF EXISTS set_updated_at ON users;

-- Create trigger
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Auth Trigger Pattern

```sql
-- migrations/20240115120003_auto_create_profile.sql

-- Function to handle new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(
            NEW.raw_user_meta_data->>'name',
            split_part(NEW.email, '@', 1)
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing trigger
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Create trigger on auth.users
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();
```

---

## Seed Data

```sql
-- supabase/seed.sql (runs after migrations on db reset)

-- Insert default data
INSERT INTO categories (name, slug) VALUES
    ('Technology', 'technology'),
    ('Science', 'science'),
    ('Health', 'health')
ON CONFLICT (slug) DO NOTHING;

-- Insert test user (development only!)
-- Note: This won't work for auth.users, use Supabase dashboard
```

---

## Migration Checklist

### Before Writing
- [ ] Check if column/table already exists
- [ ] Plan for rollback
- [ ] Consider data migration needs

### In Migration
- [ ] Use IF EXISTS / IF NOT EXISTS
- [ ] Add indexes for foreign keys
- [ ] Enable RLS on new tables
- [ ] Add appropriate policies

### After Migration
- [ ] Test locally with `supabase db reset`
- [ ] Check with EXPLAIN for new queries
- [ ] Update TypeScript types
- [ ] Update API code if needed

---

## Troubleshooting

### Migration Failed

```bash
# Check error in Supabase dashboard > Database > Migrations

# Fix SQL and re-run
supabase db push

# Or reset local and try again
supabase db reset
```

### Conflicts with Remote

```bash
# Pull remote changes first
supabase db pull

# Then push your changes
supabase db push
```

### Types Out of Sync

```bash
# Regenerate TypeScript types
supabase gen types typescript --project-id YOUR_ID > src/types/database.ts
```

---

## Example: Full Feature Migration

```sql
-- migrations/20240120100000_add_subscriptions.sql

-- 1. Create table
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan TEXT NOT NULL CHECK (plan IN ('free', 'premium', 'enterprise')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'expired')),
    starts_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Add indexes
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);

-- 3. Add trigger for updated_at
CREATE TRIGGER set_subscriptions_updated_at
    BEFORE UPDATE ON subscriptions
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. Enable RLS
ALTER TABLE subscriptions ENABLE ROW LEVEL SECURITY;

-- 5. Add policies
CREATE POLICY "Users can view own subscriptions"
ON subscriptions FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Service role manages subscriptions"
ON subscriptions FOR ALL
USING (auth.jwt() ->> 'role' = 'service_role');

-- 6. Update profiles to reference current plan
ALTER TABLE profiles ADD COLUMN IF NOT EXISTS current_subscription_id UUID REFERENCES subscriptions(id);
```
