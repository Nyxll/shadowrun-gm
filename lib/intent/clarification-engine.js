/**
 * Clarification Engine
 * Generates user-friendly clarification requests when intent classification is uncertain
 */

export class ClarificationEngine {
  constructor(database) {
    this.db = database;
    
    // Intent metadata for user-friendly display
    this.intentMetadata = {
      'SPELL_LOOKUP': {
        label: '🔮 Spell Information',
        description: 'Get details about a specific spell',
        example: 'e.g., "What is the Fireball spell?"',
        keywords: ['spell', 'magic', 'cast', 'mana']
      },
      'POWER_LOOKUP': {
        label: '⚡ Adept/Critter Powers',
        description: 'Learn about adept powers or critter abilities',
        example: 'e.g., "Tell me about Improved Reflexes"',
        keywords: ['power', 'adept', 'critter', 'ability']
      },
      'TOTEM_LOOKUP': {
        label: '🦅 Totem Spirits',
        description: 'Information about shamanic totems',
        example: 'e.g., "What are Bear totem advantages?"',
        keywords: ['totem', 'spirit', 'shaman', 'mentor']
      },
      'GEAR_LOOKUP': {
        label: '⚔️ Gear & Equipment',
        description: 'Stats and details for weapons, armor, cyberware',
        example: 'e.g., "Show me Ares Predator stats"',
        keywords: ['weapon', 'armor', 'cyberware', 'gear', 'equipment']
      },
      'GEAR_COMPARISON': {
        label: '📊 Compare Items',
        description: 'Compare and rank multiple items',
        example: 'e.g., "What\'s the best heavy pistol?"',
        keywords: ['compare', 'best', 'better', 'rank', 'top']
      },
      'RULES_QUESTION': {
        label: '📖 Game Rules & Mechanics',
        description: 'Understand game mechanics and rules',
        example: 'e.g., "How does initiative work?"',
        keywords: ['how', 'rules', 'mechanics', 'work', 'calculate']
      },
      'LIST_QUERY': {
        label: '📋 List All Items',
        description: 'See all items in a category',
        example: 'e.g., "List all combat spells"',
        keywords: ['list', 'all', 'show', 'available']
      }
    };
    
    // Stop words to ignore when analyzing queries
    this.stopWords = new Set([
      'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
      'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
      'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that',
      'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
    ]);
  }
  
  /**
   * Generate clarification request for ambiguous query
   */
  async generateClarification(query, bestGuess, alternatives = [], context = null) {
    const ambiguityType = this.detectAmbiguityType(query, bestGuess, alternatives);
    
    switch (ambiguityType) {
      case 'ENTITY_AMBIGUOUS':
        return this.generateEntityDisambiguation(query, bestGuess, alternatives);
      
      case 'INTENT_AMBIGUOUS':
        return this.generateIntentClarification(query, bestGuess, alternatives);
      
      case 'CONTEXT_NEEDED':
        return this.generateContextRequest(query, bestGuess);
      
      case 'TOO_VAGUE':
        return this.generateRephraseRequest(query, bestGuess);
      
      default:
        return this.generateGenericClarification(query, bestGuess, alternatives);
    }
  }
  
  /**
   * Detect what type of ambiguity we're dealing with
   */
  detectAmbiguityType(query, bestGuess, alternatives) {
    const words = query.toLowerCase().split(/\s+/);
    const significantWords = words.filter(w => !this.stopWords.has(w) && w.length > 2);
    
    // Single word queries are often entity ambiguous
    if (significantWords.length === 1) {
      return 'ENTITY_AMBIGUOUS';
    }
    
    // Very short queries need more context
    if (significantWords.length <= 2) {
      return 'TOO_VAGUE';
    }
    
    // Multiple high-confidence alternatives suggest intent ambiguity
    if (alternatives.length >= 2 && alternatives[0].confidence > 0.60) {
      return 'INTENT_AMBIGUOUS';
    }
    
    // Low confidence overall suggests need for context
    if (bestGuess.confidence < 0.60) {
      return 'CONTEXT_NEEDED';
    }
    
    return 'GENERIC';
  }
  
