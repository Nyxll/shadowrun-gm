/**
 * LLM Classifier
 * 
 * Uses an LLM to classify queries when all other methods fail.
 * This is the final fallback in the 4-stage pipeline.
 * 
 * Stage 4 of 4-stage intent classification pipeline.
 */

export class LLMClassifier {
  constructor(llmProvider = null) {
    this.llmProvider = llmProvider;
    this.stats = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0
    };
  }

  /**
   * Set the LLM provider function
   * Provider should be async function that takes (prompt) and returns response text
   */
  setProvider(provider) {
    this.llmProvider = provider;
  }

  /**
   * Create the classification prompt
   */
  createPrompt(query, context = {}) {
    return `You are an intent classifier for a Shadowrun 2nd Edition tabletop RPG assistant.

Classify the following user query into ONE of these intents:

INTENTS:
1. GEAR_LOOKUP - User wants to see stats/info about specific gear (weapons, armor, cyberware, etc.)
   Examples: "show me the Ares Predator", "what is a smartgun", "stats for heavy pistols"

2. GEAR_COMPARISON - User wants to compare multiple items or find the best item
   Examples: "compare sniper rifles", "what's better for damage", "rank assault rifles by cost"

3. SPELL_LOOKUP - User wants info about a specific spell
   Examples: "show me fireball", "what does invisibility do", "stats for heal spell"

4. POWER_LOOKUP - User wants info about adept or critter powers
   Examples: "what is killing hands", "show me adept powers", "what does improved reflexes do"

5. TOTEM_LOOKUP - User wants info about shamanic totems
   Examples: "what is bear totem", "show me totems", "what does wolf totem do"

6. RULES_QUESTION - User asking about game mechanics/rules
   Examples: "how does initiative work", "explain spell casting", "what are the rules for hacking"

7. ROLEPLAY_ACTION - User is describing character action in game (narrative)
   Examples: "Platinum draws his gun", "I pull out my commlink", "my character casts a spell"

8. COMBAT_ACTION - User performing combat action (requires dice rolls)
   Examples: "I shoot at the guard", "roll for initiative", "attack with my katana"

9. LORE_QUESTION - User asking about game world/lore
   Examples: "who runs Aztechnology", "what is the Sixth World", "tell me about the Crash"

10. MIXED_QUERY - Query involves multiple intents or is unclear
    Examples: "show me the best combat spells and how to cast them"

QUERY: "${query}"

${context.previousIntent ? `PREVIOUS INTENT: ${context.previousIntent}` : ''}
${context.sessionContext ? `SESSION CONTEXT: ${JSON.stringify(context.sessionContext)}` : ''}

Respond with ONLY the intent name and confidence (0.0-1.0) separated by a pipe:
FORMAT: INTENT_NAME|confidence

Example responses:
GEAR_LOOKUP|0.95
RULES_QUESTION|0.85
MIXED_QUERY|0.70`;
  }

  /**
   * Parse LLM response
   */
  parseResponse(response) {
    const trimmed = response.trim();
    const parts = trimmed.split('|');
    
    if (parts.length !== 2) {
      throw new Error(`Invalid LLM response format: ${response}`);
    }

    const intent = parts[0].trim();
    const confidence = parseFloat(parts[1].trim());

    if (isNaN(confidence) || confidence < 0 || confidence > 1) {
      throw new Error(`Invalid confidence value: ${parts[1]}`);
    }

    const validIntents = [
      'GEAR_LOOKUP',
      'GEAR_COMPARISON',
      'SPELL_LOOKUP',
      'POWER_LOOKUP',
      'TOTEM_LOOKUP',
      'RULES_QUESTION',
      'ROLEPLAY_ACTION',
      'COMBAT_ACTION',
      'LORE_QUESTION',
      'MIXED_QUERY'
    ];

    if (!validIntents.includes(intent)) {
      throw new Error(`Invalid intent: ${intent}`);
    }

    return { intent, confidence };
  }

  /**
   * Classify a query using LLM
   */
  async classify(query, context = {}) {
    if (!this.llmProvider) {
      throw new Error('LLM provider not configured. Call setProvider() first.');
    }

    const startTime = Date.now();
    this.stats.totalCalls++;

    try {
      const prompt = this.createPrompt(query, context);
      const response = await this.llmProvider(prompt);
      const { intent, confidence } = this.parseResponse(response);

      const responseTime = Date.now() - startTime;
      
      // Update average response time
      this.stats.averageResponseTime = 
        (this.stats.averageResponseTime * (this.stats.successfulCalls) + responseTime) / 
        (this.stats.successfulCalls + 1);
      
      this.stats.successfulCalls++;

      return {
        intent,
        confidence,
        method: 'llm',
        responseTime,
        rawResponse: response
      };
    } catch (error) {
      this.stats.failedCalls++;
      throw new Error(`LLM classification failed: ${error.message}`);
    }
  }

  /**
   * Get classifier statistics
   */
  getStats() {
    return {
      ...this.stats,
      successRate: this.stats.totalCalls > 0 
        ? (this.stats.successfulCalls / this.stats.totalCalls * 100).toFixed(1) + '%'
        : 'N/A',
      hasProvider: this.llmProvider !== null
    };
  }

  /**
   * Reset statistics
   */
  resetStats() {
    this.stats = {
      totalCalls: 0,
      successfulCalls: 0,
      failedCalls: 0,
      averageResponseTime: 0
    };
  }
}

/**
 * Mock LLM provider for testing
 * Returns deterministic responses based on simple pattern matching
 */
export class MockLLMProvider {
  async call(prompt) {
    // Extract query from prompt
    const queryMatch = prompt.match(/QUERY: "(.+?)"/);
    if (!queryMatch) {
      return 'MIXED_QUERY|0.5';
    }

    const query = queryMatch[1].toLowerCase();

    // Simple pattern matching for testing
    if (query.includes('show') || query.includes('stats') || query.includes('what is')) {
      if (query.includes('spell')) return 'SPELL_LOOKUP|0.9';
      if (query.includes('power')) return 'POWER_LOOKUP|0.9';
      if (query.includes('totem')) return 'TOTEM_LOOKUP|0.9';
      return 'GEAR_LOOKUP|0.9';
    }

    if (query.includes('compare') || query.includes('better') || query.includes('best')) {
      return 'GEAR_COMPARISON|0.9';
    }

    if (query.includes('how') || query.includes('explain') || query.includes('rules')) {
      return 'RULES_QUESTION|0.9';
    }

    if (query.includes('draws') || query.includes('pulls') || query.includes('my character')) {
      return 'ROLEPLAY_ACTION|0.85';
    }

    if (query.includes('shoot') || query.includes('attack') || query.includes('roll')) {
      return 'COMBAT_ACTION|0.85';
    }

    if (query.includes('who') || query.includes('what happened') || query.includes('tell me about')) {
      return 'LORE_QUESTION|0.8';
    }

    return 'MIXED_QUERY|0.6';
  }
}
