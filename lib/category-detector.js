/**
 * PHASE 1 - STEP 1.2: Category Detector
 * 
 * Detects and parses category headers from GEAR.DAT file.
 * Category headers follow the format: 0-{id}|{name}|{fieldCount}|{field1}|{field2}|...
 */

export class CategoryDetector {
  constructor() {
    // Load category mappings from analysis
    this.categoryMappings = this.buildCategoryMappings();
  }

  /**
   * Detect if a line is a category header
   * @param {string} line - Line from GEAR.DAT
   * @returns {Object|null} Category info or null if not a category header
   */
  detectCategory(line) {
    const trimmed = line.trim();
    
    // Category headers start with "0-"
    if (!trimmed.startsWith('0-')) {
      return null;
    }

    // Parse: 0-{id}|{name}|{fieldCount}|{field1}|{field2}|...
    const match = trimmed.match(/^0-(\d+)\|(.+?)\|(\d+)\|(.+)$/);
    
    if (!match) {
      return null;
    }

    const categoryId = parseInt(match[1]);
    const categoryName = match[2];
    const fieldCount = parseInt(match[3]);
    const fieldsStr = match[4];
    
    // Split fields and clean them
    const fields = fieldsStr.split('|')
      .map(f => f.trim())
      .filter(f => f.length > 0);

    // Validate field count matches
    if (fields.length !== fieldCount) {
      console.warn(`Warning: Category ${categoryId} field count mismatch. Expected ${fieldCount}, got ${fields.length}`);
    }

    return {
      id: categoryId,
      name: categoryName,
      fieldCount: fieldCount,
      fields: fields,
      rawLine: trimmed
    };
  }

  /**
   * Build schema mapping for a category
   * Maps GEAR.DAT fields to database columns
   * @param {Object} category - Category info from detectCategory
   * @returns {Object} Schema mapping
   */
  buildSchema(category) {
    const mapping = this.categoryMappings[category.id];
    
    if (!mapping) {
      // Return generic schema for unknown categories
      return this.buildGenericSchema(category);
    }

    return {
      ...mapping,
      categoryId: category.id,
      categoryName: category.name,
      fields: category.fields
    };
  }

  /**
   * Build generic schema for categories without specific mappings
   * @param {Object} category - Category info
   * @returns {Object} Generic schema
   */
  buildGenericSchema(category) {
    return {
      table: 'gear',
      category: this.normalizeCategoryName(category.name),
      subcategory: null,
      categoryId: category.id,
      categoryName: category.name,
      fields: category.fields,
      fieldMappings: this.buildGenericFieldMappings(category.fields)
    };
  }

  /**
   * Normalize category name for database storage
   * @param {string} name - Category name
   * @returns {string} Normalized name
   */
  normalizeCategoryName(name) {
    return name
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  }

  /**
   * Build generic field mappings
   * @param {Array} fields - Field names
   * @returns {Object} Field mappings
   */
  buildGenericFieldMappings(fields) {
    const mappings = {};
    
    fields.forEach((field, index) => {
      const normalized = this.normalizeFieldName(field);
      mappings[index] = {
        source: field,
        target: normalized,
        type: this.inferFieldType(field)
      };
    });
    
    return mappings;
  }

  /**
   * Normalize field name for database column
   * @param {string} name - Field name
   * @returns {string} Normalized name
   */
  normalizeFieldName(name) {
    return name
      .toLowerCase()
      .replace(/\$/g, '')
      .replace(/[^a-z0-9]+/g, '_')
      .replace(/^_+|_+$/g, '');
  }

  /**
   * Infer field type from field name
   * @param {string} fieldName - Field name
   * @returns {string} Field type
   */
  inferFieldType(fieldName) {
    const lower = fieldName.toLowerCase();
    
    if (lower.includes('cost') || lower.includes('price')) return 'cost';
    if (lower.includes('availability')) return 'availability';
    if (lower.includes('weight')) return 'number';
    if (lower.includes('damage')) return 'damage';
    if (lower.includes('rating')) return 'number';
    if (lower.includes('conceal')) return 'number';
    if (lower.includes('index')) return 'number';
    
    return 'string';
  }

