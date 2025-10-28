#!/usr/bin/env node

import fs from 'fs';
import path from 'path';

const XAI_DIR = 'D:/projects/xAI/prod-mc-asset-server';

console.log('Testing xAI directory access...');
console.log('Directory:', XAI_DIR);

try {
  if (!fs.existsSync(XAI_DIR)) {
    console.error('ERROR: Directory does not exist!');
    process.exit(1);
  }
  
  console.log('✓ Directory exists');
  
  const entries = fs.readdirSync(XAI_DIR);
  console.log(`✓ Found ${entries.length} entries`);
  
  const folders = entries.filter(name => {
    const fullPath = path.join(XAI_DIR, name);
    return fs.statSync(fullPath).isDirectory();
  });
  
  console.log(`✓ Found ${folders.length} folders`);
  
  // Check first folder
  if (folders.length > 0) {
    const firstFolder = folders[0];
    const contentPath = path.join(XAI_DIR, firstFolder, 'content');
    console.log(`\nChecking first folder: ${firstFolder}`);
    console.log(`Content file exists: ${fs.existsSync(contentPath)}`);
    
    if (fs.existsSync(contentPath)) {
      const content = fs.readFileSync(contentPath, 'utf-8');
      console.log(`Content length: ${content.length} characters`);
      console.log(`First 200 chars:\n${content.substring(0, 200)}`);
    }
  }
  
  console.log('\n✓ All tests passed!');
  
} catch (error) {
  console.error('ERROR:', error.message);
  console.error(error.stack);
  process.exit(1);
}
