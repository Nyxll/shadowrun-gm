/**
 * Combat Modifier System for Shadowrun 2nd Edition
 * Based on AwakeMUD architecture with SR2-specific adjustments
 */

// Modifier type constants
const COMBAT_MOD = {
  // Ranged Combat
  RECOIL: 0,
  MOVEMENT_ATTACKER: 1,
  DUAL_WIELDING: 2,
  SMARTLINK: 3,
  RANGE: 4,
  VISIBILITY: 5,
  POSITION_TARGET: 6,
  GYRO: 7,
  DEFENDER_MOVING: 8,
  FRIENDS_IN_MELEE: 9,
  CALLED_SHOT: 10,
  WOUNDS: 11,
  
  // Melee Combat
  REACH: 12,
  POSITION_ATTACKER: 13,
  
  // Universal
  SURPRISE: 14,
  SITUATIONAL: 15
};

// Human-readable names for modifiers
const MODIFIER_NAMES = [
  'Recoil',
  'Attacker Movement',
  'Dual Wielding',
  'Smartlink',
  'Range',
  'Visibility',
  'Target Position',
  'Gyro Stabilization',
  'Defender Moving',
  'Friends in Melee',
  'Called Shot',
  'Wounds',
  'Reach',
  'Attacker Position',
  'Surprise',
  'Situational'
];

// SR2-specific constants
const SR2_CONSTANTS = {
  PRONE_SHORT_RANGE: -2,  // SR2 uses -2, SR3 uses -1
  PRONE_LONG_RANGE: 1,
  EX_AMMO_BONUS: 2,       // SR2 uses +2, SR3 uses +1
  UNCONSCIOUS_TARGET: -6,
  SMARTLINK_BONUS: -2,
  DUAL_WIELD_PENALTY: 2,
  CALLED_SHOT_PENALTY: 4,
  FRIENDS_IN_MELEE_PENALTY: 2,
  WALKING_PENALTY: 1,
  RUNNING_PENALTY: 4,
  DEFENDER_RUNNING_PENALTY: 2
};

// Light level modifiers (SR2 4-tier system)
const LIGHT_LEVELS = {
  NORMAL: { modifier: 0, name: 'Normal Light' },
  PARTIAL: { modifier: 1, name: 'Partial Light' },
  DIM: { modifier: 2, name: 'Dim Light' },
  DARK: { modifier: 4, name: 'Total Darkness' }
};

// Range categories
const RANGE_CATEGORIES = {
  SHORT: 'short',
  MEDIUM: 'medium',
  LONG: 'long',
  EXTREME: 'extreme'
};

// Base target numbers by range
const BASE_TN_BY_RANGE = {
  [RANGE_CATEGORIES.SHORT]: 4,
  [RANGE_CATEGORIES.MEDIUM]: 5,
  [RANGE_CATEGORIES.LONG]: 6,
  [RANGE_CATEGORIES.EXTREME]: 9
};

/**
 * Combat Modifier Tracker
 * Manages all combat modifiers using array-based system from AwakeMUD
 */
class CombatModifiers {
  constructor() {
    this.modifiers = new Array(16).fill(0);
    this.explanations = new Array(16).fill(null);
  }

  /**
   * Apply a modifier with optional explanation
   */
  apply(modifierType, value, explanation = null) {
    if (modifierType < 0 || modifierType >= this.modifiers.length) {
      throw new Error(`Invalid modifier type: ${modifierType}`);
    }
    
    this.modifiers[modifierType] = value;
    if (explanation) {
      this.explanations[modifierType] = explanation;
    }
  }

  /**
   * Get total of all modifiers
   */
  getTotal() {
    return this.modifiers.reduce((sum, mod) => sum + mod, 0);
  }

  /**
   * Get breakdown of all non-zero modifiers
   */
  getBreakdown() {
    return this.modifiers
      .map((value, idx) => ({
        type: MODIFIER_NAMES[idx],
        value: value,
        explanation: this.explanations[idx]
      }))
      .filter(m => m.value !== 0);
  }

