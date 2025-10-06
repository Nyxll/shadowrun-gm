# Shadowrun GM MCP Server - Implementation Roadmap

## Project Overview
Create an MCP server to query a local Supabase/PostgreSQL database containing Shadowrun 2nd Edition rules, gear information, and setting lore.

---

## Phase 1: Rules System ✅ COMPLETED

### 1.1 Project Setup ✅
- [x] Create project directory structure
- [x] Initialize Node.js project with package.json
- [x] Install dependencies (@modelcontextprotocol/sdk, pg, dotenv)
- [x] Configure .env with Supabase credentials
- [x] Create comprehensive README.md
- [x] Create SETUP.md guide

### 1.2 Database Schema ✅
- [x] Design rules_content table schema
- [x] Add vector embedding support (pgvector)
- [x] Create full-text search indexes
- [x] Create category and tag indexes
- [x] Add timestamp triggers
- [x] Execute schema.sql on database
- [x] Verify table creation

### 1.3 MCP Server Implementation ✅
- [x] Create server.js with MCP SDK
- [x] Implement database connection pooling
- [x] Implement query_rules tool (natural language search)
- [x] Implement explain_mechanic tool (comprehensive explanations)
- [x] Implement list_rule_categories tool (browse categories)
- [x] Add error handling
- [x] Test database connectivity

### 1.4 Testing & Validation ✅
- [x] Create sample-data.sql with 13 test rules
- [x] Load sample data into database
- [x] Verify data insertion (7 categories, 13 rules)
- [x] Test server startup
- [x] Validate query functionality

### 1.5 Documentation ✅
- [x] Write comprehensive README.md
- [x] Create SETUP.md with configuration steps
- [x] Document all three MCP tools
- [x] Add troubleshooting section
- [x] Include usage examples

---

## Phase 2: Data Migration 🔄 NEXT PRIORITY

### 2.1 Assessment & Planning ⏳
- [ ] Analyze existing RAG database structure
- [ ] Identify data sources (which files/collections)
- [ ] Map existing data to rules_content schema
- [ ] Determine embedding strategy (reuse vs regenerate)
- [ ] Plan data transformation pipeline

### 2.2 Migration Script Development ⏳
- [ ] Create migration script (Python or Node.js)
- [ ] Implement data extraction from RAG store
- [ ] Transform data to match schema
  - [ ] Extract titles from content
  - [ ] Categorize rules (combat, magic, matrix, etc.)
  - [ ] Add subcategories
  - [ ] Generate tags
  - [ ] Preserve source file references
- [ ] Handle embeddings
  - [ ] Option A: Copy existing embeddings
  - [ ] Option B: Generate new with OpenAI API
- [ ] Implement batch insertion for performance

### 2.3 Data Quality ⏳
- [ ] Remove duplicates
- [ ] Validate data completeness
- [ ] Check for missing categories
- [ ] Verify embedding dimensions (1536)
- [ ] Test search quality with sample queries

### 2.4 Migration Execution ⏳
- [ ] Backup existing database
- [ ] Run migration script
- [ ] Verify record counts
- [ ] Test search functionality
- [ ] Validate category distribution
- [ ] Check for data integrity issues

---

## Phase 3: Cline Integration ⏳ PENDING USER ACTION

### 3.1 MCP Configuration ⏳
- [ ] **USER ACTION:** Edit cline_mcp_settings.json
- [ ] **USER ACTION:** Add shadowrun-gm server configuration
- [ ] **USER ACTION:** Restart VS Code
- [ ] Verify server appears in Cline's MCP list
- [ ] Test connection from Cline

### 3.2 Functional Testing ⏳
- [ ] Test query_rules from Cline
- [ ] Test explain_mechanic from Cline
- [ ] Test list_rule_categories from Cline
- [ ] Verify response formatting
- [ ] Test with various query types
- [ ] Validate error handling

---

## Phase 4: Enhanced Search Capabilities ⏳ FUTURE

### 4.1 Vector Search Implementation ⏳
- [ ] Ensure all rules have embeddings
- [ ] Implement semantic search function
- [ ] Add hybrid search (vector + full-text)
- [ ] Tune search relevance
- [ ] Add similarity threshold configuration

### 4.2 Advanced Query Features ⏳
- [ ] Add multi-category search
- [ ] Implement tag-based filtering
- [ ] Add source book filtering
- [ ] Create related rules suggestions
- [ ] Add search result ranking

### 4.3 Performance Optimization ⏳
- [ ] Analyze query performance
- [ ] Optimize index usage
- [ ] Implement query caching
- [ ] Add connection pooling tuning
- [ ] Monitor database performance

---

## Phase 5: Gear & Equipment Database ⏳ FUTURE

### 5.1 Schema Design ⏳
- [ ] Design gear_items table
  - [ ] Weapons (damage, range, ammo)
  - [ ] Armor (ballistic, impact ratings)
  - [ ] Cyberware (essence cost, effects)
  - [ ] Equipment (cost, availability)
- [ ] Add gear categories and subcategories
- [ ] Create indexes for common queries

### 5.2 MCP Tools ⏳
- [ ] Implement lookup_gear tool
- [ ] Implement compare_gear tool
- [ ] Implement search_by_stats tool
- [ ] Add availability/cost filtering

### 5.3 Data Population ⏳
- [ ] Extract gear data from source books
- [ ] Categorize all equipment
- [ ] Add stats and descriptions
- [ ] Link to relevant rules

---

## Phase 6: Character Management ⏳ FUTURE

### 6.1 Schema Design ⏳
- [ ] Design characters table
- [ ] Design character_skills table
- [ ] Design character_gear table
- [ ] Design character_cyberware table
- [ ] Add character progression tracking

