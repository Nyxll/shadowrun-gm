# Tool Inventory - Complete Analysis

**Generated:** 2025-10-29 00:40:03

## Summary

- **Total Tools:** 268
- **Total Lines:** 34,411
- **Categories:** 7

### By Category

| Category | Count | Percentage | Avg Lines |
|----------|-------|------------|----------|
| check | 110 | 41.0% | 60 |
| fix | 44 | 16.4% | 88 |
| test | 41 | 15.3% | 83 |
| other | 33 | 12.3% | 155 |
| generate | 20 | 7.5% | 232 |
| import | 16 | 6.0% | 609 |
| analyze | 4 | 1.5% | 256 |

### By Status

| Status | Count | Percentage |
|--------|-------|------------|
| active | 256 | 95.5% |
| versioned | 12 | 4.5% |

## Detailed Listings

### ANALYZE Tools (4 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| compare-character-sheets.py | 113 | 7 | active | - |
| compare-gpt-models.py | 407 | 23 | active | json |
| compare-llms.py | 388 | 23 | active | json |
| compare-weapons.py | 117 | 12 | active | database, json, env |

### CHECK Tools (110 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| audit-all-operations.py | 101 | 0 | active | - |
| audit-schema-compliance.py | 139 | 0 | active | - |
| audit-schema-reads.py | 106 | 0 | active | - |
| check-all-character-gear.py | 70 | 6 | active | env |
| check-all-character-modifiers.py | 56 | 8 | active | json, env |
| check-all-edges-flaws.py | 41 | 7 | active | json, http |
| check-all-schemas.py | 67 | 1 | active | env |
| check-all-uuids.py | 131 | 1 | active | env |
| check-api-gear.py | 8 | 6 | active | json |
| check-api-response.py | 28 | 0 | active | json, http |
| check-attribute-columns.py | 40 | 0 | active | env |
| check-barrett.py | 43 | 8 | active | json, env |
| check-bioware-costs.py | 41 | 7 | active | json, env |
| check-block-attrs.py | 41 | 6 | active | env |
| check-campaign-schema.py | 30 | 3 | active | database, env |
| check-categories.py | 32 | 14 | active | database, env |
| check-character-columns.py | 48 | 8 | active | env |
| check-character-data-completeness.py | 87 | 7 | active | env |
| check-character-id-type.py | 47 | 1 | active | env |
| check-character-schema.py | 30 | 2 | active | database, env |
| check-character-tables.py | 34 | 1 | active | env |
| check-characters-schema.py | 31 | 0 | active | env |
| check-characters.py | 50 | 9 | active | database, env |
| check-combat-pool-modifiers.py | 63 | 4 | active | database, env |
| check-contacts-schema.py | 29 | 7 | active | env |
| check-content-types-final.py | 50 | 15 | active | database, env |
| check-content-types.py | 57 | 15 | active | database, env |
| check-current-modifiers.py | 33 | 8 | active | env |
| check-cyberdecks.py | 66 | 4 | active | database, env |
| check-cyberware-essence.py | 41 | 7 | active | json, env |
| check-cyberware-structure.py | 36 | 0 | active | lib, env |
| check-db-schema.py | 74 | 8 | active | env |
| check-duplicates-remote.py | 95 | 9 | active | http, env |
| check-duplicates.py | 74 | 15 | active | database, env |
| check-edges-flaws.py | 77 | 1 | active | env |
| check-enrichment-sources.py | 79 | 7 | active | env |
| check-existing-tables.py | 61 | 14 | active | database, env |
| check-gear-chunks.py | 63 | 14 | active | database, env |
| check-gear-duplicates.py | 137 | 12 | active | database, env |
| check-gear-sections.py | 37 | 6 | active | - |
| check-gear-status.py | 95 | 14 | active | database, env |
| check-gear-types.py | 42 | 6 | active | env |
| check-house-rules-schema.py | 32 | 8 | active | env |
| check-line-234.py | 5 | 6 | active | - |
| check-magic-characters.py | 80 | 1 | active | env |
| check-manticore-all-modifiers.py | 60 | 6 | active | database, env |
| check-manticore-api-response.py | 100 | 6 | active | json, env |
| check-manticore-cyberware-names.py | 33 | 6 | active | env |
| check-manticore-gear.py | 34 | 8 | active | env |
| check-manticore-modifiers.py | 66 | 6 | active | env |
| check-manticore.py | 35 | 8 | active | env |
| check-math-spu.py | 73 | 6 | active | env |
| check-mcp-lookups.py | 39 | 0 | active | - |
| check-modifier-columns.py | 29 | 4 | active | database, env |
| check-modifier-data.py | 28 | 6 | active | env |
| check-modifier-descriptions.py | 48 | 6 | active | database, json, env |
| check-modifiers-columns.py | 32 | 7 | active | env |
| check-modifiers-table.py | 44 | 0 | active | env |
| check-oak-magic-fields.py | 78 | 2 | active | database, env |
| check-oak-totem.py | 34 | 0 | active | env |
| check-orphaned-modifiers.py | 44 | 6 | active | env |
| check-platinum-bioware.py | 68 | 6 | active | env |
| check-platinum-combat-pool.py | 33 | 4 | active | database, env |
| check-platinum-cyberware-v2.py | 71 | 8 | versioned | env |
| check-platinum-cyberware.py | 36 | 8 | active | env |
| check-platinum-edges-flaws.py | 15 | 7 | active | json, http |
| check-platinum-gear.py | 29 | 6 | active | env |
| check-platinum-import.py | 122 | 7 | active | env |
| check-platinum-name.py | 80 | 4 | active | database, env |
| check-platinum-skill-modifiers.py | 66 | 3 | active | env |
| check-platinum-vehicles.py | 67 | 4 | active | database, env |
| check-platinum-weapons.py | 63 | 8 | active | json, env |
| check-powers-migration-status.py | 64 | 0 | active | database, env |
| check-rag-tables.py | 29 | 7 | active | env |
| check-schema-types.py | 46 | 3 | active | database, env |
| check-schema.py | 30 | 8 | active | env |
| check-spell-category.py | 32 | 2 | active | env |
| check-spell-force.py | 99 | 1 | active | env |
| check-spells-foci-tables.py | 64 | 3 | active | env |
| check-system-status.py | 152 | 7 | active | http, env |
| check-table-columns.py | 35 | 1 | active | env |
| check-table-schema.py | 69 | 1 | active | env |
| check-table-schemas.py | 46 | 7 | active | env |
| check-tables.py | 91 | 15 | active | database, env |
| check-tailored-pheromones.py | 51 | 6 | active | env |
| check-totem-columns.py | 28 | 0 | active | env |
| check-totem-opposed.py | 168 | 2 | active | database, env |
| check-vehicles-imported.py | 60 | 6 | active | env |
| check-vehicles-in-files.py | 33 | 6 | active | - |
| check-vision-modifiers.py | 90 | 6 | active | database, env |
| check-weapon-data.py | 41 | 8 | active | json, env |
| find-bioware.py | 23 | 7 | active | - |
| find-effects-code.py | 9 | 6 | active | - |
| find-skill-updates.py | 27 | 0 | active | - |
| inspect-roleplay-data.py | 33 | 9 | active | json |
| inspect-xai-data.py | 45 | 9 | active | json |
| show-duplicate-examples.py | 79 | 15 | active | database, env |
| show-gear-examples.py | 67 | 14 | active | database, env |
| show-update-skill-method.py | 26 | 0 | active | - |
| verify-actual-schema.py | 91 | 1 | active | env |
| verify-all-modifiers.py | 62 | 8 | active | env |
| verify-all-types.py | 39 | 9 | active | - |
| verify-body-index.py | 91 | 6 | active | env |
| verify-character-imports.py | 70 | 10 | active | database, json, env |
| verify-complete-import.py | 303 | 7 | active | env |
| verify-database.py | 138 | 23 | active | database, env |
| verify-game-server-fixes.py | 53 | 0 | active | - |
| verify-modifiers.py | 43 | 8 | active | env |
| verify-spell-modifiers.py | 52 | 8 | active | env |
| verify-tables-ready.py | 79 | 1 | active | env |

