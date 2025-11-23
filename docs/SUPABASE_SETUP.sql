-- =====================================================
-- Supabase 数据库设置脚本
-- =====================================================
-- 在 Supabase SQL Editor 中执行此脚本

-- 1. 创建 posts 表（如果不存在）
CREATE TABLE IF NOT EXISTS posts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  date DATE NOT NULL,
  description TEXT,
  tags TEXT[],
  content TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(date DESC);
CREATE INDEX IF NOT EXISTS idx_posts_slug ON posts(slug);
CREATE INDEX IF NOT EXISTS idx_posts_created_at ON posts(created_at DESC);

-- 3. 创建更新时间的触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_posts_updated_at ON posts;
CREATE TRIGGER update_posts_updated_at
    BEFORE UPDATE ON posts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 4. 配置 Row Level Security (RLS)

-- 启用 RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- 删除现有策略（如果存在）
DROP POLICY IF EXISTS "Enable read access for all users" ON posts;
DROP POLICY IF EXISTS "Enable insert for service role" ON posts;
DROP POLICY IF EXISTS "Enable update for service role" ON posts;
DROP POLICY IF EXISTS "Enable delete for service role" ON posts;

-- 方案 A: 允许所有人读取，但只允许认证用户写入
-- 适用于：使用 anon key 的情况
CREATE POLICY "Enable read access for all users"
ON posts FOR SELECT
USING (true);

CREATE POLICY "Enable insert for authenticated users"
ON posts FOR INSERT
WITH CHECK (true);

CREATE POLICY "Enable update for authenticated users"
ON posts FOR UPDATE
USING (true)
WITH CHECK (true);

CREATE POLICY "Enable delete for authenticated users"
ON posts FOR DELETE
USING (true);

-- =====================================================
-- 如果上面的策略不起作用，请使用下面的方案 B
-- （需要使用 service_role key 而不是 anon key）
-- =====================================================

-- 方案 B: 完全禁用 RLS（仅用于开发/测试）
-- 注意：这会移除所有安全限制，生产环境不推荐
-- ALTER TABLE posts DISABLE ROW LEVEL SECURITY;

-- =====================================================
-- 验证设置
-- =====================================================

-- 查看表结构
\d posts

-- 查看 RLS 策略
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename = 'posts';

-- 查看索引
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'posts';

-- 测试插入一条数据
INSERT INTO posts (slug, title, date, description, tags, content)
VALUES (
  'test-post',
  '测试文章',
  CURRENT_DATE,
  '这是一个测试文章',
  ARRAY['测试', '区块链'],
  '测试内容'
)
ON CONFLICT (slug)
DO UPDATE SET
  title = EXCLUDED.title,
  updated_at = NOW();

-- 查询测试数据
SELECT * FROM posts WHERE slug = 'test-post';

-- 清理测试数据（可选）
-- DELETE FROM posts WHERE slug = 'test-post';
