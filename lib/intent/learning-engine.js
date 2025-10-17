/**
 * Learning Engine
 * Learns patterns from user feedback and improves classification over time
 */

export class LearningEngine {
  constructor(database) {
    this.db = database;
    
    // Stop words to filter out when extracting patterns
    this.stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
      'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
      'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
      'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
      'what', 'which', 'who', 'when', 'where', 'why', 'how'
    ]);
    
    // Minimum occurrences before a pattern is considered reliable
    this.minOccurrencesForActivation = 3;
    
    // Minimum success rate to keep a pattern active
    this.minSuccessRate = 50;
  }
  
  /**
   * Process user feedback from clarification interaction
   */
  async processClarificationFeedback(queryAttemptId, userSelection, resolvedIntent) {
    if (!this.db) {
      console.warn('No database connection - skipping learning');
      return;
    }
    
    try {
      // Get the original query
      const queryResult = await this.db.query(`
        SELECT query_text, normalized_query, intent_detected, confidence
        FROM query_attempts
        WHERE id = $1
      `, [queryAttemptId]);
      
      if (queryResult.rows.length === 0) {
        console.warn('Query attempt not found:', queryAttemptId);
        return;
      }
      
      const { query_text, normalized_query } = queryResult.rows[0];
      
      // Update the query attempt with final intent
      await this.db.query(`
        UPDATE query_attempts
        SET final_intent = $1, classification_method = 'clarified'
        WHERE id = $2
      `, [resolvedIntent, queryAttemptId]);
      
      // Extract and learn patterns
      await this.learnFromQuery(normalized_query, resolvedIntent, queryAttemptId);
      
      console.log(`✓ Learned from clarification: "${query_text}" → ${resolvedIntent}`);
    } catch (error) {
      console.error('Error processing clarification feedback:', error);
    }
  }
  
  /**
   * Learn patterns from a resolved query
   */
  async learnFromQuery(query, intent, queryAttemptId) {
    const patterns = this.extractPatterns(query);
    
    for (const pattern of patterns) {
      await this.recordPattern(pattern, intent, queryAttemptId, query);
    }
  }
  
  /**
   * Extract potential patterns from a query
   */
  extractPatterns(query) {
    const patterns = [];
    const words = query.toLowerCase().split(/\s+/).filter(w => w.length > 0);
    
    // Extract bigrams (2-word phrases)
    for (let i = 0; i < words.length - 1; i++) {
      const bigram = words.slice(i, i + 2).join(' ');
      if (this.isSignificantPhrase(bigram)) {
        patterns.push({
          text: bigram,
          type: 'phrase',
          confidence: 0.70
        });
      }
    }
    
    // Extract trigrams (3-word phrases)
    for (let i = 0; i < words.length - 2; i++) {
      const trigram = words.slice(i, i + 3).join(' ');
      if (this.isSignificantPhrase(trigram)) {
        patterns.push({
          text: trigram,
          type: 'phrase',
          confidence: 0.75
        });
      }
    }
    
    // Extract significant keywords
    const keywords = words.filter(w => 
      w.length > 3 && !this.stopWords.has(w)
    );
    
    for (const keyword of keywords) {
      patterns.push({
        text: keyword,
        type: 'keyword',
        confidence: 0.65
      });
    }
    
    // Extract potential regex patterns
    const regexPatterns = this.extractRegexPatterns(query);
    patterns.push(...regexPatterns);
    
    return patterns;
  }
  
  /**
   * Check if a phrase is significant (not all stop words)
   */
  isSignificantPhrase(phrase) {
    const words = phrase.split(/\s+/);
    const significantWords = words.filter(w => !this.stopWords.has(w));
    return significantWords.length > 0;
  }
  
  /**
   * Extract regex patterns from query
   */
  extractRegexPatterns(query) {
    const patterns = [];
    
    // Pattern: "how does X work"
    if (/how does .+ work/i.test(query)) {
      patterns.push({
        text: 'how does .* work',
        type: 'regex',
        confidence: 0.85
      });
    }
    
    // Pattern: "what is X"
    if (/what is .+/i.test(query)) {
      patterns.push({
        text: 'what is .*',
        type: 'regex',
        confidence: 0.80
      });
    }
    
    // Pattern: "list all X"
    if (/list all .+/i.test(query)) {
      patterns.push({
        text: 'list all .*',
        type: 'regex',
        confidence: 0.90
      });
    }
    
    // Pattern: "compare X and Y"
    if (/compare .+ and .+/i.test(query)) {
      patterns.push({
        text: 'compare .* and .*',
        type: 'regex',
        confidence: 0.90
      });
    }
    
    // Pattern: "best X for Y"
    if (/best .+ for .+/i.test(query)) {
      patterns.push({
        text: 'best .* for .*',
        type: 'regex',
        confidence: 0.85
      });
    }
    
    return patterns;
  }
  
  /**
   * Record a learned pattern in the database
   */
  async recordPattern(pattern, intent, queryAttemptId, exampleQuery) {
    if (!this.db) return;
    
    try {
      // Check if pattern already exists
      const existing = await this.db.query(`
        SELECT id, occurrence_count, success_count, example_queries
        FROM learned_patterns
        WHERE pattern_text = $1 AND intent = $2 AND pattern_type = $3
      `, [pattern.text, intent, pattern.type]);
      
      if (existing.rows.length > 0) {
        // Update existing pattern
        const row = existing.rows[0];
        const newExamples = [...new Set([...row.example_queries, exampleQuery])].slice(0, 10);
        
        await this.db.query(`
          UPDATE learned_patterns
          SET 
            occurrence_count = occurrence_count + 1,
            success_count = success_count + 1,
            learned_from_query_ids = array_append(learned_from_query_ids, $1),
            example_queries = $2,
            updated_at = NOW()
          WHERE id = $3
        `, [queryAttemptId, newExamples, row.id]);
        
        console.log(`  ↻ Updated pattern: "${pattern.text}" (${pattern.type}) - ${row.occurrence_count + 1} occurrences`);
      } else {
        // Create new pattern
        await this.db.query(`
          INSERT INTO learned_patterns (
            pattern_text, pattern_type, intent, confidence,
            learned_from_query_ids, example_queries
          ) VALUES ($1, $2, $3, $4, $5, $6)
        `, [
          pattern.text,
          pattern.type,
          intent,
          pattern.confidence,
          [queryAttemptId],
          [exampleQuery]
        ]);
        
        console.log(`  + New pattern: "${pattern.text}" (${pattern.type}) → ${intent}`);
      }
    } catch (error) {
      // Ignore duplicate key errors (race condition)
      if (!error.message.includes('duplicate key')) {
        console.error('Error recording pattern:', error);
      }
    }
  }
  
  /**
   * Record pattern match result for performance tracking
   */
  async recordPatternMatch(patternId, wasCorrect, confidence) {
    if (!this.db) return;
    
    try {
      // Update pattern success/failure counts
      if (wasCorrect) {
        await this.db.query(`
          UPDATE learned_patterns
          SET success_count = success_count + 1
          WHERE id = $1
        `, [patternId]);
      } else {
        await this.db.query(`
          UPDATE learned_patterns
          SET failure_count = failure_count + 1
          WHERE id = $1
        `, [patternId]);
      }
      
      // Update daily performance metrics
      await this.db.query(`
        INSERT INTO pattern_performance (
          pattern_id, times_matched, times_correct, times_incorrect, avg_confidence
        ) VALUES ($1, 1, $2, $3, $4)
        ON CONFLICT (pattern_id, date) DO UPDATE SET
          times_matched = pattern_performance.times_matched + 1,
          times_correct = pattern_performance.times_correct + $2,
          times_incorrect = pattern_performance.times_incorrect + $3,
          avg_confidence = (pattern_performance.avg_confidence * pattern_performance.times_matched + $4) / (pattern_performance.times_matched + 1)
      `, [
        patternId,
        wasCorrect ? 1 : 0,
        wasCorrect ? 0 : 1,
        confidence
      ]);
    } catch (error) {
      console.error('Error recording pattern match:', error);
    }
  }
  
  /**
   * Deactivate poorly performing patterns
   */
  async deactivatePoorPatterns() {
    if (!this.db) return;
    
    try {
      const result = await this.db.query(`
        UPDATE learned_patterns
        SET is_active = false
        WHERE 
          is_active = true
          AND occurrence_count >= $1
          AND success_rate < $2
          AND is_verified = false
        RETURNING id, pattern_text, success_rate
      `, [this.minOccurrencesForActivation, this.minSuccessRate]);
      
      if (result.rows.length > 0) {
        console.log(`Deactivated ${result.rows.length} poor-performing patterns:`);
        for (const row of result.rows) {
          console.log(`  - "${row.pattern_text}" (${row.success_rate}% success rate)`);
        }
      }
    } catch (error) {
      console.error('Error deactivating poor patterns:', error);
    }
  }
  
  /**
   * Get learning statistics
   */
  async getStatistics() {
    if (!this.db) return null;
    
    try {
      const result = await this.db.query(`
        SELECT 
          COUNT(*) as total_patterns,
          COUNT(CASE WHEN is_active THEN 1 END) as active_patterns,
          COUNT(CASE WHEN is_verified THEN 1 END) as verified_patterns,
          AVG(success_rate) as avg_success_rate,
          SUM(occurrence_count) as total_occurrences
        FROM learned_patterns
      `);
      
      return result.rows[0];
    } catch (error) {
      console.error('Error getting statistics:', error);
      return null;
    }
  }
  
  /**
   * Get top performing patterns
   */
  async getTopPatterns(limit = 20) {
    if (!this.db) return [];
    
    try {
      const result = await this.db.query(`
        SELECT 
          pattern_text,
          pattern_type,
          intent,
          occurrence_count,
          success_rate,
          is_verified,
          example_queries
        FROM learned_patterns
        WHERE is_active = true
        ORDER BY success_rate DESC, occurrence_count DESC
        LIMIT $1
      `, [limit]);
      
      return result.rows;
    } catch (error) {
      console.error('Error getting top patterns:', error);
      return [];
    }
  }
  
  /**
   * Verify a pattern (mark as manually reviewed and approved)
   */
  async verifyPattern(patternId, verifiedBy = 'admin') {
    if (!this.db) return;
    
    try {
      await this.db.query(`
        UPDATE learned_patterns
        SET 
          is_verified = true,
          verified_by = $1,
          verified_at = NOW(),
          is_active = true
        WHERE id = $2
      `, [verifiedBy, patternId]);
      
      console.log(`✓ Pattern ${patternId} verified by ${verifiedBy}`);
    } catch (error) {
      console.error('Error verifying pattern:', error);
    }
  }
}