  /**
   * Get human-readable summary
   */
  getSummary() {
    const breakdown = this.getBreakdown();
    if (breakdown.length === 0) {
      return 'No modifiers';
    }

    return breakdown
      .map(m => {
        const sign = m.value > 0 ? '+' : '';
        const exp = m.explanation ? ` (${m.explanation})` : '';
        return `${m.type}: ${sign}${m.value}${exp}`;
      })
      .join('\n');
  }

  /**
   * Reset all modifiers
   */
  reset() {
    this.modifiers.fill(0);
    this.explanations.fill(null);
  }
}

/**
 * Calculate ranged combat target number
 */
function calculateRangedTN(params) {
  const {
    weapon,
    range,
    attacker = {},
    defender = {},
    situation = {}
  } = params;

  const mods = new CombatModifiers();
  
  // 1. Base TN from range
  const baseTN = BASE_TN_BY_RANGE[range] || 4;
  
  // 2. Dual wielding vs smartlink (mutually exclusive)
  if (situation.dualWielding) {
    mods.apply(
      COMBAT_MOD.DUAL_WIELDING,
      SR2_CONSTANTS.DUAL_WIELD_PENALTY,
      'Using two weapons'
    );
  } else if (weapon.smartlink && attacker.hasSmartlink) {
    mods.apply(
      COMBAT_MOD.SMARTLINK,
      SR2_CONSTANTS.SMARTLINK_BONUS,
      'Smartlink system'
    );
  }
  
  // 3. Recoil
  if (situation.recoil && situation.recoil > 0) {
    const recoilMod = Math.max(0, situation.recoil - (weapon.recoilComp || 0));
    if (recoilMod > 0) {
      mods.apply(
        COMBAT_MOD.RECOIL,
        recoilMod,
        `Uncompensated recoil: ${recoilMod}`
      );
    }
  }
  
  // 4. Gyro stabilization
  if (weapon.gyroStabilization && weapon.gyroStabilization > 0) {
    // Gyro reduces movement and recoil penalties
    const gyroReduction = Math.min(
      weapon.gyroStabilization,
      mods.modifiers[COMBAT_MOD.MOVEMENT_ATTACKER] + mods.modifiers[COMBAT_MOD.RECOIL]
    );
    if (gyroReduction > 0) {
      mods.apply(
        COMBAT_MOD.GYRO,
        -gyroReduction,
        `Gyro stabilization (Rating ${weapon.gyroStabilization})`
      );
    }
  }
  
  // 5. Attacker movement
  if (attacker.movement === 'walking') {
    mods.apply(
      COMBAT_MOD.MOVEMENT_ATTACKER,
      SR2_CONSTANTS.WALKING_PENALTY,
      'Walking while shooting'
    );
  } else if (attacker.movement === 'running') {
    mods.apply(
      COMBAT_MOD.MOVEMENT_ATTACKER,
      SR2_CONSTANTS.RUNNING_PENALTY,
      'Running while shooting'
    );
  }
  
  // 6. Target position (SR2-specific values)
  if (defender.conscious === false) {
    mods.apply(
      COMBAT_MOD.POSITION_TARGET,
      SR2_CONSTANTS.UNCONSCIOUS_TARGET,
      'Target unconscious'
    );
  } else if (defender.prone) {
    const proneMod = range === RANGE_CATEGORIES.SHORT
      ? SR2_CONSTANTS.PRONE_SHORT_RANGE  // SR2: -2
      : SR2_CONSTANTS.PRONE_LONG_RANGE;
    mods.apply(
      COMBAT_MOD.POSITION_TARGET,
      proneMod,
      `Target prone at ${range} range`
    );
  }
  
  // 7. Defender movement
  if (defender.movement === 'running') {
    mods.apply(
      COMBAT_MOD.DEFENDER_MOVING,
      SR2_CONSTANTS.DEFENDER_RUNNING_PENALTY,
      'Target running'
    );
  }
  
  // 8. Friends in melee
  if (defender.inMeleeCombat && range === RANGE_CATEGORIES.SHORT) {
    mods.apply(
      COMBAT_MOD.FRIENDS_IN_MELEE,
      SR2_CONSTANTS.FRIENDS_IN_MELEE_PENALTY,
      'Target engaged in melee'
    );
  }
  
  // 9. Called shot
  if (situation.calledShot) {
    mods.apply(
      COMBAT_MOD.CALLED_SHOT,
      SR2_CONSTANTS.CALLED_SHOT_PENALTY,
      'Called shot'
    );
  }
  
  // 10. Visibility
  if (situation.lightLevel) {
    const lightMod = calculateVisibilityModifier(
      situation.lightLevel,
      attacker.vision,
      situation.conditions
    );
    if (lightMod !== 0) {
      mods.apply(
        COMBAT_MOD.VISIBILITY,
        lightMod,
        `Light level: ${situation.lightLevel}`
      );
    }
  }
  
  // 11. Wound modifiers
  if (attacker.woundLevel) {
    const woundMod = getWoundModifier(attacker.woundLevel);
    if (woundMod > 0) {
      mods.apply(
        COMBAT_MOD.WOUNDS,
        woundMod,
        `${attacker.woundLevel} wounds`
      );
    }
  }
  
  // 12. Situational modifiers (GM discretion)
  if (situation.modifier) {
    mods.apply(
      COMBAT_MOD.SITUATIONAL,
      situation.modifier,
      situation.modifierReason || 'GM ruling'
    );
  }
  
  const finalTN = Math.max(2, baseTN + mods.getTotal());
  
  return {
    baseTN,
    modifiers: mods.getBreakdown(),
    totalModifier: mods.getTotal(),
    finalTN,
    summary: mods.getSummary()
  };
}

