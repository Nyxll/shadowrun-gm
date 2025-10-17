/**
 * PHASE 1 - STEP 1.3: Field Parser
 * 
 * Parses individual item data lines from GEAR.DAT.
 * Item lines follow the format: 3-* {name} {categoryId}|{field1}|{field2}|...
 */

export class FieldParser {
  constructor() {
    this.parsers = this.buildFieldParsers();
  }

  /**
   * Detect if a line is an item data line
   * @param {string} line - Line from GEAR.DAT
   * @returns {boolean} True if item line
   */
  isItemLine(line) {
    const trimmed = line.trim();
    return trimmed.startsWith('4-*');
  }

  /**
   * Parse an item data line
   * @param {string} line - Item line from GEAR.DAT
   * @param {Object} schema - Category schema from CategoryDetector
   * @returns {Object} Parsed item data
   */
  parseItem(line, schema) {
    const trimmed = line.trim();
    
    if (!this.isItemLine(trimmed)) {
      throw new Error('Not an item line');
    }

    // Format: 4-* {name} {categoryId}|{field1}|{field2}|...
    // Example: 4-* Ares Predator II 3|4|10|SA/BF|9M|2.5|5/12hrs|450|1.2|
    
    // Remove "4-* " prefix
    const withoutPrefix = trimmed.substring(4);
    
    // Find the category ID (number before first pipe)
    const firstPipeIndex = withoutPrefix.indexOf('|');
    if (firstPipeIndex === -1) {
      throw new Error('Invalid item format: no pipe separator found');
    }
    
    // Split into name part and data part
    const beforePipe = withoutPrefix.substring(0, firstPipeIndex).trim();
    const afterPipe = withoutPrefix.substring(firstPipeIndex + 1);
    
    // The name is everything except the last token (which is the category ID)
    const tokens = beforePipe.split(/\s+/);
    const categoryId = parseInt(tokens[tokens.length - 1]);
    const name = tokens.slice(0, -1).join(' ').trim();
    
    // Validate category ID matches schema
    if (schema && categoryId !== schema.categoryId) {
      console.warn(`Warning: Category ID mismatch. Expected ${schema.categoryId}, got ${categoryId}`);
    }
    
    // Split remaining fields by pipe
    const fieldValues = afterPipe.split('|');
    
    // Parse each field according to schema
    const parsedData = {
      name: name,
      category_id: categoryId,
      raw_line: trimmed
    };
    
    if (schema && schema.fields) {
      schema.fields.forEach((fieldName, index) => {
        const rawValue = fieldValues[index] || '';
        const fieldType = this.inferFieldType(fieldName);
        const parsedValue = this.parseField(rawValue, fieldType, fieldName);
        
        // Use normalized field name as key
        const normalizedName = this.normalizeFieldName(fieldName);
        parsedData[normalizedName] = parsedValue;
      });
    } else {
      // No schema, just store raw values
      fieldValues.forEach((value, index) => {
        parsedData[`field_${index}`] = value.trim();
      });
    }
    
    return parsedData;
  }

  /**
   * Parse a single field value based on its type
   * @param {string} value - Raw field value
   * @param {string} type - Field type
   * @param {string} fieldName - Field name for context
   * @returns {*} Parsed value
   */
  parseField(value, type, fieldName) {
    const trimmed = value.trim();
    
    if (!trimmed || trimmed === '-' || trimmed === 'N/A') {
      return null;
    }
    
    const parser = this.parsers[type];
    if (parser) {
      try {
        return parser(trimmed, fieldName);
      } catch (error) {
        console.warn(`Warning: Failed to parse ${fieldName} value "${trimmed}": ${error.message}`);
        return trimmed; // Return raw value on parse failure
      }
    }
    
    return trimmed;
  }

