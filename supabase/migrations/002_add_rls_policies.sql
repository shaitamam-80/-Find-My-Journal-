-- Additional RLS Policies for Sprint 2
-- Run this in Supabase SQL Editor

-- Allow users to update their own profile (for incrementing search count)
CREATE POLICY "Users can update own profile" ON public.profiles
  FOR UPDATE USING (auth.uid() = id);

-- Allow users to insert their own search logs
CREATE POLICY "Users can insert own logs" ON public.search_logs
  FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Allow service role to read all profiles (for admin stats)
-- Note: This uses the service_role key, not anon key
CREATE POLICY "Service role can read all profiles" ON public.profiles
  FOR SELECT USING (auth.role() = 'service_role');

CREATE POLICY "Service role can read all logs" ON public.search_logs
  FOR SELECT USING (auth.role() = 'service_role');
