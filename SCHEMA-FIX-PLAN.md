# Schema Fix Plan

## Problem Summary

The test file expects different table/column names than what the migration created.

## Actual Schema (from migration)

### Tables Created:
1. `query_attempts` - All query classification attempts
2. `clarification_interactions` - User clarification interactions  
3. `learned_patterns` - Learned query patterns
4. `pattern_performance` - Daily pattern metrics

### Key Columns in `learned_patterns`:
- `pattern_text` TEXT NOT NULL
- `pattern_type` VARCHAR(20)
- `intent` VARCHAR(50) NOT NULL
- `confidence` DECIMAL(3,2) DEFAULT 0.75
- `success_rate` DECIMAL(3,2)
- `occurrence_count` INTEGER
- `success_count` INTEGER
- `failure_count` INTEGER

## Recommended Fix: Update Code to Match Migration

### Why This Approach?
1. ✅ Migration has better, more comprehensive schema
2. ✅ Migration already deployed to database
3. ✅ Migration has proper relationships and indexes
4. ✅ Migration includes analytics views and helper functions
5. ✅ Less risky than altering deployed schema

### Changes Required:

#### 1. Update Test File
**File**: `tests/test-clarification-learning.js`

Change:
```javascript
// OLD
FROM clarification_history
// NEW  
FROM clarification_interactions

// OLD
confidence_boost
// NEW
confidence
```

#### 2. Update LearningEngine
**File**: `lib/intent/learning-engine.js`

In `recordPattern()` method, ensure we provide:
```javascript
{
  pattern_text: pattern.query_pattern,  // Map query_pattern → pattern_text
  pattern_type: 'phrase',               // Add pattern_type
  intent: pattern.intent,
  confidence: pattern.confidence_boost || 0.75,  // Map confidence_boost → confidence
  example_queries: pattern.example_queries || []
}
```

#### 3. Update ClarificationEngine  
**File**: `lib/intent/clarification-engine.js`

Use table name `clarification_interactions` instead of `clarification_history`

#### 4. Add Missing Methods

Both engines need these methods implemented to match the migration schema:

**ClarificationEngine**:
- `needsClarification(classification)` - Check if confidence < threshold
- `generateOptions(query, classification)` - Create clarification choices
- `recordClarification(...)` - Insert into `clarification_interactions`

**LearningEngine**:
- `findSimilarPatterns(query)` - Query `learned_patterns` table
- `recordPatternSuccess(patternId, wasSuccessful)` - Update success metrics

## Implementation Steps

### Step 1: Fix Test File (5 min)
Update table and column names to match migration

### Step 2: Fix LearningEngine.recordPattern() (10 min)
Map input parameters to correct column names:
- `query_pattern` → `pattern_text`
- `confidence_boost` → `confidence`
- Add `pattern_type` field

### Step 3: Implement Missing Methods (1-2 hours)
Add the 5 missing methods using the actual schema

### Step 4: Run Tests (5 min)
Verify all tests pass

## SQL Reference for Implementation

### Insert into clarification_interactions:
```sql
INSERT INTO clarification_interactions (
  query_attempt_id,
  clarification_type,
  options_presented,
  user_selection,
  resolved_intent,
  was_helpful
) VALUES ($1, $2, $3, $4, $5, $6)
RETURNING id;
```

### Insert into learned_patterns:
```sql
INSERT INTO learned_patterns (
  pattern_text,
  pattern_type,
  intent,
  confidence,
  example_queries
) VALUES ($1, $2, $3, $4, $5)
RETURNING id;
```

### Query learned_patterns:
```sql
SELECT * FROM learned_patterns
WHERE is_active = true
  AND pattern_text ILIKE $1
ORDER BY success_rate DESC NULLS LAST, confidence DESC
LIMIT 10;
```

### Update pattern success:
```sql
UPDATE learned_patterns
SET 
  success_count = success_count + $2,
  failure_count = failure_count + $3,
  occurrence_count = occurrence_count + 1
WHERE id = $1;
-- Trigger will auto-update success_rate
```

## Benefits of This Approach

1. **Comprehensive Schema** - Migration includes analytics, triggers, and helper functions
2. **Better Organization** - Separate tables for attempts, interactions, and patterns
3. **Built-in Analytics** - `pattern_analytics` view for monitoring
4. **Auto-calculations** - Triggers maintain success_rate automatically
5. **Future-proof** - Room for expansion with query_attempts table

## Alternative (Not Recommended)

We could create a new migration to rename tables/columns, but this:
- ❌ Requires another migration
- ❌ Loses the better schema design
- ❌ More complex to maintain
- ❌ Doesn't leverage existing analytics features

## Conclusion

**Update the code to match the migration schema.** This gives us a better foundation for the clarification and learning system.