/**
 * Calculate melee combat target number
 */
function calculateMeleeTN(params) {
  const {
    attacker = {},
    defender = {},
    attackerWeapon = {},
    defenderWeapon = {},
    situation = {}
  } = params;

  const mods = new CombatModifiers();
  
  // Base TN for melee is always 4
  const baseTN = 4;
  
  // 1. Reach modifiers
  const attackerReach = (attackerWeapon.reach || 0) + (attacker.naturalReach || 0);
  const defenderReach = (defenderWeapon.reach || 0) + (defender.naturalReach || 0);
  const reachDiff = attackerReach - defenderReach;
  
  if (reachDiff !== 0) {
    mods.apply(
      COMBAT_MOD.REACH,
      -reachDiff,  // Negative because higher reach is better
      `Reach ${reachDiff > 0 ? 'advantage' : 'disadvantage'}: ${Math.abs(reachDiff)}`
    );
  }
  
  // 2. Attacker position
  if (attacker.prone) {
    mods.apply(
      COMBAT_MOD.POSITION_ATTACKER,
      2,
      'Attacker prone'
    );
  }
  
  // 3. Defender position
  if (defender.conscious === false) {
    mods.apply(
      COMBAT_MOD.POSITION_TARGET,
      SR2_CONSTANTS.UNCONSCIOUS_TARGET,
      'Defender unconscious'
    );
  } else if (defender.prone) {
    mods.apply(
      COMBAT_MOD.POSITION_TARGET,
      -2,
      'Defender prone'
    );
  }
  
  // 4. Visibility
  if (situation.lightLevel) {
    const lightMod = calculateVisibilityModifier(
      situation.lightLevel,
      attacker.vision,
      situation.conditions
    );
    if (lightMod !== 0) {
      mods.apply(
        COMBAT_MOD.VISIBILITY,
        lightMod,
        `Light level: ${situation.lightLevel}`
      );
    }
  }
  
  // 5. Wound modifiers
  if (attacker.woundLevel) {
    const woundMod = getWoundModifier(attacker.woundLevel);
    if (woundMod > 0) {
      mods.apply(
        COMBAT_MOD.WOUNDS,
        woundMod,
        `${attacker.woundLevel} wounds`
      );
    }
  }
  
  // 6. Situational modifiers
  if (situation.modifier) {
    mods.apply(
      COMBAT_MOD.SITUATIONAL,
      situation.modifier,
      situation.modifierReason || 'GM ruling'
    );
  }
  
  const finalTN = Math.max(2, baseTN + mods.getTotal());
  
  return {
    baseTN,
    modifiers: mods.getBreakdown(),
    totalModifier: mods.getTotal(),
    finalTN,
    summary: mods.getSummary()
  };
}

