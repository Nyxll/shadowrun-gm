#!/usr/bin/env node
/**
 * PHASE 1 - STEP 1.5: Universal GEAR.DAT Parser
 * 
 * Combines CategoryDetector, FieldParser, and DatabaseImporter
 * to parse GEAR.DAT files and import data into PostgreSQL.
 */

import fs from 'fs';
import { CategoryDetector } from './category-detector.js';
import { FieldParser } from './field-parser.js';
import { DatabaseImporter } from './database-importer.js';

export class GearDatParser {
  constructor(dbConfig) {
    this.detector = new CategoryDetector();
    this.parser = new FieldParser();
    this.importer = new DatabaseImporter(dbConfig);
  }

  /**
   * Parse GEAR.DAT file and import to database
   * @param {string} filePath - Path to GEAR.DAT file
   * @param {Object} options - Import options
   * @returns {Object} Import results
   */
  async parseAndImport(filePath, options = {}) {
    const {
      skipDuplicates = true,
      updateExisting = false,
      dryRun = false,
      categoriesFilter = null, // Array of category IDs to import, null = all
      verbose = false
    } = options;

    console.log(`\n${'='.repeat(80)}`);
    console.log('GEAR.DAT PARSER - Universal Import Tool');
    console.log('='.repeat(80));
    console.log(`File: ${filePath}`);
    console.log(`Mode: ${dryRun ? 'DRY RUN' : 'LIVE IMPORT'}`);
    console.log(`Skip Duplicates: ${skipDuplicates}`);
    console.log(`Update Existing: ${updateExisting}`);
    if (categoriesFilter) {
      console.log(`Categories Filter: ${categoriesFilter.join(', ')}`);
    }
    console.log('='.repeat(80));
    console.log();

    // Read file
    const content = fs.readFileSync(filePath, 'utf-8');
    const lines = content.split('\n').map(line => line.trim());

    console.log(`Total lines: ${lines.length}`);
    console.log();

    // Parse file structure
    const structure = this.parseFileStructure(lines);
    
    console.log(`Categories found: ${structure.categories.length}`);
    console.log();

    // Import results
    const results = {
      totalCategories: 0,
      processedCategories: 0,
      skippedCategories: 0,
      totalItems: 0,
      inserted: 0,
      updated: 0,
      skipped: 0,
      errors: [],
      categoryResults: []
    };

    // Process each category
    for (const category of structure.categories) {
      results.totalCategories++;

      // Apply category filter if specified
      if (categoriesFilter && !categoriesFilter.includes(category.id)) {
        results.skippedCategories++;
        if (verbose) {
          console.log(`⊘ Skipping category ${category.id}: ${category.name} (filtered)`);
        }
        continue;
      }

      console.log(`\n${'─'.repeat(80)}`);
      console.log(`Processing Category ${category.id}: ${category.name}`);
      console.log(`Items: ${category.items.length} | Fields: ${category.fieldCount}`);
      console.log('─'.repeat(80));

      try {
        // Build schema for this category
        const schema = this.detector.buildSchema(category);

        if (verbose) {
          console.log(`Schema: ${JSON.stringify(schema, null, 2)}`);
        }

        // Parse items
        const parseResult = this.parser.parseItems(category.items, schema);

        console.log(`Parsed: ${parseResult.stats.parsed}/${parseResult.stats.total} items`);
        if (parseResult.stats.failed > 0) {
          console.log(`⚠ Parse failures: ${parseResult.stats.failed}`);
        }

        // Import to database
        const importResult = await this.importer.importItems(
          parseResult.items,
          schema,
          { skipDuplicates, updateExisting, dryRun }
        );

        console.log(`✓ Inserted: ${importResult.inserted}`);
        console.log(`✓ Updated: ${importResult.updated}`);
        console.log(`⊘ Skipped: ${importResult.skipped}`);
        if (importResult.errors.length > 0) {
          console.log(`✗ Errors: ${importResult.errors.length}`);
        }

        // Update totals
        results.processedCategories++;
        results.totalItems += parseResult.stats.total;
        results.inserted += importResult.inserted;
        results.updated += importResult.updated;
        results.skipped += importResult.skipped;
        results.errors.push(...importResult.errors);

        // Store category result
        results.categoryResults.push({
          id: category.id,
          name: category.name,
          itemCount: category.items.length,
          parsed: parseResult.stats.parsed,
          inserted: importResult.inserted,
          updated: importResult.updated,
          skipped: importResult.skipped,
          errors: importResult.errors.length
        });

        // Show errors if verbose
        if (verbose && importResult.errors.length > 0) {
          console.log('\nErrors:');
          importResult.errors.forEach(err => {
            console.log(`  - ${err.item}: ${err.error}`);
          });
        }

      } catch (error) {
        console.error(`✗ Error processing category ${category.id}: ${error.message}`);
        results.errors.push({
          category: category.name,
          error: error.message
        });
      }
    }

    // Print summary
    console.log(`\n${'='.repeat(80)}`);
    console.log('IMPORT SUMMARY');
    console.log('='.repeat(80));
    console.log(`Categories: ${results.processedCategories}/${results.totalCategories} processed`);
    if (results.skippedCategories > 0) {
      console.log(`           ${results.skippedCategories} skipped (filtered)`);
    }
    console.log(`Total Items: ${results.totalItems}`);
    console.log(`✓ Inserted: ${results.inserted}`);
    console.log(`✓ Updated: ${results.updated}`);
    console.log(`⊘ Skipped: ${results.skipped}`);
    console.log(`✗ Errors: ${results.errors.length}`);
    console.log('='.repeat(80));

    // Category breakdown
    if (results.categoryResults.length > 0) {
      console.log('\nCategory Breakdown:');
      console.log('─'.repeat(80));
      console.log('ID | Category Name                | Items | Inserted | Updated | Skipped | Errors');
      console.log('─'.repeat(80));
      
      for (const cat of results.categoryResults) {
        const name = cat.name.padEnd(28);
        console.log(
          `${String(cat.id).padStart(2)} | ${name} | ` +
          `${String(cat.itemCount).padStart(5)} | ` +
          `${String(cat.inserted).padStart(8)} | ` +
          `${String(cat.updated).padStart(7)} | ` +
          `${String(cat.skipped).padStart(7)} | ` +
          `${String(cat.errors).padStart(6)}`
        );
      }
      console.log('─'.repeat(80));
    }

    // Show errors summary
    if (results.errors.length > 0 && !verbose) {
      console.log(`\n⚠ ${results.errors.length} errors occurred. Run with --verbose to see details.`);
    }

    console.log();

    return results;
  }

