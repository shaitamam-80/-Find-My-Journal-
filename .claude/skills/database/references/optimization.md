# Query Optimization Reference

## Indexing Strategies

### When to Add Indexes

```sql
-- 1. Foreign Keys (almost always)
CREATE INDEX idx_posts_user_id ON posts(user_id);

-- 2. Frequently filtered columns
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_status ON orders(status);

-- 3. Sorted/ordered queries
CREATE INDEX idx_posts_created_desc ON posts(created_at DESC);

-- 4. Unique lookups
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
```

### Composite Indexes

```sql
-- For queries that filter on multiple columns
-- Order matters! Put most selective first

-- Query: WHERE user_id = X AND created_at > Y
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at DESC);

-- Query: WHERE status = X AND created_at > Y ORDER BY created_at
CREATE INDEX idx_orders_status_date ON orders(status, created_at DESC);
```

### Partial Indexes

```sql
-- Index only subset of rows
-- Saves space, faster for specific queries

-- Only active users
CREATE INDEX idx_users_active ON users(email) WHERE is_active = true;

-- Only recent data
CREATE INDEX idx_logs_recent ON logs(created_at) 
WHERE created_at > '2024-01-01';

-- Only pending orders
CREATE INDEX idx_orders_pending ON orders(created_at)
WHERE status = 'pending';
```

### Full-Text Search

```sql
-- GIN index for text search
CREATE INDEX idx_articles_content_gin 
ON articles USING gin(to_tsvector('english', title || ' ' || content));

-- Query
SELECT * FROM articles
WHERE to_tsvector('english', title || ' ' || content) @@ to_tsquery('search & term');
```

---

## EXPLAIN ANALYZE

### Understanding Output

```sql
EXPLAIN ANALYZE
SELECT * FROM posts
WHERE user_id = 'xxx'
ORDER BY created_at DESC
LIMIT 10;

-- Output:
-- Limit  (cost=0.42..12.45 rows=10 width=100) (actual time=0.05..0.08 rows=10 loops=1)
--   ->  Index Scan using idx_posts_user_date on posts
--        Index Cond: (user_id = 'xxx')
-- Planning Time: 0.2 ms
-- Execution Time: 0.1 ms
```

### What to Look For

| Term | Good | Bad |
|------|------|-----|
| Scan Type | Index Scan | Seq Scan (on big tables) |
| Rows | Close to actual | Way off (stale stats) |
| Time | < 100ms | > 1000ms |
| Cost | Lower is better | Very high |

### Common Problems

```sql
-- ❌ Sequential Scan (bad on large tables)
Seq Scan on posts (cost=0.00..1234.00 rows=50000)

-- ✅ Index Scan (good)
Index Scan using idx_posts_user_id on posts (cost=0.42..8.44 rows=1)

-- ❌ Sort (expensive)
Sort (cost=1000.00..1050.00 rows=20000)

-- ✅ Index provides ordering
Index Scan Backward using idx_posts_created on posts
```

---

## Query Patterns

### Efficient Pagination

```sql
-- ❌ OFFSET is slow for large offsets
SELECT * FROM posts
ORDER BY created_at DESC
LIMIT 20 OFFSET 10000;  -- Scans 10,020 rows!

-- ✅ Cursor-based pagination (fast)
SELECT * FROM posts
WHERE created_at < '2024-01-15T10:00:00Z'  -- Last item's timestamp
ORDER BY created_at DESC
LIMIT 20;
```

### Batch Operations

```sql
-- ❌ Single inserts in loop (slow)
INSERT INTO logs (user_id, action) VALUES ('a', 'view');
INSERT INTO logs (user_id, action) VALUES ('b', 'click');
-- ... 1000 more

-- ✅ Batch insert (fast)
INSERT INTO logs (user_id, action)
VALUES 
    ('a', 'view'),
    ('b', 'click'),
    -- ... up to 1000 per batch
;
```

### Avoid SELECT *

```sql
-- ❌ Fetches all columns
SELECT * FROM users WHERE id = 'xxx';

-- ✅ Only needed columns
SELECT id, name, email FROM users WHERE id = 'xxx';
```

### Use EXISTS Instead of COUNT

```sql
-- ❌ Counts all matching rows
SELECT COUNT(*) > 0 FROM posts WHERE user_id = 'xxx';

-- ✅ Stops at first match
SELECT EXISTS (SELECT 1 FROM posts WHERE user_id = 'xxx');
```

### Avoid Functions on Indexed Columns

```sql
-- ❌ Can't use index on created_at
SELECT * FROM posts WHERE DATE(created_at) = '2024-01-15';

-- ✅ Can use index
SELECT * FROM posts 
WHERE created_at >= '2024-01-15' 
AND created_at < '2024-01-16';
```

---

## Supabase-Specific Optimization

### Use .single() When Expecting One Row

```javascript
// ❌ Returns array, extra processing
const { data } = await supabase
    .from('users')
    .select('*')
    .eq('id', userId);
const user = data[0];

// ✅ Returns object directly
const { data: user } = await supabase
    .from('users')
    .select('*')
    .eq('id', userId)
    .single();
```

### Select Only Needed Columns

```javascript
// ❌ All columns
const { data } = await supabase
    .from('posts')
    .select('*');

// ✅ Only needed
const { data } = await supabase
    .from('posts')
    .select('id, title, created_at');
```

### Use Count Efficiently

```javascript
// Get count without fetching data
const { count } = await supabase
    .from('posts')
    .select('*', { count: 'exact', head: true })
    .eq('user_id', userId);
```

### Batch with .in()

```javascript
// ❌ Multiple queries
const post1 = await supabase.from('posts').select().eq('id', 'a');
const post2 = await supabase.from('posts').select().eq('id', 'b');

// ✅ Single query
const { data } = await supabase
    .from('posts')
    .select()
    .in('id', ['a', 'b', 'c']);
```

---

## Monitoring

### Check Slow Queries

```sql
-- In Supabase Dashboard > Database > Query Performance
-- Or enable pg_stat_statements

SELECT 
    query,
    calls,
    mean_exec_time,
    total_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;
```

### Check Table Sizes

```sql
SELECT 
    relname as table,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as data_size,
    pg_size_pretty(pg_indexes_size(relid)) as index_size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### Check Index Usage

```sql
SELECT 
    indexrelname as index,
    idx_scan as times_used,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

---

## Quick Wins

| Problem | Solution |
|---------|----------|
| Slow user lookups | Add index on user_id |
| Slow ordering | Add index with DESC |
| Slow text search | Add GIN index |
| High memory | Select fewer columns |
| Slow pagination | Use cursor-based |
| Slow counts | Use EXISTS or head:true |
