/**
 * MCP Tool Definitions for Combat Modifiers
 * Calls PHP API for all combat calculations
 */

const axios = require('axios');

const API_BASE_URL = process.env.COMBAT_API_URL || 'https://shadowrun2.com/dice/api.php';

/**
 * Helper function to call the combat API
 */
async function callCombatAPI(action, data = {}) {
  try {
    const response = await axios.post(API_BASE_URL, {
      action,
      ...data
    }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (response.data.success) {
      return response.data.data;
    } else {
      throw new Error(response.data.error || 'API request failed');
    }
  } catch (error) {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw error;
  }
}

/**
 * Calculate ranged combat target number with modifiers
 */
async function calculateRangedCombatTN(args) {
  const {
    weapon_name,
    weapon_type,
    distance,
    range,
    attacker = {},
    defender = {},
    situation = {}
  } = args;

  // Determine range if distance provided
  let actualRange = range;
  if (distance && weapon_type && !range) {
    const rangeResult = await callCombatAPI('determine_range', {
      distance,
      weapon_type
    });
    actualRange = rangeResult.range;
    
    if (!actualRange) {
      return {
        error: true,
        message: `Target is out of range (${distance}m exceeds maximum range for ${weapon_type})`
      };
    }
  }

  if (!actualRange) {
    return {
      error: true,
      message: 'Either range category or distance + weapon_type must be provided'
    };
  }

  // Build weapon object
  const weapon = {
    name: weapon_name,
    type: weapon_type,
    smartlink: situation.smartlink || false,
    recoilComp: situation.recoil_compensation || 0,
    gyroStabilization: situation.gyro_rating || 0
  };

  // Call PHP API
  const result = await callCombatAPI('calculate_ranged_tn', {
    weapon,
    range: actualRange,
    attacker,
    defender,
    situation
  });

  return {
    weapon: weapon_name || weapon_type,
    range: actualRange,
    distance: distance || 'not specified',
    baseTN: result.baseTN,
    modifiers: result.modifiers,
    totalModifier: result.totalModifier,
    finalTN: result.finalTN,
    summary: result.summary,
    explanation: formatCombatExplanation(result, 'ranged')
  };
}

/**
 * Calculate melee combat target number with modifiers
 */
async function calculateMeleeCombatTN(args) {
  const {
    attacker = {},
    defender = {},
    attacker_weapon = {},
    defender_weapon = {},
    situation = {}
  } = args;

  // Call PHP API
  const result = await callCombatAPI('calculate_melee_tn', {
    attacker,
    defender,
    attackerWeapon: attacker_weapon,
    defenderWeapon: defender_weapon,
    situation
  });

  return {
    baseTN: result.baseTN,
    modifiers: result.modifiers,
    totalModifier: result.totalModifier,
    finalTN: result.finalTN,
    summary: result.summary,
    explanation: formatCombatExplanation(result, 'melee')
  };
}

/**
 * Get detailed explanation of combat modifiers
 */
async function explainCombatModifiers(args) {
  const { combat_type = 'ranged' } = args;

  // Call PHP API
  const result = await callCombatAPI('explain_combat_modifiers', {
    combat_type
  });

  // Format for MCP response
  const modifiers = Object.entries(result.modifiers).map(([name, description]) => ({
    name,
    description
  }));

  return {
    type: `${result.combat_type.charAt(0).toUpperCase() + result.combat_type.slice(1)} Combat Modifiers`,
    modifiers,
    notes: combat_type === 'ranged' ? [
      'Minimum TN is always 2',
      'Gyro stabilization reduces movement + recoil penalties',
      'Vision enhancements (low-light, thermographic, ultrasound) reduce visibility penalties'
    ] : [
      'Base TN for melee is always 4',
      'Minimum TN is always 2',
      'Trolls have +1 natural reach',
      'Melee is an opposed test (both sides roll)'
    ]
  };
}

/**
 * List available light levels and their effects
 */
async function listLightLevels() {
  // Call PHP API
  const result = await callCombatAPI('list_light_levels', {});

  // Format for MCP response
  const levels = Object.entries(result).map(([key, data]) => ({
    level: key.toLowerCase(),
    name: data.name,
    modifier: data.modifier,
    description: getLightLevelDescription(key)
  }));

  return {
    levels,
    vision_enhancements: [
      {
        type: 'Low-Light Vision',
        effect: 'Reduces light penalties by half (round down)'
      },
      {
        type: 'Thermographic Vision',
        effect: 'Reduces light penalties to maximum of +1'
      },
      {
        type: 'Ultrasound',
        effect: 'Ignores all light penalties completely'
      }
    ]
  };
}

/**
 * Format combat explanation for human readability
 */
function formatCombatExplanation(result, combatType) {
  const lines = [];
  
  lines.push(`${combatType.toUpperCase()} COMBAT TARGET NUMBER CALCULATION`);
  lines.push('='.repeat(50));
  lines.push(`Base TN: ${result.baseTN}`);
  lines.push('');
  
  if (result.modifiers && result.modifiers.length > 0) {
    lines.push('Modifiers:');
    result.modifiers.forEach(mod => {
      const sign = mod.value > 0 ? '+' : '';
      const exp = mod.explanation ? ` (${mod.explanation})` : '';
      lines.push(`  ${mod.type}: ${sign}${mod.value}${exp}`);
    });
    lines.push('');
    lines.push(`Total Modifier: ${result.totalModifier > 0 ? '+' : ''}${result.totalModifier}`);
  } else {
    lines.push('No modifiers apply');
  }
  
  lines.push('');
  lines.push(`FINAL TARGET NUMBER: ${result.finalTN}`);
  lines.push('='.repeat(50));
  
  return lines.join('\n');
}

/**
 * Get description for light level
 */
function getLightLevelDescription(level) {
  const descriptions = {
    NORMAL: 'Full daylight or bright artificial lighting',
    PARTIAL: 'Overcast day, street lighting, or dim interior',
    DIM: 'Twilight, shadowy areas, or minimal lighting',
    DARK: 'Night with no moon, unlit interior, or total darkness'
  };
  return descriptions[level.toUpperCase()] || 'Unknown light level';
}

module.exports = {
  calculateRangedCombatTN,
  calculateMeleeCombatTN,
  explainCombatModifiers,
  listLightLevels
};