### FIX Tools (44 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| apply-audit-migration.py | 117 | 1 | active | env |
| apply-body-index-migration.py | 74 | 6 | active | env |
| apply-campaign-migration.py | 80 | 3 | active | database, env |
| apply-character-schema.py | 79 | 14 | active | database, env |
| apply-characters-v2-schema.py | 68 | 8 | active | env |
| apply-complete-schema.py | 121 | 7 | active | env |
| apply-edges-flaws-cost-migration.py | 50 | 1 | active | env |
| apply-magic-fields-migration.py | 56 | 2 | active | database, env |
| apply-migration.py | 60 | 0 | active | database, env |
| apply-missing-modifiers.py | 42 | 8 | active | env |
| apply-modifier-fixes.py | 42 | 8 | active | env |
| apply-powers-uuid-migration.py | 45 | 0 | active | env |
| apply-schema-v5.py | 42 | 6 | versioned | env |
| apply-spell-force-migration.py | 60 | 1 | active | env |
| apply-spells-foci-migration.py | 56 | 3 | active | env |
| apply-totem-migration.py | 84 | 3 | active | env |
| ensure-system-user.py | 84 | 1 | active | env |
| fix-all-remaining.py | 39 | 9 | active | - |
| fix-all-schema-mismatches.py | 121 | 0 | active | - |
| fix-all-test-issues.py | 88 | 0 | active | env |
| fix-all-type-mismatches.py | 108 | 9 | active | - |
| fix-all-vehicle-stats.py | 142 | 4 | active | database, json, env |
| fix-campaign-schema.py | 77 | 3 | active | database, env |
| fix-cyberware-bioware-ui.py | 210 | 0 | active | - |
| fix-foreign-key-constraints.py | 94 | 8 | active | env |
| fix-game-server.py | 91 | 0 | active | - |
| fix-levels-jsonb.py | 42 | 9 | active | - |
| fix-manticore-math-spu.py | 114 | 6 | active | env |
| fix-mcp-operations-encoding.py | 15 | 0 | active | - |
| fix-mcp-operations.py | 18 | 0 | active | - |
| fix-metatypes-now.py | 27 | 9 | active | - |
| fix-platinum-cyberware-costs.py | 87 | 7 | active | json, env |
| fix-platinum-vehicle-stats.py | 128 | 4 | active | database, env |
| fix-renderer-file.py | 111 | 0 | active | - |
| fix-split-files.py | 57 | 9 | active | - |
| fix-test-unicode.py | 62 | 0 | active | - |
| fix-type-mismatches.py | 75 | 9 | active | - |
| fix-types-properly.py | 82 | 9 | active | - |
| fix-users-table.py | 89 | 1 | active | env |
| migrate-foreign-keys-to-uuid.py | 328 | 8 | active | env |
| migrate-platinum-modifiers.py | 162 | 8 | active | env |
| migrate-spells-foci-v2.py | 146 | 3 | versioned | env |
| rebuild-cyber-bio-functions-fixed.py | 97 | 0 | active | - |
| rebuild-cyber-bio-functions.py | 96 | 0 | active | - |