### 6.2 MCP Tools ⏳
- [ ] Implement create_character tool
- [ ] Implement update_character tool
- [ ] Implement get_character tool
- [ ] Implement calculate_derived_stats tool
- [ ] Add karma/experience tracking

### 6.3 Character Features ⏳
- [ ] Attribute management
- [ ] Skill tracking
- [ ] Gear inventory
- [ ] Essence tracking
- [ ] Condition monitor
- [ ] Karma pool management

---

## Phase 7: Setting & Lore Database ⏳ FUTURE

### 7.1 Schema Design ⏳
- [ ] Design lore_content table
  - [ ] Locations
  - [ ] Corporations
  - [ ] NPCs
  - [ ] Timeline events
  - [ ] Factions
- [ ] Add relationship mapping
- [ ] Create cross-reference system

### 7.2 MCP Tools ⏳
- [ ] Implement query_lore tool
- [ ] Implement get_location tool
- [ ] Implement get_corporation tool
- [ ] Implement timeline_lookup tool

### 7.3 Content Population ⏳
- [ ] Extract lore from source books
- [ ] Organize by category
- [ ] Add cross-references
- [ ] Link to relevant rules

---

## Phase 8: Advanced Features ⏳ FUTURE

### 8.1 Campaign Management ⏳
- [ ] Session notes storage
- [ ] NPC tracking
- [ ] Plot thread management
- [ ] Location/scene tracking

### 8.2 Dice Integration ⏳
- [ ] Link to dice-server MCP
- [ ] Create combined roll + rule lookup
- [ ] Add context-aware rolling
- [ ] Implement roll history

### 8.3 AI Enhancements ⏳
- [ ] Add rule interpretation assistance
- [ ] Implement scenario suggestions
- [ ] Create encounter generators
- [ ] Add house rule management

---

## Current Status Summary

### ✅ Completed (Phase 1)
- Project structure and setup
- Database schema with vector support
- Three functional MCP tools
- Sample data for testing
- Comprehensive documentation
- Server tested and verified

### 🔄 Next Immediate Steps (Phase 2)
1. **Analyze existing RAG database** - Understand current data structure
2. **Create migration script** - Build tool to transfer data
3. **Execute migration** - Populate database with full rules
4. **Validate migration** - Ensure data quality and completeness

### ⏳ Pending User Action (Phase 3)
- Add shadowrun-gm to Cline MCP settings
- Restart VS Code
- Test tools from within Cline

### 🔮 Future Enhancements (Phases 4-8)
- Vector search optimization
- Gear database
- Character management
- Setting/lore database
- Advanced campaign tools

---

## Missing or Overlooked Items

### From Original Plan - Still Needed:
1. **Migration Script** - Critical for populating database with full rules
2. **Embedding Generation** - If not reusing existing embeddings
3. **Data Validation Tools** - To ensure migration quality
4. **Backup Strategy** - Before running migrations
5. **Performance Benchmarks** - To measure search speed

### Additional Considerations:
1. **Error Logging** - Add comprehensive logging to server
2. **Rate Limiting** - If using OpenAI API for embeddings
3. **Data Versioning** - Track which source books are included
4. **Update Mechanism** - How to add new rules/errata
5. **Multi-user Support** - If multiple GMs will use the system

---

## Recommended Next Actions

### Immediate (This Week):
1. **Analyze RAG Database Structure**
   - Examine current vector store
   - Document data format
   - Identify all data sources

2. **Create Migration Script**
   - Choose Python or Node.js
   - Implement data extraction
   - Add transformation logic
   - Test with small dataset

3. **Add to Cline Settings**
   - Update MCP configuration
   - Test basic functionality
   - Verify all tools work

### Short Term (Next 2 Weeks):
1. **Execute Full Migration**
   - Run migration script
   - Validate all data
   - Test search quality

2. **Optimize Search**
   - Implement vector search
   - Tune relevance
   - Add hybrid search

### Medium Term (Next Month):
1. **Start Gear Database**
   - Design schema
   - Begin data entry
   - Create lookup tools

2. **Enhanced Documentation**
   - Add API reference
   - Create video tutorials
   - Write migration guide

---

## Success Metrics

### Phase 1 (Completed):
- ✅ Server starts without errors
- ✅ Database connection successful
- ✅ All three tools functional
- ✅ Sample queries return results

### Phase 2 (Migration):
- [ ] 100% of RAG data migrated
- [ ] Zero data loss
- [ ] Search quality maintained or improved
- [ ] Query response time < 500ms

### Phase 3 (Integration):
- [ ] Server visible in Cline
- [ ] All tools accessible from Cline
- [ ] No connection errors
- [ ] Responses properly formatted

---

## Notes & Decisions

### Technology Choices:
- **Database:** PostgreSQL via Supabase (local Docker)
- **Vector Search:** pgvector extension
- **MCP SDK:** @modelcontextprotocol/sdk v1.19.1
- **Node.js:** ES modules (type: "module")
- **Embeddings:** OpenAI text-embedding-3-small (1536 dimensions)

### Design Decisions:
- Full-text search as fallback when embeddings not available
- Category-based filtering for faster queries
- Tag system for flexible organization
- Source tracking for attribution
- Timestamp tracking for updates

### Open Questions:
1. Should we regenerate embeddings or reuse existing?
2. What's the priority order for gear vs character vs lore?
3. Do we need multi-edition support (2nd vs 3rd vs later)?
4. Should we support house rules/custom content?
5. What's the backup/restore strategy?

---

**Last Updated:** 2025-10-05 02:36 AM
**Current Phase:** Phase 1 Complete, Phase 2 Planning
**Next Milestone:** Complete data migration from RAG database