  /**
   * Parse GEAR.DAT file structure
   * @param {Array} lines - File lines
   * @returns {Object} File structure
   */
  parseFileStructure(lines) {
    // First pass: collect all category headers
    const categoryMap = new Map();
    
    for (const line of lines) {
      if (!line) continue;
      
      const categoryInfo = this.detector.detectCategory(line);
      if (categoryInfo) {
        categoryMap.set(categoryInfo.id, {
          id: categoryInfo.id,
          name: categoryInfo.name,
          fieldCount: categoryInfo.fieldCount,
          fields: categoryInfo.fields,
          items: []
        });
      }
    }

    // Second pass: collect all items and assign to categories based on their category ID
    for (const line of lines) {
      if (!line || !this.parser.isItemLine(line)) continue;
      
      // Extract category ID from item line
      // Format: 4-* {name} {categoryId}|...
      const match = line.match(/4-\*\s+.+?\s+(\d+)\|/);
      if (match) {
        const categoryId = parseInt(match[1]);
        const category = categoryMap.get(categoryId);
        
        if (category) {
          category.items.push(line);
        } else {
          console.warn(`Warning: Item references unknown category ${categoryId}: ${line.substring(0, 50)}...`);
        }
      }
    }

    // Convert map to array
    const categories = Array.from(categoryMap.values());
    
    return { categories };
  }

  /**
   * Get import statistics from database
   * @param {string} category - Optional category filter
   * @returns {Array} Statistics
   */
  async getStats(category = null) {
    return await this.importer.getImportStats(category);
  }