  /**
   * Generate multiple choice clarification for intent ambiguity
   */
  generateIntentClarification(query, bestGuess, alternatives) {
    // Combine best guess with alternatives, limit to top 4
    const allOptions = [bestGuess, ...alternatives]
      .filter(opt => opt && opt.intent)
      .slice(0, 4);
    
    const options = allOptions.map((opt, idx) => {
      const metadata = this.intentMetadata[opt.intent] || {};
      return {
        id: idx + 1,
        intent: opt.intent,
        label: metadata.label || opt.intent,
        description: metadata.description || '',
        example: metadata.example || '',
        confidence: opt.confidence
      };
    });
    
    return {
      type: 'multiple_choice',
      message: `I'm not completely sure what you're asking about. Please choose the option that best matches your question:`,
      query: query,
      options: options,
      allow_rephrase: true,
      rephrase_prompt: "Or, rephrase your question to be more specific"
    };
  }
  
  /**
   * Generate disambiguation for entity ambiguity (e.g., "Bear" could be totem or animal)
   */
  generateEntityDisambiguation(query, bestGuess, alternatives) {
    const entity = query.trim();
    const allOptions = [bestGuess, ...alternatives].filter(opt => opt && opt.intent).slice(0, 3);
    
    const options = allOptions.map((opt, idx) => {
      const metadata = this.intentMetadata[opt.intent] || {};
      return {
        id: idx + 1,
        intent: opt.intent,
        label: metadata.label || opt.intent,
        description: `"${entity}" as ${metadata.description || opt.intent}`,
        example: metadata.example || '',
        confidence: opt.confidence
      };
    });
    
    return {
      type: 'disambiguation',
      message: `"${entity}" could mean different things. Which did you mean?`,
      query: query,
      entity: entity,
      options: options,
      allow_custom: true,
      custom_prompt: "Or describe what you're looking for"
    };
  }
  
  /**
   * Generate context request for queries that need more information
   */
  generateContextRequest(query, bestGuess) {
    const metadata = this.intentMetadata[bestGuess.intent] || {};
    
    return {
      type: 'context_request',
      message: `I think you're asking about ${metadata.label || bestGuess.intent}, but I need more information.`,
      query: query,
      best_guess: {
        intent: bestGuess.intent,
        label: metadata.label,
        confidence: bestGuess.confidence
      },
      suggestions: [
        `Try being more specific about what you want to know`,
        `Include the name of the item or concept you're asking about`,
        metadata.example || `Example: ${this.getExampleForIntent(bestGuess.intent)}`
      ],
      allow_rephrase: true
    };
  }
  
  /**
   * Generate rephrase request for very vague queries
   */
  generateRephraseRequest(query, bestGuess) {
    const examplesByIntent = this.getExamplesForAllIntents();
    
    return {
      type: 'rephrase_request',
      message: `Your query "${query}" is too vague for me to understand. Could you rephrase it?`,
      query: query,
      suggestions: [
        "Be more specific about what you're looking for",
        "Include the name of what you're asking about",
        "Specify if you want rules, stats, or a list"
      ],
      examples: examplesByIntent,
      allow_custom: true
    };
  }
  
  /**
   * Generate generic clarification as fallback
   */
  generateGenericClarification(query, bestGuess, alternatives) {
    const allOptions = [bestGuess, ...alternatives].filter(opt => opt && opt.intent).slice(0, 3);
    
    if (allOptions.length === 0) {
      return this.generateRephraseRequest(query, { intent: 'UNKNOWN', confidence: 0 });
    }
    
    return this.generateIntentClarification(query, bestGuess, alternatives);
  }
  
  /**
   * Get example query for a specific intent
   */
  getExampleForIntent(intent) {
    const metadata = this.intentMetadata[intent];
    return metadata?.example || 'No example available';
  }
  
  /**
   * Get examples for all intents
   */
  getExamplesForAllIntents() {
    return Object.entries(this.intentMetadata).map(([intent, meta]) => ({
      intent: intent,
      label: meta.label,
      example: meta.example
    }));
  }
  
