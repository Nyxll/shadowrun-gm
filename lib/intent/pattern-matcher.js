/**
 * Pattern Matcher - Stage 1 of Intent Classification
 * Uses regex patterns to quickly identify common query types
 * Fast (~100ms), free, ~60% coverage
 */

class PatternMatcher {
  constructor() {
    this.patterns = {
      // SPELL_LOOKUP - Specific spell queries
      SPELL_LOOKUP: [
        // Specific spell names
        /\b(fireball|manaball|stunball|powerball|lightning bolt|heal|armor|invisibility|levitate|confusion|chaos|control thoughts|mind probe|detect enemies|clairvoyance|clairaudience)\b/i,
        // "list all X spells", "show me combat spells"
        /^list\s+(all\s+)?(combat|detection|health|illusion|manipulation)\s+spells?/i,
        /^show\s+me\s+(all\s+)?(combat|detection|health|illusion|manipulation)\s+spells?/i,
        // "what spells", "spell stats"
        /\b(spell|magic|mana)\b.*\b(stats?|info|details?|list)\b/i,
        /^list\s+(all\s+)?spells?/i,
      ],
      
      // POWER_LOOKUP - Adept/critter power queries
      POWER_LOOKUP: [
        // Specific power names
        /\b(improved reflexes|killing hands|mystic armor|pain resistance|enhanced perception|combat sense|distance strike)\b/i,
        // "list adept powers", "show me powers"
        /^list\s+(all\s+)?(adept|critter)\s+powers?/i,
        /^show\s+me\s+(all\s+)?(adept|critter)\s+powers?/i,
        /\b(adept|critter)\s+powers?\b/i,
        /^list\s+(all\s+)?powers?/i,
      ],
      
      // TOTEM_LOOKUP - Totem/shamanic queries
      TOTEM_LOOKUP: [
        // Specific totem names
        /\b(bear|wolf|eagle|raven|snake|cat|dog|lion|shark|whale|dolphin|owl|coyote|rat|gator)\s+totem\b/i,
        // "list totems", "show me shamanic totems"
        /^list\s+(all\s+)?totems?/i,
        /^show\s+me\s+(all\s+)?totems?/i,
        /\bshamanic?\b.*\btotems?\b/i,
        /\btotems?\b.*\b(advantages?|disadvantages?)\b/i,
      ],
      
      // GEAR_LOOKUP - Specific item lookup
      GEAR_LOOKUP: [
        // "show me X", "what is X", "stats for X"
        /^(?:show|display|get|find)\s+(?:me\s+)?(?:the\s+)?([A-Z][a-zA-Z\s\-]+)/i,
        /^what\s+(?:is|are)\s+(?:the\s+)?([A-Z][a-zA-Z\s\-]+)\??$/i,
        /\b(stats?|info|details?)\b\s+(?:for|on|about)\s+([A-Z][a-zA-Z\s\-]+)/i,
        /^look\s*up\s+([A-Z][a-zA-Z\s\-]+)/i,
        // Specific weapon types
        /\b(ares predator|colt manhunter|beretta|ruger|uzi|ak-97|hk227|remington|panther cannon|vindicator)\b/i,
      ],
      
      // GEAR_COMPARISON - Compare/rank items
      GEAR_COMPARISON: [
        // "compare X and Y", "X vs Y"
        /\bcompare\b.*?\b(and|vs|versus)\b/i,
        // "best X", "top X", "rank X by Y"
        /\b(better|best|top)\b.*?\b(pistol|rifle|shotgun|smg|armor|cyberware)\b/i,
        /^rank\s+(.+?)\s+by\s+(damage|cost|conceal|ammo|essence)/i,
        // "what's the best"
        /^what'?s\s+the\s+(best|better|top)/i,
      ],
      
      // RULES_QUESTION - Game mechanics
      RULES_QUESTION: [
        // "how does X work", "explain X"
        /^how\s+(?:does|do|did)\s+(.+?)\s+work\??$/i,
        /^explain\s+(.+)/i,
        // "what are the rules for X"
        /^what\s+(?:are|is)\s+the\s+rules?\s+(?:for|about|on)\s+(.+)/i,
        /\brules?\b.*\b(for|about|on)\b\s+(.+)/i,
        // Specific mechanics
        /\b(initiative|combat|damage|healing|magic|hacking|rigging|astral|physical adept)\b.*\b(work|calculate|determine|resolve)\b/i,
      ],
      
      // LIST_QUERY - List all items of a type
      LIST_QUERY: [
        // "list all X", "show all X"
        /^list\s+(?:all\s+)?(heavy pistols?|light pistols?|smgs?|assault rifles?|sniper rifles?|shotguns?|melee weapons?)/i,
        /^show\s+(?:me\s+)?(?:all\s+)?(heavy pistols?|light pistols?|smgs?|assault rifles?|sniper rifles?|shotguns?)/i,
        // "what X are there"
        /^what\s+(weapons?|armor|cyberware|spells?|powers?|totems?)\s+(?:are\s+)?(?:there|available|exist)/i,
      ],
    };
  }
  
  /**
   * Match query against patterns
   * @param {string} query - User query
   * @returns {Object|null} Match result with intent, confidence, matches
   */
  match(query) {
    if (!query || typeof query !== 'string') {
      return null;
    }
    
    const trimmedQuery = query.trim();
    
    for (const [intent, patterns] of Object.entries(this.patterns)) {
      for (const pattern of patterns) {
        const match = trimmedQuery.match(pattern);
        if (match) {
          return {
            intent,
            confidence: 0.9,
            method: 'pattern',
            matches: match.slice(1).filter(Boolean),
            pattern: pattern.source,
            query: trimmedQuery,
          };
        }
      }
    }
    
    return null;
  }
  
  /**
   * Get statistics about pattern coverage
   * @returns {Object} Pattern statistics
   */
  getStats() {
    const stats = {};
    for (const [intent, patterns] of Object.entries(this.patterns)) {
      stats[intent] = patterns.length;
    }
    return {
      total_intents: Object.keys(this.patterns).length,
      total_patterns: Object.values(this.patterns).reduce((sum, arr) => sum + arr.length, 0),
      by_intent: stats,
    };
  }
}

export { PatternMatcher };
