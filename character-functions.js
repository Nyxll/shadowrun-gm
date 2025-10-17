/**
 * Character Management Functions for Shadowrun GM MCP Server
 * Implements create_character, get_character, and update_character
 */

/**
 * Create a new Shadowrun character
 */
export async function createCharacter(pool, args) {
  const {
    name,
    campaign_id,
    metatype,
    archetype,
    attributes,
    skills,
    starting_nuyen = 5000,
    starting_karma = 0,
  } = args;

  // Get metatype data
  const metatypeResult = await pool.query(
    'SELECT * FROM metatypes WHERE LOWER(name) = LOWER($1)',
    [metatype]
  );

  if (metatypeResult.rows.length === 0) {
    throw new Error(`Unknown metatype: ${metatype}`);
  }

  const metatypeData = metatypeResult.rows[0];

  // Set default attributes if not provided
  const defaultAttributes = {
    body: attributes?.body || metatypeData.body_range[0],
    quickness: attributes?.quickness || metatypeData.quickness_range[0],
    strength: attributes?.strength || metatypeData.strength_range[0],
    charisma: attributes?.charisma || metatypeData.charisma_range[0],
    intelligence: attributes?.intelligence || metatypeData.intelligence_range[0],
    willpower: attributes?.willpower || metatypeData.willpower_range[0],
    essence: attributes?.essence || 6.0,
    magic: attributes?.magic || 0,
    reaction: attributes?.reaction || metatypeData.reaction_range[0],
  };

  // Create character
  const result = await pool.query(
    `INSERT INTO sr_characters (
      name, campaign_id, metatype_id, archetype, attributes,
      essence, nuyen, good_karma, karma_pool
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
    RETURNING *`,
    [
      name,
      campaign_id || null,
      metatypeData.id,
      archetype || null,
      JSON.stringify(defaultAttributes),
      defaultAttributes.essence,
      starting_nuyen,
      starting_karma,
      starting_karma,
    ]
  );

  const character = result.rows[0];

  // Add skills if provided
  if (skills && skills.length > 0) {
    for (const skill of skills) {
      await pool.query(
        `INSERT INTO character_skills (character_id, skill_name, rating, specialization)
         VALUES ($1, $2, $3, $4)`,
        [character.id, skill.name, skill.rating || 1, skill.specialization || null]
      );
    }
  }

  return `# Character Created Successfully! 🎲

**ID:** ${character.id}
**Name:** ${character.name}
**Metatype:** ${metatypeData.name}
**Archetype:** ${archetype || 'Not set'}

## Attributes
${Object.entries(defaultAttributes)
  .map(([key, value]) => `- **${key.charAt(0).toUpperCase() + key.slice(1)}:** ${value}`)
  .join('\n')}

## Resources
- **Nuyen:** ¥${starting_nuyen.toLocaleString()}
- **Karma Pool:** ${starting_karma}
- **Essence:** ${defaultAttributes.essence}

${skills && skills.length > 0 ? `## Starting Skills\n${skills.map(s => `- ${s.name} ${s.rating}${s.specialization ? ` (${s.specialization})` : ''}`).join('\n')}` : ''}

Use \`get_character\` with ID ${character.id} to view full details.
Use \`update_character\` to modify attributes, add skills, gear, etc.`;
}

/**
 * Get character data
 */