  /**
   * Extract significant keywords from query
   */
  extractKeywords(query) {
    return query.toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 3 && !this.stopWords.has(word));
  }
  
  /**
   * Calculate similarity between query and intent keywords
   */
  calculateIntentSimilarity(query, intent) {
    const queryKeywords = new Set(this.extractKeywords(query));
    const intentKeywords = new Set(this.intentMetadata[intent]?.keywords || []);
    
    if (queryKeywords.size === 0 || intentKeywords.size === 0) {
      return 0;
    }
    
    const intersection = new Set([...queryKeywords].filter(k => intentKeywords.has(k)));
    return intersection.size / Math.max(queryKeywords.size, intentKeywords.size);
  }
  
  /**
   * Log clarification interaction to database
   */
  async logClarification(queryAttemptId, clarification) {
    if (!this.db) return;
    
    try {
      await this.db.query(`
        INSERT INTO clarification_interactions (
          query_attempt_id,
          clarification_type,
          options_presented
        ) VALUES ($1, $2, $3)
        RETURNING id
      `, [
        queryAttemptId,
        clarification.type,
        JSON.stringify(clarification.options || [])
      ]);
    } catch (error) {
      console.error('Error logging clarification:', error);
    }
  }
  
  /**
   * Record user's clarification response
   */
  async recordClarificationResponse(clarificationId, userSelection, resolvedIntent, wasHelpful = true) {
    if (!this.db) return;
    
    try {
      await this.db.query(`
        UPDATE clarification_interactions
        SET 
          user_selection = $1,
          resolved_intent = $2,
          was_helpful = $3,
          resolution_time_ms = EXTRACT(EPOCH FROM (NOW() - timestamp)) * 1000
        WHERE id = $4
      `, [userSelection, resolvedIntent, wasHelpful, clarificationId]);
    } catch (error) {
      console.error('Error recording clarification response:', error);
    }
  }
  
  /**
   * Check if a classification needs clarification
   */
  needsClarification(classification) {
    // Need clarification if:
    // 1. Confidence is low (< 0.6)
    // 2. Multiple tables suggested (ambiguous)
    // 3. No clear intent
    
    if (!classification) return true;
    
    if (classification.confidence && classification.confidence < 0.6) {
      return true;
    }
    
    if (classification.tables && classification.tables.length > 1) {
      return true;
    }
    
    if (!classification.intent || classification.intent === 'unknown') {
      return true;
    }
    
    return false;
  }
  
  /**
   * Generate clarification options for ambiguous classification
   */
  async generateOptions(query, classification) {
    const options = [];
    
    // If multiple tables, create option for each
    if (classification.tables && classification.tables.length > 1) {
      for (const table of classification.tables) {
        const label = this.getTableLabel(table);
        options.push({
          label: label,
          classification: {
            ...classification,
            tables: [table],
            confidence: 0.8
          }
        });
      }
    }
    
    // If low confidence, suggest common intents
    if (classification.confidence < 0.6) {
      const commonIntents = ['lookup', 'list', 'rules', 'compare'];
      for (const intent of commonIntents) {
        if (intent !== classification.intent) {
          options.push({
            label: this.getIntentLabel(intent),
            classification: {
              ...classification,
              intent: intent,
              confidence: 0.7
            }
          });
        }
      }
    }
    
    return options.slice(0, 4); // Limit to 4 options
  }
  
  /**
   * Record a clarification interaction
   */
  async recordClarification(originalQuery, originalClassification, options, selectedOption) {
    if (!this.db) return null;
    
    try {
      // First, create a query_attempt record
      const attemptResult = await this.db.query(`
        INSERT INTO query_attempts (
          query_text,
          intent_detected,
          confidence,
          classification_method,
          needed_clarification,
          clarification_shown
        ) VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
      `, [
        originalQuery,
        originalClassification.intent,
        originalClassification.confidence || 0,
        'clarified',
        true,
        JSON.stringify(options)
      ]);
      
      const queryAttemptId = attemptResult.rows[0].id;
      
      // Then create clarification_interaction record
      const clarificationResult = await this.db.query(`
        INSERT INTO clarification_interactions (
          query_attempt_id,
          clarification_type,
          options_presented,
          resolved_intent,
          was_helpful
        ) VALUES ($1, $2, $3, $4, $5)
        RETURNING id
      `, [
        queryAttemptId,
        'multiple_choice',
        JSON.stringify(options),
        selectedOption.classification.intent,
        true
      ]);
      
      return clarificationResult.rows[0].id;
    } catch (error) {
      console.error('Error recording clarification:', error);
      return null;
    }
  }
  
  /**
   * Get user-friendly label for a table
   */
  getTableLabel(table) {
    const labels = {
      'spells': '🔮 Spell (magic)',
      'powers': '⚡ Adept/Critter Power',
      'totems': '🦅 Totem Spirit',
      'gear': '⚔️ Gear/Equipment'
    };
    return labels[table] || table;
  }
  
  /**
   * Get user-friendly label for an intent
   */
  getIntentLabel(intent) {
    const labels = {
      'lookup': '📖 Look up specific item',
      'list': '📋 List all items',
      'compare': '📊 Compare items',
      'rules': '📚 Game rules/mechanics'
    };
    return labels[intent] || intent;
  }
}
