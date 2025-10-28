/**
 * Embedding Similarity Classifier
 * 
 * Uses sentence transformers to classify queries based on semantic similarity
 * to example queries for each intent.
 * 
 * Stage 3 of 4-stage intent classification pipeline.
 */

import { pipeline } from '@xenova/transformers';

export class EmbeddingSimilarity {
  constructor() {
    this.model = null;
    this.modelName = 'Xenova/all-MiniLM-L6-v2';
    this.intentExamples = {
      GEAR_LOOKUP: [
        "show me the Ares Predator",
        "what is a smartgun",
        "stats for heavy pistols",
        "look up armor jacket",
        "tell me about the Uzi III",
        "what are the specs on a katana",
        "info on cyberware",
        "details about the Ingram Smartgun",
        "what's a dermal plating",
        "show stats for Fichetti Security 500"
      ],
      GEAR_COMPARISON: [
        "compare sniper rifles and heavy pistols",
        "what's better for damage",
        "rank assault rifles by cost",
        "best cyberware for combat",
        "which has more conceal",
        "compare Ares Predator vs Fichetti",
        "what's the best armor",
        "rank weapons by damage",
        "which pistol is cheaper",
        "best gun for stealth"
      ],
      RULES_QUESTION: [
        "how does initiative work",
        "explain spell casting",
        "what are the rules for hacking",
        "how do I calculate damage",
        "what's the combat sequence",
        "explain target numbers",
        "how does essence work",
        "what are the magic rules",
        "explain skill tests",
        "how do opposed tests work"
      ],
      ROLEPLAY_ACTION: [
        "Platinum draws his gun",
        "I pull out my commlink",
        "my character casts a spell",
        "she opens the door",
        "he runs down the alley",
        "I hack into the system",
        "my character attacks",
        "she casts invisibility",
        "I sneak past the guard",
        "he jumps over the fence"
      ],
      COMBAT_ACTION: [
        "I shoot at the guard",
        "roll for initiative",
        "attack with my katana",
        "fire at the drone",
        "I dodge the attack",
        "cast combat spell",
        "throw a grenade",
        "make a called shot",
        "full auto burst",
        "melee attack"
      ],
      SPELL_LOOKUP: [
        "show me fireball",
        "what does invisibility do",
        "stats for heal spell",
        "tell me about manaball",
        "what's the powerball spell",
        "info on detect enemies",
        "show me combat spells",
        "what are healing spells",
        "tell me about illusion magic",
        "what does armor spell do"
      ],
      POWER_LOOKUP: [
        "what is killing hands",
        "show me adept powers",
        "what does improved reflexes do",
        "tell me about mystic armor",
        "what are physical adept powers",
        "info on enhanced strength",
        "what does pain resistance do",
        "show me combat powers",
        "what is astral perception",
        "tell me about critter powers"
      ],
      TOTEM_LOOKUP: [
        "what is bear totem",
        "show me shamanic totems",
        "what does wolf totem do",
        "tell me about eagle",
        "what are the totem bonuses",
        "info on cat totem",
        "what does raven totem give",
        "show me all totems",
        "what is snake totem",
        "tell me about dog totem"
      ],
      LORE_QUESTION: [
        "who runs Aztechnology",
        "what is the Sixth World",
        "tell me about the Crash",
        "what are megacorps",
        "who is Dunkelzahn",
        "what happened in 2029",
        "tell me about the UCAS",
        "what are the Tir nations",
        "who are the Great Dragons",
        "what is the Matrix"
      ]
    };
    this.intentEmbeddings = null;
    this.embeddingCache = new Map();
  }

  /**
   * Initialize the model and pre-compute embeddings
   */
  async initialize() {
    if (this.model) {
      return; // Already initialized
    }

    console.log('Initializing embedding model...');
    
    // Load sentence transformer model
    this.model = await pipeline(
      'feature-extraction',
      this.modelName
    );

    console.log('Pre-computing intent example embeddings...');
    
    // Pre-compute embeddings for all examples
    this.intentEmbeddings = {};
    for (const [intent, examples] of Object.entries(this.intentExamples)) {
      this.intentEmbeddings[intent] = await Promise.all(
        examples.map(ex => this.getEmbedding(ex))
      );
    }

    console.log('Embedding model initialized successfully');
  }

  /**
   * Get embedding for a text string
   */
  async getEmbedding(text) {
    // Check cache first
    if (this.embeddingCache.has(text)) {
      return this.embeddingCache.get(text);
    }

    const output = await this.model(text, {
      pooling: 'mean',
      normalize: true
    });

    const embedding = Array.from(output.data);
    
    // Cache the embedding
    this.embeddingCache.set(text, embedding);
    
    return embedding;
  }

  /**
   * Calculate cosine similarity between two embeddings
   */
  cosineSimilarity(a, b) {
    // Embeddings are already normalized, so dot product = cosine similarity
    const dotProduct = a.reduce((sum, val, i) => sum + val * b[i], 0);
    return dotProduct;
  }

  /**
   * Classify a query based on embedding similarity
   */
  async classify(query) {
    if (!this.model) {
      await this.initialize();
    }

    const queryEmbedding = await this.getEmbedding(query);
    const similarities = {};

    // Calculate similarity to each intent's examples
    for (const [intent, embeddings] of Object.entries(this.intentEmbeddings)) {
      // Find max similarity to any example
      const maxSim = Math.max(
        ...embeddings.map(emb => this.cosineSimilarity(queryEmbedding, emb))
      );
      similarities[intent] = maxSim;
    }

    // Find intent with highest similarity
    const maxIntent = Object.keys(similarities).reduce((a, b) =>
      similarities[a] > similarities[b] ? a : b
    );

    const confidence = similarities[maxIntent];

    // Only return if confidence is high enough
    if (confidence > 0.7) {
      return {
        intent: maxIntent,
        confidence,
        method: 'embedding',
        similarities,
        allScores: similarities
      };
    }

    return null;
  }

  /**
   * Get statistics about the embedding classifier
   */
  getStats() {
    return {
      modelName: this.modelName,
      initialized: this.model !== null,
      intentCount: Object.keys(this.intentExamples).length,
      exampleCount: Object.values(this.intentExamples).reduce((sum, arr) => sum + arr.length, 0),
      cacheSize: this.embeddingCache.size
    };
  }

  /**
   * Clear the embedding cache
   */
  clearCache() {
    this.embeddingCache.clear();
  }
}