### GENERATE Tools (20 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| add-all-phases-to-gameserver.py | 428 | 0 | active | - |
| add-comprehensive-logging.py | 106 | 0 | active | - |
| add-cyberware-modifiers.py | 326 | 8 | active | env |
| add-final-tool-defs.py | 356 | 0 | active | - |
| add-missing-platinum-modifiers.py | 67 | 6 | active | env |
| add-phase1-to-gameserver.py | 156 | 0 | active | - |
| add-platinum-smartlink-3.py | 191 | 8 | active | env |
| add-spell-force-values.py | 120 | 1 | active | env |
| add-spell-timing.py | 76 | 3 | active | - |
| create-test-shaman.py | 84 | 1 | active | env |
| create-user-functions.py | 88 | 1 | active | env |
| export-actual-schema.py | 136 | 1 | active | env |
| export-character-sheets.py | 332 | 8 | active | json, env |
| export-to-v1-gemini-format.py | 522 | 7 | active | env |
| export-to-v1-markdown.py | 313 | 7 | active | env |
| generate-character-tests.py | 146 | 7 | active | env |
| generate-phases-4-5-6-defs.py | 496 | 0 | active | - |
| generate-remaining-tool-defs.py | 461 | 0 | active | - |
| generate-totem-inserts-v2.py | 137 | 3 | versioned | - |
| generate-totem-inserts.py | 98 | 3 | active | - |