export async function getCharacter(pool, args) {
  const { character_id, include_history = false, include_modifiers = true } = args;

  // Get character
  const charResult = await pool.query(
    `SELECT c.*, m.name as metatype_name
     FROM sr_characters c
     JOIN metatypes m ON c.metatype_id = m.id
     WHERE c.id = $1`,
    [character_id]
  );

  if (charResult.rows.length === 0) {
    return `Character with ID ${character_id} not found.`;
  }

  const char = charResult.rows[0];

  // Get skills
  const skillsResult = await pool.query(
    'SELECT * FROM character_skills WHERE character_id = $1 ORDER BY skill_name',
    [character_id]
  );

  // Get spells
  const spellsResult = await pool.query(
    'SELECT * FROM character_spells WHERE character_id = $1 ORDER BY spell_name',
    [character_id]
  );

  // Get gear
  const gearResult = await pool.query(
    'SELECT * FROM character_gear WHERE character_id = $1 ORDER BY gear_name',
    [character_id]
  );

  // Get modifiers if requested
  let modifiers = [];
  if (include_modifiers) {
    const modResult = await pool.query(
      'SELECT * FROM character_modifiers WHERE character_id = $1 AND is_active = true ORDER BY modifier_target',
      [character_id]
    );
    modifiers = modResult.rows;
  }

  // Get history if requested
  let history = [];
  if (include_history) {
    const histResult = await pool.query(
      'SELECT * FROM character_history WHERE character_id = $1 ORDER BY changed_at DESC LIMIT 20',
      [character_id]
    );
    history = histResult.rows;
  }

  // Format output
  let output = `# ${char.name}\n\n`;
  output += `**ID:** ${char.id} | **Metatype:** ${char.metatype_name} | **Archetype:** ${char.archetype || 'None'}\n`;
  if (char.campaign_id) output += `**Campaign:** ${char.campaign_id}\n`;
  output += `\n`;

  // Attributes
  output += `## Attributes\n\n`;
  const attrs = char.attributes;
  output += `| Attribute | Value |\n|-----------|-------|\n`;
  for (const [key, value] of Object.entries(attrs)) {
    output += `| ${key.charAt(0).toUpperCase() + key.slice(1)} | ${value} |\n`;
  }
  output += `\n`;

  // Derived Stats
  output += `## Derived Stats\n\n`;
  output += `- **Essence:** ${char.essence}\n`;
  output += `- **Initiative:** ${attrs.reaction}d6 + ${attrs.reaction}\n`;
  output += `- **Condition Monitor:** Physical ${Math.ceil(10 + (attrs.body / 2))}, Stun ${Math.ceil(10 + (attrs.willpower / 2))}\n`;
  output += `\n`;

  // Resources
  output += `## Resources\n\n`;
  output += `- **Nuyen:** ¥${char.nuyen?.toLocaleString() || 0}\n`;
  output += `- **Good Karma:** ${char.good_karma || 0}\n`;
  output += `- **Karma Pool:** ${char.karma_pool || 0}\n`;
  output += `\n`;

  // Skills
  if (skillsResult.rows.length > 0) {
    output += `## Skills (${skillsResult.rows.length})\n\n`;
    output += `| Skill | Rating | Specialization |\n|-------|--------|----------------|\n`;
    for (const skill of skillsResult.rows) {
      output += `| ${skill.skill_name} | ${skill.rating} | ${skill.specialization || '-'} |\n`;
    }
    output += `\n`;
  }

  // Spells
  if (spellsResult.rows.length > 0) {
    output += `## Spells (${spellsResult.rows.length})\n\n`;
    output += `| Spell | Category | Type | Drain |\n|-------|----------|------|-------|\n`;
    for (const spell of spellsResult.rows) {
      output += `| ${spell.spell_name} | ${spell.category || '-'} | ${spell.type || '-'} | ${spell.drain || '-'} |\n`;
    }
    output += `\n`;
  }

  // Gear
  if (gearResult.rows.length > 0) {
    output += `## Gear (${gearResult.rows.length})\n\n`;
    output += `| Item | Category | Quantity | Notes |\n|------|----------|----------|-------|\n`;
    for (const item of gearResult.rows) {
      output += `| ${item.gear_name} | ${item.category || '-'} | ${item.quantity || 1} | ${item.notes || '-'} |\n`;
    }
    output += `\n`;
  }

  // Active Modifiers
  if (modifiers.length > 0) {
    output += `## Active Modifiers (${modifiers.length})\n\n`;
    output += `| Target | Value | Type | Source |\n|--------|-------|------|--------|\n`;
    for (const mod of modifiers) {
      output += `| ${mod.modifier_target} | ${mod.modifier_value > 0 ? '+' : ''}${mod.modifier_value} | ${mod.modifier_type} | ${mod.source_name} |\n`;
    }
    output += `\n`;
  }

  // History
  if (history.length > 0) {
    output += `## Recent Changes (${history.length})\n\n`;
    for (const h of history) {
      const date = new Date(h.changed_at).toLocaleDateString();
      output += `- **${date}** - ${h.change_type}: ${h.reason || 'No reason given'}`;
      if (h.karma_spent) output += ` (${h.karma_spent} karma)`;
      output += `\n`;
    }
  }

  return output;
}

/**
 * Update character
 */
