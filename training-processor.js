/**
 * Interactive Training Processor
 * 
 * Processes training queries one at a time, allowing the AI GM to:
 * 1. Classify the query using the intent classifier
 * 2. Provide a GM response
 * 3. Specify any dice rolls required
 * 4. Save results to database
 * 5. Track accuracy in real-time
 */

import 'dotenv/config';
import pkg from 'pg';
const { Pool } = pkg;
import readline from 'readline';
import { IntentClassifier } from './lib/intent/intent-classifier.js';

// Database configuration
const pool = new Pool({
  user: process.env.POSTGRES_USER || process.env.DB_USER || 'postgres',
  host: process.env.POSTGRES_HOST || process.env.DB_HOST || 'localhost',
  database: process.env.POSTGRES_DB || process.env.DB_NAME || 'postgres',
  password: process.env.POSTGRES_PASSWORD || process.env.DB_PASSWORD || 'postgres',
  port: process.env.POSTGRES_PORT || process.env.DB_PORT || 5432,
});

// Initialize intent classifier
const classifier = new IntentClassifier();

// Create readline interface for user input
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

function question(prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, resolve);
  });
}

async function getNextUnprocessedQuery(client) {
  const result = await client.query(`
    SELECT id, query_text, expected_intent
    FROM query_logs
    WHERE is_training_data = TRUE
      AND gm_response IS NULL
    ORDER BY id
    LIMIT 1
  `);
  
  return result.rows[0] || null;
}

async function getTrainingStats(client) {
  const result = await client.query(`
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN gm_response IS NOT NULL THEN 1 ELSE 0 END) as processed,
      SUM(CASE WHEN gm_response IS NULL THEN 1 ELSE 0 END) as pending,
      SUM(CASE WHEN is_correct = TRUE THEN 1 ELSE 0 END) as correct,
      SUM(CASE WHEN is_correct = FALSE THEN 1 ELSE 0 END) as incorrect
    FROM query_logs
    WHERE is_training_data = TRUE
  `);
  
  return result.rows[0];
}

async function saveTrainingResponse(client, queryId, classification, gmResponse, diceRolls) {
  await client.query(`
    UPDATE query_logs
    SET 
      intent = $1,
      confidence = $2,
      classification_method = $3,
      classification = $4,
      gm_response = $5,
      dice_rolls = $6
    WHERE id = $7
  `, [
    classification.intent,
    classification.confidence,
    classification.method,
    JSON.stringify(classification),
    gmResponse,
    JSON.stringify(diceRolls),
    queryId
  ]);
}

function formatDiceRoll(roll) {
  let formatted = `  - ${roll.type}: ${roll.skill || 'Roll'} (${roll.notation})`;
  if (roll.targetNumber) {
    formatted += ` vs TN ${roll.targetNumber}`;
  }
  if (roll.modifiers && roll.modifiers.length > 0) {
    formatted += ` [${roll.modifiers.join(', ')}]`;
  }
  if (roll.reason) {
    formatted += `\n    Reason: ${roll.reason}`;
  }
  return formatted;
}

