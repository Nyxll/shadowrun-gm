#!/usr/bin/env node

/**
 * xAI Export Discovery Tool
 * Safely counts and lists UUID folders without parsing content
 * This is Chunk 1 - Discovery & Counting
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const XAI_EXPORT_DIR = 'D:/projects/xAI/prod-mc-asset-server';
const OUTPUT_DIR = path.join(__dirname, '../parsed-xai-data');

// Ensure output directory exists
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

/**
 * Get file size in human-readable format
 */
function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Main discovery function
 */
async function discoverXAIExports() {
  console.log('🔍 xAI Export Discovery Tool');
  console.log('=' .repeat(60));
  console.log(`Scanning: ${XAI_EXPORT_DIR}\n`);
  
  if (!fs.existsSync(XAI_EXPORT_DIR)) {
    console.error(`❌ Directory not found: ${XAI_EXPORT_DIR}`);
    console.log('\nPlease verify the path is correct.');
    return;
  }
  
  console.log('📊 Counting folders...\n');
  
  const entries = fs.readdirSync(XAI_EXPORT_DIR);
  const folders = [];
  let totalSize = 0;
  let foldersWithContent = 0;
  let foldersWithoutContent = 0;
  
  for (const entry of entries) {
    const fullPath = path.join(XAI_EXPORT_DIR, entry);
    const stats = fs.statSync(fullPath);
    
    if (stats.isDirectory()) {
      const contentPath = path.join(fullPath, 'content');
      const hasContent = fs.existsSync(contentPath);
      
      let contentSize = 0;
      if (hasContent) {
        const contentStats = fs.statSync(contentPath);
        contentSize = contentStats.size;
        totalSize += contentSize;
        foldersWithContent++;
      } else {
        foldersWithoutContent++;
      }
      
      folders.push({
        uuid: entry,
        hasContent,
        contentSize,
        contentSizeFormatted: formatBytes(contentSize)
      });
    }
  }
  
  // Sort by size (largest first)
  folders.sort((a, b) => b.contentSize - a.contentSize);
  
  // Calculate statistics
  const avgSize = foldersWithContent > 0 ? totalSize / foldersWithContent : 0;
  const largestFile = folders.find(f => f.hasContent);
  const smallestFile = [...folders].reverse().find(f => f.hasContent);
  
  // Display results
  console.log('📈 Discovery Results:');
  console.log('─'.repeat(60));
  console.log(`Total UUID folders: ${folders.length}`);
  console.log(`Folders with content: ${foldersWithContent}`);
  console.log(`Folders without content: ${foldersWithoutContent}`);
  console.log(`Total content size: ${formatBytes(totalSize)}`);
  console.log(`Average file size: ${formatBytes(avgSize)}`);
  
  if (largestFile) {
    console.log(`Largest file: ${largestFile.contentSizeFormatted} (${largestFile.uuid})`);
  }
  if (smallestFile) {
    console.log(`Smallest file: ${smallestFile.contentSizeFormatted} (${smallestFile.uuid})`);
  }
  
  // Show size distribution
  console.log('\n📊 Size Distribution:');
  const sizeRanges = {
    'Under 1 KB': 0,
    '1-10 KB': 0,
    '10-50 KB': 0,
    '50-100 KB': 0,
    'Over 100 KB': 0
  };
  
  folders.forEach(f => {
    if (!f.hasContent) return;
    const kb = f.contentSize / 1024;
    if (kb < 1) sizeRanges['Under 1 KB']++;
    else if (kb < 10) sizeRanges['1-10 KB']++;
    else if (kb < 50) sizeRanges['10-50 KB']++;
    else if (kb < 100) sizeRanges['50-100 KB']++;
    else sizeRanges['Over 100 KB']++;
  });
  
  Object.entries(sizeRanges).forEach(([range, count]) => {
    if (count > 0) {
      const bar = '█'.repeat(Math.ceil(count / 5));
      console.log(`  ${range.padEnd(15)}: ${count.toString().padStart(4)} ${bar}`);
    }
  });
  
  // Show first 10 folders as preview
  console.log('\n📋 First 10 Folders (Preview):');
  console.log('─'.repeat(60));
  folders.slice(0, 10).forEach((f, i) => {
    const status = f.hasContent ? '✓' : '✗';
    const size = f.hasContent ? f.contentSizeFormatted : 'no content';
    console.log(`${(i + 1).toString().padStart(2)}. ${status} ${f.uuid.substring(0, 36)} (${size})`);
  });
  
  // Save results
  const results = {
    timestamp: new Date().toISOString(),
    directory: XAI_EXPORT_DIR,
    summary: {
      totalFolders: folders.length,
      foldersWithContent,
      foldersWithoutContent,
      totalSize,
      totalSizeFormatted: formatBytes(totalSize),
      averageSize: avgSize,
      averageSizeFormatted: formatBytes(avgSize)
    },
    sizeDistribution: sizeRanges,
    folders: folders.map(f => ({
      uuid: f.uuid,
      hasContent: f.hasContent,
      contentSize: f.contentSize
    }))
  };
  
  const outputPath = path.join(OUTPUT_DIR, 'xai-discovery.json');
  fs.writeFileSync(outputPath, JSON.stringify(results, null, 2));
  
  console.log('\n💾 Results saved to:');
  console.log(`   ${outputPath}`);
  
  console.log('\n✅ Discovery complete!');
  console.log('\n💡 Next step: Run sample-xai-parse.js to analyze first 10 items');
  
  return results;
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  discoverXAIExports().catch(console.error);
}

export { discoverXAIExports };
