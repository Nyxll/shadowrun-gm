#!/usr/bin/env node

/**
 * Shadowrun GM MCP Server
 * Provides tools for querying Shadowrun 2nd Edition rules, gear, and game mechanics
 * Phase 1: Rules System
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

// Database connection pool
const pool = new Pool({
  host: process.env.POSTGRES_HOST || 'localhost',
  port: parseInt(process.env.POSTGRES_PORT || '5432'),
  user: process.env.POSTGRES_USER || 'postgres',
  password: process.env.POSTGRES_PASSWORD,
  database: process.env.POSTGRES_DB || 'postgres',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Test database connection
pool.on('error', (err) => {
  console.error('Unexpected database error:', err);
});

// Create MCP server
const server = new Server(
  {
    name: 'shadowrun-gm',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

/**
 * Helper function to perform vector similarity search
 * Note: This requires embeddings to be pre-generated and stored
 */
async function vectorSearch(query, category = null, limit = 3) {
  try {
    // For now, we'll use full-text search until embeddings are populated
    // In production, you would generate an embedding for the query and use vector similarity
    
    let sql = `
      SELECT 
        id,
        title,
        content,
        category,
        subcategory,
        tags,
        ts_rank(to_tsvector('english', title || ' ' || content), plainto_tsquery('english', $1)) as rank
      FROM rules_content
      WHERE to_tsvector('english', title || ' ' || content) @@ plainto_tsquery('english', $1)
    `;
    
    const params = [query];
    
    if (category) {
      sql += ` AND category = $2`;
      params.push(category);
    }
    
    sql += ` ORDER BY rank DESC LIMIT $${params.length + 1}`;
    params.push(limit);
    
    const result = await pool.query(sql, params);
    return result.rows;
  } catch (error) {
    console.error('Vector search error:', error);
    throw error;
  }
}

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'query_rules',
        description: 'Search for Shadowrun 2nd Edition rules using natural language. Returns relevant rule sections without page citations.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Natural language question about game rules (e.g., "How does initiative work?", "What is the target number for shooting?")',
            },
            category: {
              type: 'string',
              description: 'Optional: Filter by rule category',
              enum: ['combat', 'magic', 'matrix', 'character_creation', 'skills', 'gear_mechanics', 'general'],
            },
            limit: {
              type: 'number',
              description: 'Maximum number of results to return (default: 3)',
              default: 3,
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'explain_mechanic',
        description: 'Get a detailed explanation of a specific game mechanic by combining related rules into a comprehensive answer.',
        inputSchema: {
          type: 'object',
          properties: {
            mechanic: {
              type: 'string',
              description: 'The game mechanic to explain (e.g., "initiative", "target numbers", "combat pool", "spellcasting drain")',
            },
          },
          required: ['mechanic'],
        },
      },
      {
        name: 'list_rule_categories',
        description: 'List all available rule categories and their subcategories to help browse the rules database.',
        inputSchema: {
          type: 'object',
          properties: {},
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case 'query_rules': {
        const { query, category, limit = 3 } = args;
        
        if (!query) {
          throw new Error('Query parameter is required');
        }

        const results = await vectorSearch(query, category, limit);
        
        if (results.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: `No rules found matching: "${query}"\n\nTry rephrasing your question or use list_rule_categories to see available topics.`,
              },
            ],
          };
        }

        // Format results
        let response = `Found ${results.length} rule(s) for: "${query}"\n\n`;
        
        results.forEach((rule, index) => {
          response += `## ${index + 1}. ${rule.title}\n`;
          response += `**Category:** ${rule.category}`;
          if (rule.subcategory) {
            response += ` > ${rule.subcategory}`;
          }
          response += '\n\n';
          response += `${rule.content}\n\n`;
          if (rule.tags && rule.tags.length > 0) {
            response += `*Tags: ${rule.tags.join(', ')}*\n\n`;
          }
          response += '---\n\n';
        });

        return {
          content: [
            {
              type: 'text',
              text: response,
            },
          ],
        };
      }

      case 'explain_mechanic': {
        const { mechanic } = args;
        
        if (!mechanic) {
          throw new Error('Mechanic parameter is required');
        }

        // Search for all related rules
        const results = await vectorSearch(mechanic, null, 5);
        
        if (results.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: `No information found about: "${mechanic}"\n\nTry using query_rules with a more specific question.`,
              },
            ],
          };
        }

        // Synthesize explanation
        let explanation = `# ${mechanic.toUpperCase()}\n\n`;
        explanation += `This explanation combines ${results.length} related rule section(s):\n\n`;
        
        results.forEach((rule, index) => {
          explanation += `### ${rule.title}\n`;
          explanation += `${rule.content}\n\n`;
        });

        return {
          content: [
            {
              type: 'text',
              text: explanation,
            },
          ],
        };
      }

      case 'list_rule_categories': {
        const result = await pool.query(`
          SELECT 
            category,
            array_agg(DISTINCT subcategory) FILTER (WHERE subcategory IS NOT NULL) as subcategories,
            COUNT(*) as rule_count
          FROM rules_content
          GROUP BY category
          ORDER BY category
        `);

        if (result.rows.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No rules categories found. The database may be empty.',
              },
            ],
          };
        }

        let response = '# Available Rule Categories\n\n';
        
        result.rows.forEach((cat) => {
          response += `## ${cat.category} (${cat.rule_count} rules)\n`;
          if (cat.subcategories && cat.subcategories.length > 0) {
            response += `Subcategories: ${cat.subcategories.join(', ')}\n`;
          }
          response += '\n';
        });

        return {
          content: [
            {
              type: 'text',
              text: response,
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${error.message}`,
        },
      ],
      isError: true,
    };
  }
});

/**
 * List available resources
 */
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'shadowrun://rules/categories',
        name: 'Rule Categories',
        description: 'List of all available rule categories',
        mimeType: 'text/plain',
      },
    ],
  };
});

/**
 * Read resource content
 */
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;

  if (uri === 'shadowrun://rules/categories') {
    const result = await pool.query(`
      SELECT DISTINCT category 
      FROM rules_content 
      ORDER BY category
    `);
    
    const categories = result.rows.map(row => row.category).join('\n');
    
    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text: categories,
        },
      ],
    };
  }

  throw new Error(`Unknown resource: ${uri}`);
});

/**
 * Start the server
 */
async function main() {
  // Test database connection
  try {
    await pool.query('SELECT NOW()');
    console.error('Database connection successful');
  } catch (error) {
    console.error('Database connection failed:', error.message);
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Shadowrun GM MCP Server running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
