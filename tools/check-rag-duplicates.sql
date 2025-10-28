-- ============================================================
-- SQL Queries to Check for Duplicates in RAG/Vector Store
-- ============================================================

-- 1. Check for duplicate IDs in rules_content
-- ============================================================
SELECT 
    id,
    COUNT(*) as duplicate_count
FROM rules_content
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 2. Check for duplicate content (exact matches)
-- ============================================================
SELECT 
    content,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM rules_content
GROUP BY content
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- 3. Check for duplicate embeddings (same vector)
-- ============================================================
SELECT 
    embedding::text as embedding_text,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM rules_content
WHERE embedding IS NOT NULL
GROUP BY embedding::text
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- 4. Check for near-duplicate content (similar text)
-- Using first 100 characters as a simple similarity check
-- ============================================================
SELECT 
    LEFT(content, 100) as content_preview,
    COUNT(*) as similar_count,
    array_agg(id) as similar_ids
FROM rules_content
GROUP BY LEFT(content, 100)
HAVING COUNT(*) > 1
ORDER BY similar_count DESC
LIMIT 20;

-- 5. Check for duplicate source references
-- ============================================================
SELECT 
    source,
    page_reference,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM rules_content
WHERE source IS NOT NULL
GROUP BY source, page_reference
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- 6. Summary statistics for rules_content
-- ============================================================
SELECT 
    'Total Records' as metric,
    COUNT(*) as value
FROM rules_content
UNION ALL
SELECT 
    'Records with Embeddings',
    COUNT(*)
FROM rules_content
WHERE embedding IS NOT NULL
UNION ALL
SELECT 
    'Records without Embeddings',
    COUNT(*)
FROM rules_content
WHERE embedding IS NULL
UNION ALL
SELECT 
    'Unique Content Pieces',
    COUNT(DISTINCT content)
FROM rules_content
UNION ALL
SELECT 
    'Unique Sources',
    COUNT(DISTINCT source)
FROM rules_content
WHERE source IS NOT NULL;

-- 7. Check for duplicate chunks from same source
-- (chunks that might have been split incorrectly)
-- ============================================================
SELECT 
    source,
    COUNT(*) as chunk_count,
    array_agg(id ORDER BY id) as chunk_ids
FROM rules_content
WHERE source IS NOT NULL
GROUP BY source
HAVING COUNT(*) > 1
ORDER BY chunk_count DESC
LIMIT 20;

-- 8. Find potential duplicate content by length and source
-- ============================================================
SELECT 
    source,
    LENGTH(content) as content_length,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM rules_content
GROUP BY source, LENGTH(content)
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- 9. Check for empty or null content
-- ============================================================
SELECT 
    'Empty Content' as issue_type,
    COUNT(*) as count
FROM rules_content
WHERE content IS NULL OR content = ''
UNION ALL
SELECT 
    'Null Embeddings',
    COUNT(*)
FROM rules_content
WHERE embedding IS NULL;

-- 10. Advanced: Find semantically similar content using vector similarity
-- (Only works if you have embeddings)
-- This finds pairs of documents with very similar embeddings
-- ============================================================
WITH similar_pairs AS (
    SELECT 
        a.id as id1,
        b.id as id2,
        1 - (a.embedding <=> b.embedding) as similarity
    FROM rules_content a
    CROSS JOIN rules_content b
    WHERE a.id < b.id
        AND a.embedding IS NOT NULL
        AND b.embedding IS NOT NULL
        AND 1 - (a.embedding <=> b.embedding) > 0.95  -- 95% similar
    LIMIT 100
)
SELECT 
    id1,
    id2,
    similarity,
    (SELECT LEFT(content, 100) FROM rules_content WHERE id = id1) as content1_preview,
    (SELECT LEFT(content, 100) FROM rules_content WHERE id = id2) as content2_preview
FROM similar_pairs
ORDER BY similarity DESC;
