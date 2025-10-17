/**
 * Learned Pattern Matcher
 * Applies patterns learned from user feedback to classify queries
 */

export class LearnedPatternMatcher {
  constructor(database) {
    this.db = database;
    this.patternsCache = null;
    this.cacheTimestamp = null;
    this.cacheLifetime = 5 * 60 * 1000; // 5 minutes
  }
  
  /**
   * Match query against learned patterns
   */
  async match(query) {
    if (!this.db) {
      return null;
    }
    
    const normalized = query.toLowerCase().trim();
    
    // Load patterns (with caching)
    const patterns = await this.getPatterns();
    
    if (!patterns || patterns.length === 0) {
      return null;
    }
    
    // Try to match patterns in order of priority
    const matches = [];
    
    // 1. Try regex patterns first (highest confidence)
    for (const pattern of patterns.filter(p => p.pattern_type === 'regex')) {
      const match = this.matchRegexPattern(normalized, pattern);
      if (match) {
        matches.push(match);
      }
    }
    
    // 2. Try phrase patterns (medium-high confidence)
    for (const pattern of patterns.filter(p => p.pattern_type === 'phrase')) {
      const match = this.matchPhrasePattern(normalized, pattern);
      if (match) {
        matches.push(match);
      }
    }
    
    // 3. Try keyword patterns (medium confidence)
    for (const pattern of patterns.filter(p => p.pattern_type === 'keyword')) {
      const match = this.matchKeywordPattern(normalized, pattern);
      if (match) {
        matches.push(match);
      }
    }
    
    // 4. Try entity patterns (context-dependent)
    for (const pattern of patterns.filter(p => p.pattern_type === 'entity')) {
      const match = this.matchEntityPattern(normalized, pattern);
      if (match) {
        matches.push(match);
      }
    }
    
    if (matches.length === 0) {
      return null;
    }
    
    // Return best match (highest confidence)
    const bestMatch = matches.reduce((best, current) => 
      current.confidence > best.confidence ? current : best
    );
    
    // Record the match for performance tracking
    if (bestMatch.patternId) {
      this.recordMatch(bestMatch.patternId, bestMatch.confidence);
    }
    
    return bestMatch;
  }
  
  /**
   * Match regex pattern
   */
  matchRegexPattern(query, pattern) {
    try {
      const regex = new RegExp(pattern.pattern_text, 'i');
      if (regex.test(query)) {
        return {
          intent: pattern.intent,
          confidence: this.calculateConfidence(pattern),
          method: 'learned_regex',
          pattern: pattern.pattern_text,
          patternId: pattern.id
        };
      }
    } catch (error) {
      console.error(`Invalid regex pattern: ${pattern.pattern_text}`, error);
    }
    return null;
  }
  
  /**
   * Match phrase pattern (exact substring match)
   */
  matchPhrasePattern(query, pattern) {
    if (query.includes(pattern.pattern_text.toLowerCase())) {
      return {
        intent: pattern.intent,
        confidence: this.calculateConfidence(pattern),
        method: 'learned_phrase',
        pattern: pattern.pattern_text,
        patternId: pattern.id
      };
    }
    return null;
  }
  
  /**
   * Match keyword pattern
   */
  matchKeywordPattern(query, pattern) {
    const words = query.split(/\s+/);
    const keyword = pattern.pattern_text.toLowerCase();
    
    if (words.includes(keyword)) {
      return {
        intent: pattern.intent,
        confidence: this.calculateConfidence(pattern) * 0.9, // Slightly lower for keywords
        method: 'learned_keyword',
        pattern: pattern.pattern_text,
        patternId: pattern.id
      };
    }
    return null;
  }
  
  /**
   * Match entity pattern (single-word queries)
   */
  matchEntityPattern(query, pattern) {
    const words = query.split(/\s+/).filter(w => w.length > 0);
    
    // Entity patterns work best for single-word or very short queries
    if (words.length <= 2 && query.includes(pattern.pattern_text.toLowerCase())) {
      return {
        intent: pattern.intent,
        confidence: this.calculateConfidence(pattern),
        method: 'learned_entity',
        pattern: pattern.pattern_text,
        patternId: pattern.id
      };
    }
    return null;
  }
  
