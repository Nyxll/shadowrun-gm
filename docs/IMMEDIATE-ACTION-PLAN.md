# Immediate Action Plan - Schema & CRUD Fixes

## Current Status
✅ Identified all schema mismatches  
✅ Fixed character lookup (street_name)  
✅ Added cost field to character_edges_flaws  
⏳ Need to complete remaining fixes

## Critical Issues to Fix

### 1. character_vehicles - RESTORE Audit Fields ⚠️
**Problem**: Removed audit field support, but table HAS them  
**Fix**: Update comprehensive_crud.py to use audit fields  
**Fields**: created_by, modified_by, modified_at, deleted_at, deleted_by  
**Sensor data**: Store in `modifications` JSONB field

### 2. character_edges_flaws - ADD Cost Support ✅
**Status**: Migration applied, cost field exists  
**Next**: Update CRUD to include cost field  
**Next**: Create tool to populate costs from RAG database

### 3. Populate Edge/Flaw Costs from RAG
**Examples from user**:
- Aptitude (Sorcery): -1 point (edge, costs karma)
- Shadow Echo: +1 point (flaw, gives karma)
- Weak Immune System: +1 point (flaw, gives karma)

**Convention**:
- Edges: NEGATIVE cost (they cost karma to buy)
- Flaws: POSITIVE cost (they give karma back)

### 4. Update schema.sql
**Problem**: schema.sql doesn't match actual database  
**Solution**: Replace with actual schema from schema-actual.sql  
**Note**: Keep as reference, actual DB is source of truth

## Step-by-Step Plan

### Phase 1: Fix CRUD API ⏳
1. ✅ Add cost field to character_edges_flaws table
2. ⏳ Update comprehensive_crud.py:
   - Add cost parameter to add_edge_flaw()
   - Restore audit fields to character_vehicles operations
   - Add sensor support via modifications JSONB
3. ⏳ Test all CRUD operations

### Phase 2: Populate Data 📊
4. ⏳ Create tool to query RAG for edge/flaw costs
5. ⏳ Populate existing edges/flaws with costs
6. ⏳ Verify all edges/flaws have costs

### Phase 3: Update Dependent Systems 🔧
7. ⏳ Update MCP operations to use corrected CRUD
8. ⏳ Update orchestrator
9. ⏳ Update UI to display costs
10. ⏳ Update documentation

### Phase 4: Schema Documentation 📝
11. ⏳ Update schema.sql with actual schema
12. ⏳ Document all JSONB field structures
13. ⏳ Create schema migration guide

## Files to Modify

### CRUD API
- `lib/comprehensive_crud.py` - Fix vehicles audit, add edge/flaw cost

### Tools
- `tools/populate-edge-flaw-costs.py` - NEW: Query RAG and populate costs

### MCP Operations
- `game-server.py` - Update to use corrected CRUD

### Documentation
- `schema.sql` - Replace with actual schema
- `docs/MCP-TOOLS-REFERENCE.md` - Update operation signatures
- `docs/CRUD-API-IMPLEMENTATION-PLAN.md` - Update with corrections

## Next Immediate Steps

1. Fix comprehensive_crud.py (vehicles + edges/flaws)
2. Create RAG query tool for edge/flaw costs
3. Populate all edge/flaw costs
4. Test all operations
5. Update MCP server
6. Update documentation

## Success Criteria
✅ All CRUD operations match actual schema  
✅ All edges/flaws have cost values  
✅ Vehicle operations support audit trail  
✅ Sensor data stored in modifications JSONB  
✅ All tests pass  
✅ MCP operations work correctly  
✅ Documentation is accurate
