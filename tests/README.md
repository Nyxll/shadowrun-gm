# Shadowrun GM MCP Server - Test Suite

Comprehensive test suite for the Shadowrun GM MCP Server covering all tools, operations, and edge cases.

## Test Files

### Phase 1 - Core Functionality ✅

1. **test-dice-rolling.js** - Dice Rolling System Tests
   - All 13 dice-related MCP tools
   - Basic rolls, modifiers, advantage/disadvantage
   - Shadowrun-style target numbers and exploding dice
   - Initiative tracking
   - Dice pools and opposed rolls
   - Karma mechanics (reroll, buy dice, buy successes)
   - Error handling

2. **test-gear-operations.js** - Gear System Integration Tests
   - lookup_gear with various filters
   - compare_gear with different sort criteria
   - get_gear_details
   - Category, subcategory, cost, and tag filtering
   - Edge cases and error handling

### Phase 2 - Analytics & Monitoring (Planned)

3. **test-query-analytics.js** - Query Analytics & Logging Tests
4. **test-performance-monitoring.js** - Performance Monitoring Tests
5. **test-error-logging.js** - Error Logging & Recovery Tests

### Phase 3 - Advanced Features (Planned)

6. **test-vector-search.js** - Embedding & Vector Search Tests
7. **test-clarifications.js** - Rule Clarifications & Errata Tests
8. **test-campaign-management.js** - Campaign & House Rules Tests

### Phase 4 - Quality & Optimization (Planned)

9. **test-data-quality.js** - Data Quality & Validation Tests
10. **test-chunking-quality.js** - Chunking Quality Tests
11. **test-cost-optimization.js** - Cost Optimization Tests
12. **test-fulltext-search.js** - Full-Text Search Tests

### Phase 5 - Usage Analysis (Planned)

13. **test-query-patterns.js** - Real-World Query Pattern Tests
14. **test-content-gaps.js** - Content Gap Analysis Tests
15. **test-search-quality.js** - Search Quality Tests

## Running Tests

### Run All Tests
```bash
npm test
```

### Run Specific Test File
```bash
node tests/test-dice-rolling.js
node tests/test-gear-operations.js
```

### Run with Coverage
```bash
npm run test:coverage
```

## Test Structure

Each test file follows this structure:

```javascript
#!/usr/bin/env node

// Test result tracking
let testsPassed = 0;
let testsFailed = 0;
const failedTests = [];

function assert(condition, testName, details = '') {
  if (condition) {
    console.log(`✅ PASS: ${testName}`);
    testsPassed++;
  } else {
    console.log(`❌ FAIL: ${testName}`);
    if (details) console.log(`   Details: ${details}`);
    testsFailed++;
    failedTests.push({ name: testName, details });
  }
}

async function runTests() {
  // Test cases here
  
  // Summary
  console.log(`\n📊 Test Results: ${testsPassed} passed, ${testsFailed} failed`);
  process.exit(testsFailed > 0 ? 1 : 0);
}

runTests().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
```

## Environment Setup

Tests require the following environment variables (from `.env`):

```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5434
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=postgres
OPENAI_API_KEY=your_openai_key
```

## Test Coverage Goals

- ✅ 100% of MCP tools tested
- ✅ All query classification paths covered
- ✅ Edge cases and error conditions
- 🔄 Performance benchmarks established
- 🔄 Integration workflows validated

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: npm test
  
- name: Check Coverage
  run: npm run test:coverage
```

## Contributing

When adding new tests:

1. Follow the existing test structure
2. Use descriptive test names
3. Include both positive and negative test cases
4. Add error handling tests
5. Update this README with new test descriptions

## Test Results Format

Each test outputs:
- ✅ PASS: Test name
- ❌ FAIL: Test name (with details)
- 📊 Summary: X passed, Y failed

Exit codes:
- 0: All tests passed
- 1: One or more tests failed

## Dependencies

- `pg` - PostgreSQL client
- `axios` - HTTP client for dice API
- `dotenv` - Environment variable management
- `openai` - OpenAI API client (for classification tests)