  /**
   * Build category mappings for all known categories
   * Maps category IDs to database schemas
   * @returns {Object} Category mappings
   */
  buildCategoryMappings() {
    return {
      // Category 1: Edged weapons (already loaded via weapons system)
      1: {
        table: 'gear',
        category: 'weapon',
        subcategory: 'edged_weapon'
      },
      
      // Category 2: Bows and crossbows (already loaded)
      2: {
        table: 'gear',
        category: 'weapon',
        subcategory: 'bow_crossbow'
      },
      
      // Category 3: Firearms (already loaded)
      3: {
        table: 'gear',
        category: 'weapon',
        subcategory: 'firearm'
      },
      
      // Category 4: Rockets and Missiles
      4: {
        table: 'gear',
        category: 'weapon',
        subcategory: 'rocket_missile'
      },
      
      // Category 5: Ammunition
      5: {
        table: 'gear',
        category: 'ammunition',
        subcategory: null
      },
      
      // Category 6: Firearms Accessories
      6: {
        table: 'gear',
        category: 'accessory',
        subcategory: 'firearm_accessory'
      },
      
      // Category 7: Explosives
      7: {
        table: 'gear',
        category: 'explosive',
        subcategory: null
      },
      
      // Category 8: Clothing and Armor
      8: {
        table: 'gear',
        category: 'armor',
        subcategory: null
      },
      
      // Category 9: S+S Vision Enhancers
      9: {
        table: 'gear',
        category: 'accessory',
        subcategory: 'vision_enhancer'
      },
      
      // Category 10: Surveillance and Security
      10: {
        table: 'gear',
        category: 'security',
        subcategory: 'surveillance'
      },
      
      // Category 11: Cyberdecks
      11: {
        table: 'gear',
        category: 'cyberdeck',
        subcategory: null
      },
      
      // Category 12: Cyberdeck Other
      12: {
        table: 'gear',
        category: 'cyberdeck',
        subcategory: 'accessory'
      },
      
      // Category 13: Biotech
      13: {
        table: 'gear',
        category: 'biotech',
        subcategory: null
      },
      
      // Category 14: Lifestyle
      14: {
        table: 'gear',
        category: 'lifestyle',
        subcategory: null
      },
      
      // Category 15: Magical Equipment (partially loaded)
      15: {
        table: 'gear',
        category: 'magical',
        subcategory: 'equipment'
      },
      
      // Category 16: Extras
      16: {
        table: 'gear',
        category: 'misc',
        subcategory: 'extras'
      },
      
      // Category 17: Cars (partially loaded as vehicles)
      17: {
        table: 'gear',
        category: 'vehicle',
        subcategory: 'car'
      },
      
      // Category 18: Vehicle gear
      18: {
        table: 'gear',
        category: 'vehicle',
        subcategory: 'gear'
      },
      
      // Category 19: Vehicle weapons
      19: {
        table: 'gear',
        category: 'vehicle',
        subcategory: 'weapon'
      },
      
      // Category 20: Chips
      20: {
        table: 'gear',
        category: 'chip',
        subcategory: null
      },
      
      // Category 21: Stuff With Ratings
      21: {
        table: 'gear',
        category: 'misc',
        subcategory: 'rated_items'
      },
      
      // Category 22: Drugs
      22: {
        table: 'gear',
        category: 'drug',
        subcategory: null
      },
      
      // Category 23: Vehicle modifications
      23: {
        table: 'gear',
        category: 'vehicle',
        subcategory: 'modification'
      }
    };
  }

  /**
   * Get all category IDs that should be imported
   * @param {Array} options.skip - Category IDs to skip
   * @param {Array} options.only - Only import these category IDs
   * @returns {Array} Category IDs to import
   */
  getCategoriesToImport(options = {}) {
    const { skip = [], only = null } = options;
    
    const allCategories = Object.keys(this.categoryMappings).map(id => parseInt(id));
    
    if (only) {
      return only.filter(id => !skip.includes(id));
    }
    
    return allCategories.filter(id => !skip.includes(id));
  }
}