  /**
   * Calculate confidence for a pattern based on its performance
   */
  calculateConfidence(pattern) {
    let confidence = parseFloat(pattern.confidence) || 0.75;
    
    // Adjust based on success rate
    if (pattern.success_rate !== null) {
      const successFactor = pattern.success_rate / 100;
      confidence = confidence * successFactor;
    }
    
    // Boost confidence for verified patterns
    if (pattern.is_verified) {
      confidence = Math.min(confidence * 1.1, 0.95);
    }
    
    // Boost confidence for patterns with many occurrences
    if (pattern.occurrence_count > 10) {
      confidence = Math.min(confidence * 1.05, 0.95);
    }
    
    return Math.round(confidence * 100) / 100; // Round to 2 decimals
  }
  
  /**
   * Get patterns from database (with caching)
   */
  async getPatterns() {
    const now = Date.now();
    
    // Return cached patterns if still valid
    if (this.patternsCache && this.cacheTimestamp && (now - this.cacheTimestamp) < this.cacheLifetime) {
      return this.patternsCache;
    }
    
    try {
      const result = await this.db.query(`
        SELECT 
          id,
          pattern_text,
          pattern_type,
          intent,
          confidence,
          occurrence_count,
          success_rate,
          is_verified
        FROM learned_patterns
        WHERE is_active = true
        ORDER BY 
          is_verified DESC,
          success_rate DESC NULLS LAST,
          occurrence_count DESC
      `);
      
      this.patternsCache = result.rows;
      this.cacheTimestamp = now;
      
      return this.patternsCache;
    } catch (error) {
      console.error('Error loading learned patterns:', error);
      return [];
    }
  }
  
  /**
   * Invalidate pattern cache (call after learning new patterns)
   */
  invalidateCache() {
    this.patternsCache = null;
    this.cacheTimestamp = null;
  }
  
  /**
   * Record pattern match (async, fire-and-forget)
   */
  recordMatch(patternId, confidence) {
    // Don't await - just fire and forget
    if (this.db) {
      this.db.query(`
        INSERT INTO pattern_performance (
          pattern_id, times_matched, avg_confidence
        ) VALUES ($1, 1, $2)
        ON CONFLICT (pattern_id, date) DO UPDATE SET
          times_matched = pattern_performance.times_matched + 1,
          avg_confidence = (pattern_performance.avg_confidence * pattern_performance.times_matched + $2) / (pattern_performance.times_matched + 1)
      `, [patternId, confidence]).catch(err => {
        console.error('Error recording pattern match:', err);
      });
    }
  }
  
  /**
   * Get statistics about learned patterns
   */
  async getStats() {
    if (!this.db) return null;
    
    try {
      const result = await this.db.query(`
        SELECT 
          COUNT(*) as total_patterns,
          COUNT(CASE WHEN is_active THEN 1 END) as active_patterns,
          COUNT(CASE WHEN is_verified THEN 1 END) as verified_patterns,
          COUNT(CASE WHEN pattern_type = 'regex' THEN 1 END) as regex_patterns,
          COUNT(CASE WHEN pattern_type = 'phrase' THEN 1 END) as phrase_patterns,
          COUNT(CASE WHEN pattern_type = 'keyword' THEN 1 END) as keyword_patterns,
          COUNT(CASE WHEN pattern_type = 'entity' THEN 1 END) as entity_patterns,
          AVG(CASE WHEN is_active THEN success_rate END) as avg_success_rate,
          SUM(CASE WHEN is_active THEN occurrence_count ELSE 0 END) as total_occurrences
        FROM learned_patterns
      `);
      
      return result.rows[0];
    } catch (error) {
      console.error('Error getting pattern stats:', error);
      return null;
    }
  }
}