export async function updateCharacter(pool, args) {
  const {
    character_id,
    update_type,
    update_data,
    karma_cost,
    use_house_rules = true,
    reason,
    gm_override = false,
    session_date,
  } = args;

  // Get character
  const charResult = await pool.query('SELECT * FROM sr_characters WHERE id = $1', [character_id]);
  if (charResult.rows.length === 0) {
    throw new Error(`Character with ID ${character_id} not found.`);
  }

  const character = charResult.rows[0];
  let finalKarmaCost = karma_cost;
  let output = '';

  // Calculate karma cost if not provided
  if (finalKarmaCost === undefined) {
    finalKarmaCost = await calculateKarmaCost(pool, update_type, update_data, character, use_house_rules);
  }

  // Validate karma availability
  if (finalKarmaCost > 0 && finalKarmaCost > character.good_karma && !gm_override) {
    throw new Error(`Insufficient karma: need ${finalKarmaCost}, have ${character.good_karma}`);
  }

  // Process update based on type
  switch (update_type) {
    case 'attribute':
      output = await updateAttribute(pool, character, update_data, finalKarmaCost, gm_override);
      break;
    case 'skill':
      output = await updateSkill(pool, character, update_data, finalKarmaCost);
      break;
    case 'spell':
      output = await updateSpell(pool, character, update_data, finalKarmaCost);
      break;
    case 'gear':
      output = await updateGear(pool, character, update_data);
      break;
    case 'cyberware':
      output = await updateCyberware(pool, character, update_data);
      break;
    case 'karma':
      output = await updateKarma(pool, character, update_data);
      break;
    case 'damage':
      output = await updateDamage(pool, character, update_data);
      break;
    default:
      throw new Error(`Unknown update type: ${update_type}`);
  }

  // Deduct karma if cost > 0
  if (finalKarmaCost > 0) {
    await pool.query(
      'UPDATE sr_characters SET good_karma = good_karma - $1 WHERE id = $2',
      [finalKarmaCost, character_id]
    );
  }

  // Log to history
  await pool.query(
    `INSERT INTO character_history (character_id, change_type, karma_spent, reason, session_date)
     VALUES ($1, $2, $3, $4, $5)`,
    [character_id, update_type, finalKarmaCost, reason || 'No reason provided', session_date || new Date().toISOString()]
  );

  return output + `\n\n**Karma spent:** ${finalKarmaCost}\n**Remaining karma:** ${character.good_karma - finalKarmaCost}`;
}

/**
 * Calculate karma cost
 */
async function calculateKarmaCost(pool, update_type, update_data, character, use_house_rules) {
  let baseCost = 0;

  switch (update_type) {
    case 'attribute':
      baseCost = update_data.new_value * 2;
      break;
    case 'skill':
      if (update_data.action === 'learn') baseCost = 1;
      else if (update_data.action === 'improve') baseCost = update_data.new_rating;
      else if (update_data.action === 'add_specialization') baseCost = 2;
      break;
    case 'spell':
      baseCost = update_data.force;
      break;
    default:
      baseCost = 0;
  }

  // Apply house rules if enabled
  if (use_house_rules && character.campaign_id) {
    const rulesResult = await pool.query(
      `SELECT * FROM house_rules 
       WHERE campaign_id = $1 AND is_active = true AND rule_type = 'karma_multiplier'
       ORDER BY priority DESC`,
      [character.campaign_id]
    );

    for (const rule of rulesResult.rows) {
      if (rule.modifier_value) {
        baseCost = Math.floor(baseCost * rule.modifier_value);
      }
    }
  }

  return baseCost;
}

/**
 * Update attribute
 */
async function updateAttribute(pool, character, update_data, karmaCost, gmOverride) {
  const { attribute_name, new_value } = update_data;

  // Validate attribute exists
  const attrs = character.attributes;
  if (!(attribute_name in attrs)) {
    throw new Error(`Unknown attribute: ${attribute_name}`);
  }

  const oldValue = attrs[attribute_name];

  // Update attribute
  attrs[attribute_name] = new_value;

  await pool.query(
    'UPDATE sr_characters SET attributes = $1 WHERE id = $2',
    [JSON.stringify(attrs), character.id]
  );

  return `# Attribute Updated\n\n**${attribute_name.charAt(0).toUpperCase() + attribute_name.slice(1)}:** ${oldValue} → ${new_value}`;
}

/**
 * Update skill
 */
async function updateSkill(pool, character, update_data, karmaCost) {
  const { action, skill_name, new_rating, specialization } = update_data;

  if (action === 'learn') {
    await pool.query(
      'INSERT INTO character_skills (character_id, skill_name, rating) VALUES ($1, $2, $3)',
      [character.id, skill_name, 1]
    );
    return `# Skill Learned\n\n**${skill_name}** learned at rating 1`;
  } else if (action === 'improve') {
    await pool.query(
      'UPDATE character_skills SET rating = $1 WHERE character_id = $2 AND skill_name = $3',
      [new_rating, character.id, skill_name]
    );
    return `# Skill Improved\n\n**${skill_name}** improved to rating ${new_rating}`;
  } else if (action === 'add_specialization') {
    await pool.query(
      'UPDATE character_skills SET specialization = $1 WHERE character_id = $2 AND skill_name = $3',
      [specialization, character.id, skill_name]
    );
    return `# Specialization Added\n\n**${skill_name}** specialized in ${specialization}`;
  }
}

