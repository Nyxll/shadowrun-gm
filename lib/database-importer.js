/**
 * PHASE 1 - STEP 1.4: Database Importer
 * 
 * Handles importing parsed gear data into the PostgreSQL database.
 * Supports batch imports, transactions, and duplicate detection.
 */

import pg from 'pg';

const { Pool } = pg;

export class DatabaseImporter {
  constructor(connectionConfig) {
    this.pool = new Pool(connectionConfig);
  }

  /**
   * Import items into the gear table
   * @param {Array} items - Parsed items from FieldParser
   * @param {Object} schema - Category schema from CategoryDetector
   * @param {Object} options - Import options
   * @returns {Object} Import results
   */
  async importItems(items, schema, options = {}) {
    const {
      skipDuplicates = true,
      updateExisting = false,
      dryRun = false
    } = options;

    const results = {
      inserted: 0,
      updated: 0,
      skipped: 0,
      errors: [],
      items: []
    };

    if (dryRun) {
      // Dry run - just validate
      for (const item of items) {
        try {
          this.validateItem(item, schema);
          results.inserted++;
        } catch (error) {
          results.errors.push({
            item: item.name,
            error: error.message
          });
        }
      }
      return results;
    }

    // Import items individually (no transaction to avoid rollback on duplicates)
    for (const item of items) {
      const client = await this.pool.connect();
      
      try {
        const result = await this.importItem(client, item, schema, {
          skipDuplicates,
          updateExisting
        });

        if (result.action === 'inserted') {
          results.inserted++;
          results.items.push({ ...item, id: result.id });
        } else if (result.action === 'updated') {
          results.updated++;
          results.items.push({ ...item, id: result.id });
        } else if (result.action === 'skipped') {
          results.skipped++;
        }
      } catch (error) {
        results.errors.push({
          item: item.name,
          error: error.message
        });
      } finally {
        client.release();
      }
    }

    return results;
  }

  /**
   * Import a single item
   * @param {Object} client - PostgreSQL client
   * @param {Object} item - Parsed item
   * @param {Object} schema - Category schema
   * @param {Object} options - Import options
   * @returns {Object} Import result
   */
  async importItem(client, item, schema, options = {}) {
    const {
      skipDuplicates = true,
      updateExisting = false
    } = options;

    // Check for existing item
    const existing = await this.findExistingItem(client, item.name, schema.category, schema.subcategory);

    if (existing) {
      if (skipDuplicates && !updateExisting) {
        return { action: 'skipped', id: existing.id };
      }

      if (updateExisting) {
        await this.updateItem(client, existing.id, item, schema);
        return { action: 'updated', id: existing.id };
      }
    }

    // Insert new item
    const id = await this.insertItem(client, item, schema);
    return { action: 'inserted', id };
  }

  /**
   * Find existing item by name and category
   * @param {Object} client - PostgreSQL client
   * @param {string} name - Item name
   * @param {string} category - Category
   * @param {string} subcategory - Subcategory
   * @returns {Object|null} Existing item or null
   */
  async findExistingItem(client, name, category, subcategory) {
    const query = `
      SELECT id, name, category, subcategory
      FROM gear
      WHERE LOWER(name) = LOWER($1)
        AND category = $2
        AND (subcategory = $3 OR (subcategory IS NULL AND $3 IS NULL))
      LIMIT 1
    `;

    const result = await client.query(query, [name, category, subcategory]);
    return result.rows.length > 0 ? result.rows[0] : null;
  }

  /**
   * Insert a new item into the database
   * @param {Object} client - PostgreSQL client
   * @param {Object} item - Parsed item
   * @param {Object} schema - Category schema
   * @returns {number} Inserted item ID
   */
  async insertItem(client, item, schema) {
    // Build the gear record
    const gearRecord = this.buildGearRecord(item, schema);

    // Prepare insert statement
    const fields = Object.keys(gearRecord);
    const placeholders = fields.map((_, i) => `$${i + 1}`).join(', ');
    const query = `
      INSERT INTO gear (${fields.join(', ')})
      VALUES (${placeholders})
      RETURNING id
    `;

    const result = await client.query(query, Object.values(gearRecord));
    return result.rows[0].id;
  }

  /**
   * Update an existing item
   * @param {Object} client - PostgreSQL client
   * @param {number} id - Item ID
   * @param {Object} item - Parsed item
   * @param {Object} schema - Category schema
   */
  async updateItem(client, id, item, schema) {
    const gearRecord = this.buildGearRecord(item, schema);

    // Build update statement
    const fields = Object.keys(gearRecord);
    const setClause = fields.map((f, i) => `${f} = $${i + 1}`).join(', ');
    const query = `
      UPDATE gear
      SET ${setClause}
      WHERE id = $${fields.length + 1}
    `;

    await client.query(query, [...Object.values(gearRecord), id]);
  }

