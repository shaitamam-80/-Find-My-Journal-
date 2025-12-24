# RLS Patterns Reference

## Policy Types

### SELECT Policy
```sql
-- Who can read
CREATE POLICY "policy_name"
ON table_name FOR SELECT
USING (condition);
```

### INSERT Policy
```sql
-- Who can create (WITH CHECK validates new data)
CREATE POLICY "policy_name"
ON table_name FOR INSERT
WITH CHECK (condition);
```

### UPDATE Policy
```sql
-- Who can modify (USING = which rows, WITH CHECK = new values)
CREATE POLICY "policy_name"
ON table_name FOR UPDATE
USING (existing_row_condition)
WITH CHECK (new_values_condition);
```

### DELETE Policy
```sql
-- Who can remove
CREATE POLICY "policy_name"
ON table_name FOR DELETE
USING (condition);
```

### ALL Policy
```sql
-- Shorthand for all operations
CREATE POLICY "policy_name"
ON table_name FOR ALL
USING (condition)
WITH CHECK (condition);
```

---

## Common Patterns

### 1. User Owns Data

```sql
-- Most common pattern: users access only their own data
CREATE POLICY "Users own their data"
ON user_data FOR ALL
USING (auth.uid() = user_id)
WITH CHECK (auth.uid() = user_id);
```

### 2. Team/Organization Access

```sql
-- Users in same organization can see each other's data
CREATE POLICY "Team members can view"
ON team_data FOR SELECT
USING (
    organization_id IN (
        SELECT organization_id FROM organization_members
        WHERE user_id = auth.uid()
    )
);
```

### 3. Role-Based Access

```sql
-- Different access levels based on role
CREATE POLICY "Admins have full access"
ON sensitive_data FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid() AND role = 'admin'
    )
);

CREATE POLICY "Users can view own data"
ON sensitive_data FOR SELECT
USING (user_id = auth.uid());
```

### 4. Public + Private Data

```sql
-- Some data public, some private
CREATE POLICY "Public items viewable by all"
ON items FOR SELECT
USING (is_public = true);

CREATE POLICY "Private items viewable by owner"
ON items FOR SELECT
USING (is_public = false AND user_id = auth.uid());

-- Combine: OR connects multiple policies automatically
```

### 5. Time-Based Access

```sql
-- Access expires after certain time
CREATE POLICY "Active subscriptions only"
ON premium_content FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM subscriptions
        WHERE user_id = auth.uid()
        AND expires_at > NOW()
    )
);
```

### 6. Invite-Based Access

```sql
-- Access through invitations
CREATE POLICY "Invited users can view"
ON shared_documents FOR SELECT
USING (
    user_id = auth.uid()
    OR
    EXISTS (
        SELECT 1 FROM document_invites
        WHERE document_id = shared_documents.id
        AND invitee_email = auth.jwt() ->> 'email'
    )
);
```

### 7. Hierarchical Access (Manager sees team)

```sql
-- Managers can see their team's data
CREATE POLICY "Managers see team data"
ON employee_records FOR SELECT
USING (
    user_id = auth.uid()
    OR
    EXISTS (
        SELECT 1 FROM team_members
        WHERE manager_id = auth.uid()
        AND member_id = employee_records.user_id
    )
);
```

---

## Helper Functions

### Get User Role

```sql
CREATE OR REPLACE FUNCTION auth.user_role()
RETURNS TEXT AS $$
BEGIN
    RETURN (
        SELECT role FROM profiles
        WHERE id = auth.uid()
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Usage in policy
CREATE POLICY "Role check"
ON table FOR ALL
USING (auth.user_role() = 'admin');
```

### Check Premium Status

```sql
CREATE OR REPLACE FUNCTION auth.is_premium()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM profiles
        WHERE id = auth.uid()
        AND plan IN ('premium', 'admin')
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Usage
CREATE POLICY "Premium feature access"
ON premium_features FOR SELECT
USING (auth.is_premium());
```

---

## Debugging RLS

### Test as User

```sql
-- In Supabase SQL Editor
SET request.jwt.claim.sub = 'user-uuid-here';
SET request.jwt.claim.role = 'authenticated';

-- Now run queries to test RLS
SELECT * FROM protected_table;
```

### Check Policies

```sql
-- List all policies on a table
SELECT * FROM pg_policies WHERE tablename = 'your_table';

-- Disable RLS temporarily (testing only!)
ALTER TABLE your_table DISABLE ROW LEVEL SECURITY;

-- Re-enable
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;
```

### Common Mistakes

```sql
-- ❌ WRONG: No auth check
CREATE POLICY "Bad policy"
ON data FOR SELECT
USING (true);  -- Everyone can read everything!

-- ✅ CORRECT: Auth check
CREATE POLICY "Good policy"
ON data FOR SELECT
USING (auth.uid() = user_id);

-- ❌ WRONG: Missing WITH CHECK on INSERT
CREATE POLICY "Bad insert"
ON data FOR INSERT
USING (auth.uid() = user_id);  -- USING doesn't work for INSERT

-- ✅ CORRECT: Use WITH CHECK
CREATE POLICY "Good insert"
ON data FOR INSERT
WITH CHECK (auth.uid() = user_id);
```

---

## Complete Example: Multi-tenant SaaS

```sql
-- Organizations
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Members
CREATE TABLE organization_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member')),
    UNIQUE(organization_id, user_id)
);

-- Projects (belong to organizations)
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    created_by UUID REFERENCES auth.users(id)
);

-- Enable RLS
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE organization_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Members see their orgs"
ON organizations FOR SELECT
USING (
    id IN (
        SELECT organization_id FROM organization_members
        WHERE user_id = auth.uid()
    )
);

CREATE POLICY "Members see membership"
ON organization_members FOR SELECT
USING (
    organization_id IN (
        SELECT organization_id FROM organization_members
        WHERE user_id = auth.uid()
    )
);

CREATE POLICY "Members see org projects"
ON projects FOR SELECT
USING (
    organization_id IN (
        SELECT organization_id FROM organization_members
        WHERE user_id = auth.uid()
    )
);

CREATE POLICY "Admins can create projects"
ON projects FOR INSERT
WITH CHECK (
    EXISTS (
        SELECT 1 FROM organization_members
        WHERE organization_id = projects.organization_id
        AND user_id = auth.uid()
        AND role IN ('owner', 'admin')
    )
);
```
