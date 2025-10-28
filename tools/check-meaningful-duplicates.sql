-- ============================================================
-- Check for MEANINGFUL Duplicates (by name, content, etc.)
-- Not just IDs which are sequences
-- ============================================================

-- 1. METATYPES - Check for duplicate names
-- ============================================================
SELECT 
    name,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM metatypes
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 2. POWERS - Check for duplicate names
-- ============================================================
SELECT 
    name,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM powers
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 3. SPELLS - Check for duplicate names
-- ============================================================
SELECT 
    name,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM spells
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 4. TOTEMS - Check for duplicate names
-- ============================================================
SELECT 
    name,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM totems
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 5. GEAR - Check for duplicate names
-- ============================================================
SELECT 
    name,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM gear
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 50;

-- 6. GEAR - Check for duplicate name + category combinations
-- (More specific - same item in same category)
-- ============================================================
SELECT 
    name,
    category,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM gear
GROUP BY name, category
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 50;

-- 7. RULES_CONTENT - Check for duplicate content (exact text)
-- ============================================================
SELECT 
    LEFT(content, 100) as content_preview,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM rules_content
GROUP BY content
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- 8. RULES_CONTENT - Check for duplicate source + page combinations
-- (Same content from same source page)
-- ============================================================
SELECT 
    source,
    page_reference,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM rules_content
WHERE source IS NOT NULL AND page_reference IS NOT NULL
GROUP BY source, page_reference
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC
LIMIT 20;

-- 9. SUMMARY - Count duplicates across all tables
-- ============================================================
SELECT 'metatypes' as table_name, 
       COUNT(*) as total_records,
       COUNT(DISTINCT name) as unique_names,
       COUNT(*) - COUNT(DISTINCT name) as duplicate_count
FROM metatypes
UNION ALL
SELECT 'powers', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name)
FROM powers
UNION ALL
SELECT 'spells', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name)
FROM spells
UNION ALL
SELECT 'totems', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name)
FROM totems
UNION ALL
SELECT 'gear', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name)
FROM gear
UNION ALL
SELECT 'rules_content', COUNT(*), COUNT(DISTINCT content), COUNT(*) - COUNT(DISTINCT content)
FROM rules_content;

-- 10. GEAR - Find items with same name but different stats
-- (Potential data quality issue)
-- ============================================================
SELECT 
    name,
    COUNT(*) as variant_count,
    array_agg(DISTINCT category) as categories,
    array_agg(DISTINCT cost) as costs,
    array_agg(id) as all_ids
FROM gear
GROUP BY name
HAVING COUNT(*) > 1
ORDER BY variant_count DESC
LIMIT 30;

-- 11. POWERS - Check for duplicate name + power_type combinations
-- (Same power for same type - likely true duplicate)
-- ============================================================
SELECT 
    name,
    power_type,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM powers
GROUP BY name, power_type
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- 12. SPELLS - Check for duplicate name + category combinations
-- ============================================================
SELECT 
    name,
    category,
    COUNT(*) as duplicate_count,
    array_agg(id) as duplicate_ids
FROM spells
GROUP BY name, category
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;


SELECT 'metatypes' as table_name, 
       COUNT(*) as total_records,
       COUNT(DISTINCT name) as unique_names,
       COUNT(*) - COUNT(DISTINCT name) as duplicate_count
FROM metatypes
UNION ALL
SELECT 'powers', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name) FROM powers
UNION ALL
SELECT 'spells', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name) FROM spells
UNION ALL
SELECT 'totems', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name) FROM totems
UNION ALL
SELECT 'gear', COUNT(*), COUNT(DISTINCT name), COUNT(*) - COUNT(DISTINCT name) FROM gear
UNION ALL
SELECT 'rules_content', COUNT(*), COUNT(DISTINCT content), COUNT(*) - COUNT(DISTINCT content) FROM rules_content;
UNION ALL
SELECT 'query_text', COUNT(*), COUNT(DISTINCT query_text), COUNT(*) - COUNT(DISTINCT query_text) FROM query_logs;