/**
 * Calculate visibility modifier based on light level and vision enhancements
 */
function calculateVisibilityModifier(lightLevel, vision = {}, conditions = {}) {
  // Get base modifier from light level
  const lightData = LIGHT_LEVELS[lightLevel.toUpperCase()] || LIGHT_LEVELS.NORMAL;
  let modifier = lightData.modifier;
  
  // Vision enhancements
  if (vision.thermographic) {
    // Thermographic ignores most light penalties
    modifier = Math.min(modifier, 1);
  } else if (vision.lowLight) {
    // Low-light reduces penalties
    modifier = Math.floor(modifier / 2);
  }
  
  if (vision.ultrasound) {
    // Ultrasound ignores light completely
    modifier = 0;
  }
  
  // Environmental conditions
  if (conditions.smoke) {
    modifier += conditions.smoke === 'heavy' ? 4 : 2;
  }
  
  if (conditions.fog) {
    modifier += conditions.fog === 'heavy' ? 4 : 2;
  }
  
  return modifier;
}

/**
 * Get wound modifier based on wound level
 */
function getWoundModifier(woundLevel) {
  const modifiers = {
    'light': 1,
    'moderate': 2,
    'serious': 3,
    'deadly': 99  // Unconscious/near death
  };
  
  return modifiers[woundLevel.toLowerCase()] || 0;
}

/**
 * Determine range category based on distance and weapon type
 */
function determineRange(distance, weaponType) {
  // Weapon range tables (in meters) - SR2 ranges
  // Ranges are: 0-short, short+1-medium, medium+1-long, long+1-extreme
  const ranges = {
    'hold-out pistol': { short: 15, medium: 30, long: 45, extreme: 60 },
    'light pistol': { short: 15, medium: 30, long: 45, extreme: 60 },
    'heavy pistol': { short: 20, medium: 30, long: 40, extreme: 60 },
    'smg': { short: 40, medium: 80, long: 120, extreme: 160 },
    'shotgun': { short: 20, medium: 40, long: 60, extreme: 80 },
    'sporting rifle': { short: 60, medium: 120, long: 180, extreme: 240 },
    'sniper rifle': { short: 80, medium: 160, long: 240, extreme: 320 },
    'assault rifle': { short: 40, medium: 80, long: 120, extreme: 160 },
    'lmg': { short: 40, medium: 80, long: 120, extreme: 160 }
  };
  
  const weaponRanges = ranges[weaponType.toLowerCase()] || ranges['heavy pistol'];
  
  if (distance <= weaponRanges.short) return RANGE_CATEGORIES.SHORT;
  if (distance <= weaponRanges.medium) return RANGE_CATEGORIES.MEDIUM;
  if (distance <= weaponRanges.long) return RANGE_CATEGORIES.LONG;
  if (distance <= weaponRanges.extreme) return RANGE_CATEGORIES.EXTREME;
  
  return null; // Out of range
}

export {
  COMBAT_MOD,
  MODIFIER_NAMES,
  SR2_CONSTANTS,
  LIGHT_LEVELS,
  RANGE_CATEGORIES,
  BASE_TN_BY_RANGE,
  CombatModifiers,
  calculateRangedTN,
  calculateMeleeTN,
  calculateVisibilityModifier,
  getWoundModifier,
  determineRange
};