  /**
   * Build field type parsers
   * @returns {Object} Map of type to parser function
   */
  buildFieldParsers() {
    return {
      // Cost parser: handles formats like "450", "1,500", "Always"
      cost: (value) => {
        if (value.toLowerCase() === 'always' || value.toLowerCase() === 'varies') {
          return value;
        }
        // Remove commas and parse as number
        const cleaned = value.replace(/,/g, '');
        const num = parseFloat(cleaned);
        return isNaN(num) ? value : num;
      },
      
      // Availability parser: handles formats like "5/12hrs", "Always", "4/3days"
      availability: (value) => {
        if (value.toLowerCase() === 'always') {
          return { rating: 0, time: 'always' };
        }
        
        // Format: {rating}/{time}
        const match = value.match(/^(\d+)\/(.+)$/);
        if (match) {
          return {
            rating: parseInt(match[1]),
            time: match[2].trim()
          };
        }
        
        return value;
      },
      
      // Number parser: handles integers and decimals
      number: (value) => {
        const num = parseFloat(value);
        return isNaN(num) ? value : num;
      },
      
      // Damage parser: handles formats like "9M", "10S", "6L", "(STR+2)M"
      damage: (value) => {
        // Check for special values
        if (value.includes('see rules') || value.includes('Special')) {
          return value;
        }
        
        // Format: {power}{type} or (formula){type}
        const match = value.match(/^(\(?.+?\)?)([MSLPD])$/);
        if (match) {
          return {
            power: match[1],
            type: match[2]
          };
        }
        
        return value;
      },
      
      // String parser: just trim
      string: (value) => {
        return value.trim();
      },
      
      // Mode parser: handles firing modes like "SA", "SA/BF", "SS/SA/BF"
      mode: (value) => {
        return value.split('/').map(m => m.trim());
      },
      
      // Ammunition parser: handles ammo capacity like "10(c)", "30(c)", "belt"
      ammunition: (value) => {
        if (value.toLowerCase() === 'belt' || value.toLowerCase() === 'varies') {
          return value;
        }
        
        const match = value.match(/^(\d+)\(([a-z])\)$/i);
        if (match) {
          return {
            capacity: parseInt(match[1]),
            type: match[2].toLowerCase()
          };
        }
        
        return value;
      }
    };
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
    if (lower.includes('damage')) return 'damage';
    if (lower.includes('mode')) return 'mode';
    if (lower.includes('ammunition') || lower.includes('ammo')) return 'ammunition';
    if (lower.includes('weight')) return 'number';
    if (lower.includes('rating')) return 'number';
    if (lower.includes('conceal')) return 'number';
    if (lower.includes('index')) return 'number';
    if (lower.includes('ballistic')) return 'number';
    if (lower.includes('impact')) return 'number';
    if (lower.includes('reach')) return 'number';
    if (lower.includes('speed')) return 'number';
    if (lower.includes('body')) return 'number';
    if (lower.includes('armor')) return 'number';
    if (lower.includes('handling')) return 'number';
    
    return 'string';
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
   * Validate parsed item data
   * @param {Object} item - Parsed item
   * @param {Object} schema - Category schema
   * @returns {Object} Validation result
   */
  validateItem(item, schema) {
    const errors = [];
    const warnings = [];
    
    // Check required fields
    if (!item.name || item.name.trim().length === 0) {
      errors.push('Item name is required');
    }
    
    if (!item.category_id) {
      errors.push('Category ID is required');
    }
    
    // Check field count matches schema
    if (schema && schema.fields) {
      const expectedFields = schema.fields.length;
      const actualFields = Object.keys(item).filter(k => 
        !['name', 'category_id', 'raw_line'].includes(k)
      ).length;
      
      if (actualFields !== expectedFields) {
        warnings.push(`Field count mismatch: expected ${expectedFields}, got ${actualFields}`);
      }
    }
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Parse multiple items from lines
   * @param {Array} lines - Array of lines
   * @param {Object} schema - Category schema
   * @returns {Array} Array of parsed items
   */
  parseItems(lines, schema) {
    const items = [];
    const parseErrors = [];
    
    lines.forEach((line, index) => {
      if (!this.isItemLine(line)) {
        return;
      }
      
      try {
        const item = this.parseItem(line, schema);
        const validation = this.validateItem(item, schema);
        
        if (validation.valid) {
          items.push(item);
        } else {
          parseErrors.push({
            line: index + 1,
            errors: validation.errors,
            warnings: validation.warnings,
            rawLine: line
          });
        }
      } catch (error) {
        parseErrors.push({
          line: index + 1,
          errors: [error.message],
          warnings: [],
          rawLine: line
        });
      }
    });
    
    return {
      items,
      parseErrors,
      stats: {
        total: lines.filter(l => this.isItemLine(l)).length,
        parsed: items.length,
        failed: parseErrors.length
      }
    };
  }
}