### IMPORT Tools (16 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| import-all-spells.py | 25 | 3 | active | - |
| import-character-sheets.py | 795 | 8 | active | json, env |
| import-characters-complete.py | 662 | 7 | active | env |
| import-characters-enhanced.py | 333 | 8 | active | env |
| import-characters-v10.py | 1243 | 1 | versioned | env |
| import-characters-v11.py | 359 | 1 | versioned | lib, env |
| import-characters-v6.py | 1090 | 6 | versioned | env |
| import-characters-v7.py | 1116 | 6 | versioned | env |
| import-characters-v8.py | 1116 | 3 | versioned | env |
| import-characters-v9.py | 1232 | 2 | versioned | env |
| import-characters.py | 520 | 10 | active | database, json, env |
| import-cyberdecks.py | 208 | 4 | active | database, json, env |
| import-historical-campaigns.py | 425 | 9 | active | database, json, env |
| import-master-spells.py | 140 | 0 | active | database, env |
| import-platinum-complete.py | 282 | 7 | active | json, env |
| import-training-corpus.py | 193 | 9 | active | database, json, env |

### OTHER Tools (33 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| analyze-gm-patterns.py | 263 | 9 | active | database, env |
| calculate-platinum-shot.py | 130 | 8 | active | lib |
| check_columns.py | 26 | 14 | active | database, env |
| check_db_config.py | 11 | 14 | active | env |
| check_schemas.py | 35 | 14 | active | database, env |
| clean-and-reload-characters.py | 93 | 7 | active | env |
| clean-duplicate-smartlinks.py | 98 | 8 | active | env |
| clean-gear-sections.py | 59 | 8 | active | env |
| diagnose-test-failures.py | 67 | 0 | active | env |
| enhance-character-modifiers.py | 75 | 8 | active | env |
| enrich-character-data.py | 340 | 7 | active | env |
| enrich-from-database.py | 272 | 7 | active | json, env |
| expand-mcp-operations.py | 171 | 0 | active | - |
| extract_reference_data.py | 486 | 14 | active | database, json, env |
| final-type-fix.py | 63 | 9 | active | - |
| gear_loader.py | 570 | 14 | active | database, json, env |
| insert-via-api.py | 161 | 9 | active | database, json, http, env |
| link-oak-spells.py | 76 | 0 | active | env |
| list-all-files.py | 40 | 15 | active | database, env |
| list-characters.py | 28 | 8 | active | env |
| load_csv_data.py | 231 | 14 | active | database, env |
| load_dat_files.py | 384 | 13 | active | database, json, env |
| quick-crud-test.py | 88 | 0 | active | lib, env |
| reimport-characters.py | 31 | 6 | active | env |
| remove-duplicates.py | 127 | 15 | active | database, env |
| resplit-to-980kb.py | 90 | 9 | active | - |
| roll-platinum-attack.py | 90 | 8 | active | lib |
| safe-cleanup-test-data.py | 121 | 0 | active | env |
| training-processor.py | 500 | 9 | active | database, json, env |
| update-all-combat-pools.py | 80 | 4 | active | database, env |
| update-modifier-descriptions.py | 241 | 6 | active | database, env |
| update-oak-opposed.py | 42 | 2 | active | env |
| update-platinum-combat-pool.py | 38 | 4 | active | database, env |

### TEST Tools (41 files)