/**
 * Update spell
 */
async function updateSpell(pool, character, update_data, karmaCost) {
  const { spell_id, spell_name, force } = update_data;

  let spellId = spell_id;
  if (!spellId && spell_name) {
    const result = await pool.query('SELECT id FROM spells WHERE LOWER(name) = LOWER($1)', [spell_name]);
    if (result.rows.length > 0) {
      spellId = result.rows[0].id;
    }
  }

  if (!spellId) {
    throw new Error(`Spell not found: ${spell_name || spell_id}`);
  }

  await pool.query(
    'INSERT INTO character_spells (character_id, spell_id, force) VALUES ($1, $2, $3)',
    [character.id, spellId, force]
  );

  return `# Spell Learned\n\n**${spell_name}** learned at Force ${force}`;
}

/**
 * Update gear
 */
async function updateGear(pool, character, update_data) {
  const { action, gear_id, quantity, cost_nuyen, notes } = update_data;

  if (action === 'purchase') {
    await pool.query(
      'INSERT INTO character_gear (character_id, gear_id, quantity, notes) VALUES ($1, $2, $3, $4)',
      [character.id, gear_id, quantity || 1, notes]
    );

    if (cost_nuyen) {
      await pool.query(
        'UPDATE sr_characters SET nuyen = nuyen - $1 WHERE id = $2',
        [cost_nuyen, character.id]
      );
    }

    return `# Gear Purchased\n\nGear ID ${gear_id} added (quantity: ${quantity || 1})${cost_nuyen ? `\n**Cost:** ¥${cost_nuyen.toLocaleString()}` : ''}`;
  }
}

/**
 * Update cyberware
 */
async function updateCyberware(pool, character, update_data) {
  const { action, gear_id, essence_cost, installation_cost, notes } = update_data;

  if (action === 'install') {
    // Add to gear
    await pool.query(
      'INSERT INTO character_gear (character_id, gear_id, quantity, notes) VALUES ($1, $2, 1, $3)',
      [character.id, gear_id, notes || 'Cyberware']
    );

    // Update essence
    const newEssence = character.essence - essence_cost;
    const newMagic = Math.max(0, Math.floor(newEssence));

    await pool.query(
      `UPDATE sr_characters 
       SET essence = $1,
           attributes = jsonb_set(attributes, '{magic}', to_jsonb($2::int)),
           nuyen = nuyen - $3
       WHERE id = $4`,
      [newEssence, newMagic, installation_cost || 0, character.id]
    );

    return `# Cyberware Installed\n\nGear ID ${gear_id} installed\n**Essence Cost:** ${essence_cost}\n**New Essence:** ${newEssence.toFixed(2)}\n**Magic Rating:** ${newMagic}${installation_cost ? `\n**Installation Cost:** ¥${installation_cost.toLocaleString()}` : ''}`;
  }
}

/**
 * Update karma
 */
async function updateKarma(pool, character, update_data) {
  const { action, amount, reason } = update_data;

  if (action === 'earn') {
    await pool.query(
      'UPDATE sr_characters SET good_karma = good_karma + $1, karma_pool = karma_pool + $1 WHERE id = $2',
      [amount, character.id]
    );
    return `# Karma Earned\n\n**Amount:** ${amount}\n**Reason:** ${reason || 'Not specified'}`;
  } else if (action === 'spend') {
    await pool.query(
      'UPDATE sr_characters SET good_karma = good_karma - $1 WHERE id = $2',
      [amount, character.id]
    );
    return `# Karma Spent\n\n**Amount:** ${amount}\n**Reason:** ${reason || 'Not specified'}`;
  }
}

/**
 * Update damage
 */
async function updateDamage(pool, character, update_data) {
  const { damage_type, action, amount } = update_data;

  const field = damage_type === 'physical' ? 'physical_damage' : 'stun_damage';

  if (action === 'take') {
    await pool.query(
      `UPDATE sr_characters SET ${field} = ${field} + $1 WHERE id = $2`,
      [amount, character.id]
    );
    return `# Damage Taken\n\n**Type:** ${damage_type}\n**Amount:** ${amount} boxes`;
  } else if (action === 'heal') {
    await pool.query(
      `UPDATE sr_characters SET ${field} = GREATEST(0, ${field} - $1) WHERE id = $2`,
      [amount, character.id]
    );
    return `# Damage Healed\n\n**Type:** ${damage_type}\n**Amount:** ${amount} boxes`;
  }
}