  /**
   * Close database connection
   */
  async close() {
    await this.importer.close();
  }
}

/**
 * CLI entry point
 */
async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help')) {
    console.log(`
GEAR.DAT Parser - Universal Import Tool

Usage:
  node gear-dat-parser.js <file> [options]

Options:
  --dry-run              Validate without importing
  --update               Update existing items
  --no-skip-duplicates   Don't skip duplicates (requires --update)
  --categories <ids>     Only import specific categories (comma-separated)
  --verbose              Show detailed output
  --stats [category]     Show import statistics
  --help                 Show this help

Database Configuration:
  Set via environment variables:
    POSTGRES_HOST     (default: localhost)
    POSTGRES_PORT     (default: 5432)
    POSTGRES_USER     (default: postgres)
    POSTGRES_PASSWORD (required)
    POSTGRES_DB       (default: postgres)

Examples:
  # Dry run to validate
  node gear-dat-parser.js GEAR.DAT --dry-run

  # Import all categories
  node gear-dat-parser.js GEAR.DAT

  # Import only weapons (category 3)
  node gear-dat-parser.js GEAR.DAT --categories 3

  # Import armor and weapons (categories 8,3)
  node gear-dat-parser.js GEAR.DAT --categories 8,3

  # Update existing items
  node gear-dat-parser.js GEAR.DAT --update

  # Show statistics
  node gear-dat-parser.js --stats
  node gear-dat-parser.js --stats weapon
`);
    process.exit(0);
  }

  // Parse arguments
  const filePath = args[0];
  const dryRun = args.includes('--dry-run');
  const updateExisting = args.includes('--update');
  const skipDuplicates = !args.includes('--no-skip-duplicates');
  const verbose = args.includes('--verbose');
  const showStats = args.includes('--stats');

  let categoriesFilter = null;
  const categoriesIndex = args.indexOf('--categories');
  if (categoriesIndex !== -1 && args[categoriesIndex + 1]) {
    categoriesFilter = args[categoriesIndex + 1].split(',').map(id => parseInt(id.trim()));
  }

  // Database configuration
  const dbConfig = {
    host: process.env.POSTGRES_HOST || 'localhost',
    port: parseInt(process.env.POSTGRES_PORT || '5432'),
    user: process.env.POSTGRES_USER || 'postgres',
    password: process.env.POSTGRES_PASSWORD,
    database: process.env.POSTGRES_DB || 'postgres',
    max: 20,
    idleTimeoutMillis: 30000,
    connectionTimeoutMillis: 2000,
  };

  if (!dbConfig.password) {
    console.error('Error: POSTGRES_PASSWORD environment variable is required');
    process.exit(1);
  }

  // Create parser
  const parser = new GearDatParser(dbConfig);

  try {
    if (showStats) {
      // Show statistics
      const category = args[args.indexOf('--stats') + 1];
      const stats = await parser.getStats(category);
      
      console.log('\nImport Statistics:');
      console.log('─'.repeat(80));
      console.log('Category                     | Subcategory              | Count');
      console.log('─'.repeat(80));
      
      for (const stat of stats) {
        const cat = (stat.category || '').padEnd(28);
        const sub = (stat.subcategory || '-').padEnd(24);
        console.log(`${cat} | ${sub} | ${stat.count}`);
      }
      console.log('─'.repeat(80));
      
      const total = stats.reduce((sum, s) => sum + parseInt(s.count), 0);
      console.log(`Total: ${total} items\n`);
    } else {
      // Parse and import
      if (!fs.existsSync(filePath)) {
        console.error(`Error: File not found: ${filePath}`);
        process.exit(1);
      }

      const results = await parser.parseAndImport(filePath, {
        skipDuplicates,
        updateExisting,
        dryRun,
        categoriesFilter,
        verbose
      });

      // Exit with error code if there were errors
      if (results.errors.length > 0) {
        process.exit(1);
      }
    }
  } catch (error) {
    console.error(`\nFatal error: ${error.message}`);
    if (verbose) {
      console.error(error.stack);
    }
    process.exit(1);
  } finally {
    await parser.close();
  }
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}