| Filename | Lines | Age (days) | Status | Dependencies |
|----------|-------|------------|--------|-------------|
| debug-bioware-parse.py | 54 | 6 | active | - |
| debug-gear-regex.py | 25 | 6 | active | - |
| debug-parent-child-structure.py | 54 | 6 | active | env |
| test-all-characters.py | 100 | 4 | active | json, http |
| test-all-patterns.py | 29 | 9 | active | - |
| test-api-cyberware-format.py | 24 | 6 | active | json, http |
| test-api-debug.py | 17 | 6 | active | json, http |
| test-api-endpoint.py | 29 | 0 | active | json, http |
| test-api-response.py | 22 | 7 | active | json, http |
| test-bioware-parse.py | 64 | 7 | active | - |
| test-bioware-parsing.py | 61 | 7 | active | - |
| test-character-api.py | 91 | 6 | active | json, http |
| test-character-sheet-display.py | 152 | 0 | active | json |
| test-cyberdeck-api.py | 48 | 4 | active | json, http |
| test-cyberware-display.py | 58 | 0 | active | lib |
| test-db-connection.py | 44 | 1 | active | env |
| test-edge-parse.py | 50 | 7 | active | - |
| test-gear-contacts.py | 56 | 7 | active | env |
| test-jsonb-type.py | 35 | 6 | active | env |
| test-manticore-bioware-api.py | 58 | 6 | active | json, http |
| test-manticore-shot.py | 151 | 8 | active | env |
| test-mcp-platinum-shot.py | 124 | 8 | active | env |
| test-metatype-pattern.py | 28 | 9 | active | - |
| test-migration-021.py | 54 | 0 | active | database, env |
| test-pattern.py | 20 | 9 | active | - |
| test-platinum-api-bioware.py | 19 | 4 | active | json, http |
| test-platinum-shot-final.py | 81 | 8 | active | json, lib, env |
| test-platinum-shot-v2.py | 236 | 8 | versioned | lib, env |
| test-reimport-platinum.py | 94 | 6 | active | env |
| test-section-parse.py | 15 | 7 | active | - |
| test-server-import.py | 24 | 0 | active | - |
| test-spell-with-timing.py | 365 | 3 | active | json, lib, env |
| test-spellcasting-v2.py | 348 | 3 | versioned | lib, env |
| test-spellcasting.py | 122 | 4 | active | env |
| test-telemetry.py | 116 | 3 | active | - |
| test-ui-character-load.py | 131 | 7 | active | json, http |
| test-ui-debug.py | 50 | 0 | active | - |
| test-ui-quick.py | 53 | 0 | active | http |
| test-unparsed-modifiers.py | 189 | 6 | active | - |
| test-v3-import.py | 94 | 7 | active | env |
| test-vehicle-api.py | 18 | 4 | active | http |

## Consolidation Recommendations

### Versioned Files (12 files)

These files have version suffixes (e.g., -v6, -v7) and should be consolidated:

**apply-schema**: 1 versions
  - apply-schema-v5.py (42 lines, 6 days old)

**check-platinum-cyberware**: 1 versions
  - check-platinum-cyberware-v2.py (71 lines, 8 days old)

**generate-totem-inserts**: 1 versions
  - generate-totem-inserts-v2.py (137 lines, 3 days old)

**import-characters**: 6 versions
  - import-characters-v10.py (1243 lines, 1 days old)
  - import-characters-v11.py (359 lines, 1 days old)
  - import-characters-v6.py (1090 lines, 6 days old)
  - import-characters-v7.py (1116 lines, 6 days old)
  - import-characters-v8.py (1116 lines, 3 days old)
  - import-characters-v9.py (1232 lines, 2 days old)

**migrate-spells-foci**: 1 versions
  - migrate-spells-foci-v2.py (146 lines, 3 days old)

**test-platinum-shot**: 1 versions
  - test-platinum-shot-v2.py (236 lines, 8 days old)

**test-spellcasting**: 1 versions
  - test-spellcasting-v2.py (348 lines, 3 days old)

### Consolidation Targets

**IMPORT**: 16 files → 3 files
  - import_characters.py
  - import_spells.py
  - import_gear.py

**CHECK**: 110 files → 6 files
  - check_schema.py
  - check_characters.py
  - check_modifiers.py
  - check_magic.py
  - check_gear.py
  - verify_integrity.py

**FIX**: 44 files → 5 files
  - apply_migration.py
  - fix_schema.py
  - fix_data.py
  - cleanup_test_data.py
  - ensure_system.py

**GENERATE**: 20 files → 4 files
  - generate_tool_defs.py
  - export_characters.py
  - process_training.py
  - generate_reports.py