async function processQuery(client, query) {
  console.log('\n' + '='.repeat(80));
  console.log(`QUERY #${query.id}`);
  console.log('='.repeat(80));
  console.log(`\nPlayer Query: "${query.query_text}"`);
  console.log(`\nExpected Intent: ${query.expected_intent}`);
  
  // Classify the query
  console.log('\nClassifying...');
  const classification = await classifier.classify(query.query_text);
  
  console.log(`\nDetected Intent: ${classification.intent}`);
  console.log(`Confidence: ${(classification.confidence * 100).toFixed(1)}%`);
  console.log(`Method: ${classification.method}`);
  
  const isCorrect = classification.intent === query.expected_intent;
  console.log(`\n${isCorrect ? '✓ CORRECT' : '✗ INCORRECT'} Classification`);
  
  // Get GM response
  console.log('\n' + '-'.repeat(80));
  console.log('GM RESPONSE:');
  console.log('-'.repeat(80));
  
  const gmResponse = await question('\nEnter GM response (or press Enter to skip): ');
  
  if (!gmResponse.trim()) {
    console.log('\nSkipping this query...');
    return false;
  }
  
  // Get dice rolls
  console.log('\n' + '-'.repeat(80));
  console.log('DICE ROLLS:');
  console.log('-'.repeat(80));
  console.log('\nDoes this query require dice rolls? (y/n)');
  
  const needsDice = await question('> ');
  const diceRolls = [];
  
  if (needsDice.toLowerCase() === 'y') {
    let addingRolls = true;
    
    while (addingRolls) {
      console.log('\nEnter dice roll details:');
      
      const rollType = await question('  Type (attack/defense/skill/resistance/initiative): ');
      const skill = await question('  Skill/Attribute name: ');
      const notation = await question('  Notation (e.g., "6d6!" or "[Unarmed]d6!"): ');
      const targetNumber = await question('  Target Number (or press Enter if none): ');
      const reason = await question('  Reason/Description: ');
      
      diceRolls.push({
        type: rollType,
        skill: skill,
        notation: notation,
        targetNumber: targetNumber || null,
        modifiers: [],
        reason: reason
      });
      
      const addAnother = await question('\nAdd another dice roll? (y/n): ');
      addingRolls = addAnother.toLowerCase() === 'y';
    }
  }
  
  // Show summary
  console.log('\n' + '='.repeat(80));
  console.log('SUMMARY');
  console.log('='.repeat(80));
  console.log(`\nQuery: "${query.query_text.substring(0, 60)}..."`);
  console.log(`Expected: ${query.expected_intent}`);
  console.log(`Detected: ${classification.intent} (${isCorrect ? 'CORRECT' : 'INCORRECT'})`);
  console.log(`\nGM Response:\n${gmResponse}`);
  
  if (diceRolls.length > 0) {
    console.log(`\nDice Rolls:`);
    diceRolls.forEach(roll => console.log(formatDiceRoll(roll)));
  }
  
  // Confirm save
  const confirm = await question('\nSave this response? (y/n): ');
  
  if (confirm.toLowerCase() === 'y') {
    await saveTrainingResponse(client, query.id, classification, gmResponse, diceRolls);
    console.log('\n✓ Saved successfully!');
    return true;
  } else {
    console.log('\nNot saved. Moving to next query...');
    return false;
  }
}

async function showProgress(client) {
  const stats = await getTrainingStats(client);
  const accuracy = stats.processed > 0 
    ? ((stats.correct / stats.processed) * 100).toFixed(1)
    : 0;
  
  console.log('\n' + '='.repeat(80));
  console.log('TRAINING PROGRESS');
  console.log('='.repeat(80));
  console.log(`Total Queries:     ${stats.total}`);
  console.log(`Processed:         ${stats.processed} (${((stats.processed / stats.total) * 100).toFixed(1)}%)`);
  console.log(`Pending:           ${stats.pending}`);
  console.log(`Correct:           ${stats.correct}`);
  console.log(`Incorrect:         ${stats.incorrect}`);
  console.log(`Current Accuracy:  ${accuracy}%`);
  console.log('='.repeat(80));
}

async function main() {
  const client = await pool.connect();
  
  try {
    console.log('\n╔════════════════════════════════════════════════════════════════╗');
    console.log('║         SHADOWRUN GM - INTERACTIVE TRAINING PROCESSOR         ║');
    console.log('╚════════════════════════════════════════════════════════════════╝');
    
    await showProgress(client);
    
    console.log('\nCommands:');
    console.log('  - Press Enter to process next query');
    console.log('  - Type "stats" to show progress');
    console.log('  - Type "quit" to exit');
    
    let processing = true;
    
    while (processing) {
      const command = await question('\n> ');
      
      if (command.toLowerCase() === 'quit') {
        processing = false;
        break;
      }
      
      if (command.toLowerCase() === 'stats') {
        await showProgress(client);
        continue;
      }
      
      // Get next unprocessed query
      const query = await getNextUnprocessedQuery(client);
      
      if (!query) {
        console.log('\n🎉 All training queries have been processed!');
        await showProgress(client);
        processing = false;
        break;
      }
      
      // Process the query
      await processQuery(client, query);
      
      // Show updated progress
      await showProgress(client);
    }
    
    console.log('\n✓ Training session complete!');
    
  } catch (err) {
    console.error('\nError during training:', err);
    throw err;
  } finally {
    client.release();
    rl.close();
  }
}

// Run training processor
main()
  .then(() => {
    console.log('\nGoodbye!');
    pool.end();
    process.exit(0);
  })
  .catch((err) => {
    console.error('\nTraining failed:', err);
    pool.end();
    process.exit(1);
  });