  /**
   * Build a gear record for database insertion
   * @param {Object} item - Parsed item
   * @param {Object} schema - Category schema
   * @returns {Object} Gear record
   */
  buildGearRecord(item, schema) {
    const record = {
      name: item.name,
      category: schema.category,
      subcategory: schema.subcategory || null
    };

    // Add standard fields
    if (item.cost !== undefined) {
      record.cost = this.serializeCost(item.cost);
    }

    if (item.availability !== undefined) {
      record.availability = this.serializeAvailability(item.availability);
    }

    if (item.street_index !== undefined) {
      record.street_index = item.street_index;
    }

    // Build base_stats JSON object
    const baseStats = {};

    if (item.concealability !== undefined) {
      baseStats.conceal = item.concealability;
    }

    if (item.weight !== undefined) {
      baseStats.weight = item.weight;
    }

    // Category-specific fields
    if (schema.category === 'weapon') {
      this.addWeaponFields(baseStats, item);
    } else if (schema.category === 'armor') {
      this.addArmorFields(baseStats, item);
    } else if (schema.category === 'ammunition') {
      this.addAmmunitionFields(baseStats, item);
    } else if (schema.category === 'explosive') {
      this.addExplosiveFields(baseStats, item);
    }

    // Store base_stats as JSONB
    if (Object.keys(baseStats).length > 0) {
      record.base_stats = baseStats;
    }

    // Store any remaining fields in base_stats as well (no separate stats column)
    const extraStats = this.buildStatsJson(item, baseStats);
    if (Object.keys(extraStats).length > 0) {
      // Merge extra stats into base_stats
      record.base_stats = { ...baseStats, ...extraStats };
    }

    return record;
  }

  /**
   * Add weapon-specific fields
   * @param {Object} baseStats - Base stats object
   * @param {Object} item - Parsed item
   */
  addWeaponFields(baseStats, item) {
    if (item.damage !== undefined) {
      baseStats.damage = this.serializeDamage(item.damage);
    }

    if (item.mode !== undefined) {
      baseStats.mode = Array.isArray(item.mode) ? item.mode.join('/') : item.mode;
    }

    if (item.ammunition !== undefined || item.ammo !== undefined) {
      const ammo = item.ammunition || item.ammo;
      baseStats.ammo = this.serializeAmmunition(ammo);
    }

    if (item.reach !== undefined) {
      baseStats.reach = item.reach;
    }
  }

  /**
   * Add armor-specific fields
   * @param {Object} baseStats - Base stats object
   * @param {Object} item - Parsed item
   */
  addArmorFields(baseStats, item) {
    if (item.ballistic !== undefined) {
      baseStats.ballistic = item.ballistic;
    }

    if (item.impact !== undefined) {
      baseStats.impact = item.impact;
    }
  }

  /**
   * Add ammunition-specific fields
   * @param {Object} baseStats - Base stats object
   * @param {Object} item - Parsed item
   */
  addAmmunitionFields(baseStats, item) {
    if (item.damage !== undefined) {
      baseStats.damage = this.serializeDamage(item.damage);
    }
  }

  /**
   * Add explosive-specific fields
   * @param {Object} baseStats - Base stats object
   * @param {Object} item - Parsed item
   */
  addExplosiveFields(baseStats, item) {
    if (item.rating !== undefined) {
      baseStats.rating = item.rating;
    }
  }

  /**
   * Build stats JSON from remaining fields
   * @param {Object} item - Parsed item
   * @param {Object} baseStats - Base stats already processed
   * @returns {Object} Stats object
   */
  buildStatsJson(item, baseStats) {
    const stats = {};
    const usedFields = new Set([
      'name', 'category_id', 'raw_line',
      'cost', 'availability', 'street_index', 'concealability', 'weight',
      'damage', 'mode', 'ammunition', 'ammo', 'reach',
      'ballistic', 'impact', 'rating',
      ...Object.keys(baseStats)
    ]);

    for (const [key, value] of Object.entries(item)) {
      if (!usedFields.has(key) && value !== null && value !== undefined) {
        stats[key] = value;
      }
    }

    return stats;
  }

  /**
   * Serialize cost for database storage
   * @param {*} cost - Cost value
   * @returns {number|null} Serialized cost
   */
  serializeCost(cost) {
    if (cost === null || cost === undefined) return null;
    if (typeof cost === 'number') return cost;
    if (typeof cost === 'string' && cost.toLowerCase() === 'always') return 0;
    return null;
  }

  /**
   * Serialize availability for database storage
   * @param {*} availability - Availability value
   * @returns {string|null} Serialized availability
   */
  serializeAvailability(availability) {
    if (availability === null || availability === undefined) return null;
    if (typeof availability === 'object') {
      // Format as "rating/time" string
      return `${availability.rating}/${availability.time}`;
    }
    return String(availability);
  }

  /**
   * Serialize damage for database storage
   * @param {*} damage - Damage value
   * @returns {string|null} Serialized damage
   */
  serializeDamage(damage) {
    if (damage === null || damage === undefined) return null;
    if (typeof damage === 'object') {
      return `${damage.power}${damage.type}`;
    }
    return String(damage);
  }

  /**
   * Serialize ammunition for database storage
   * @param {*} ammo - Ammunition value
   * @returns {string|null} Serialized ammunition
   */
  serializeAmmunition(ammo) {
    if (ammo === null || ammo === undefined) return null;
    if (typeof ammo === 'object') {
      return `${ammo.capacity}(${ammo.type})`;
    }
    return String(ammo);
  }

  /**
   * Validate item before import
   * @param {Object} item - Parsed item
   * @param {Object} schema - Category schema
   * @throws {Error} If validation fails
   */
  validateItem(item, schema) {
    if (!item.name || item.name.trim().length === 0) {
      throw new Error('Item name is required');
    }

    if (!schema.category) {
      throw new Error('Category is required');
    }
  }

  /**
   * Get import statistics
   * @param {string} category - Category to check
   * @returns {Object} Statistics
   */
  async getImportStats(category = null) {
    let query = 'SELECT category, subcategory, COUNT(*) as count FROM gear';
    const params = [];

    if (category) {
      query += ' WHERE category = $1';
      params.push(category);
    }

    query += ' GROUP BY category, subcategory ORDER BY category, subcategory';

    const result = await this.pool.query(query, params);
    return result.rows;
  }

  /**
   * Close database connection
   */
  async close() {
    await this.pool.end();
  }
}
