#!/usr/bin/env node

/**
 * Shadowrun GM MCP Server - Enhanced
 * Provides tools for querying Shadowrun 2nd Edition rules with clarifications and logging
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import queryEngine from './lib/query-engine.js';

// Create MCP server
const server = new Server(
  {
    name: 'shadowrun-gm',
    version: '2.0.0',
  },
  {
    capabilities: {
      tools: {},
      resources: {},
    },
  }
);

/**
 * Format clarifications for display
 */
function formatClarifications(clarifications) {
  if (!clarifications || clarifications.length === 0) {
    return '';
  }
  
  let output = '\n### 📋 Clarifications & Errata\n\n';
  
  clarifications.forEach((clarification) => {
    const typeEmoji = {
      'errata': '⚠️',
      'limitation': '🚫',
      'clarification': 'ℹ️',
      'house_rule': '🏠',
      'faq': '❓'
    };
    
    const emoji = typeEmoji[clarification.clarification_type] || '📌';
    
    output += `${emoji} **${clarification.title}** (${clarification.source})\n\n`;
    output += `${clarification.content}\n\n`;
    
    if (clarification.source_reference) {
      output += `*Source: ${clarification.source_reference}*\n\n`;
    }
  });
  
  return output;
}

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'query_rules',
        description: 'Search for Shadowrun 2nd Edition rules using natural language. Returns relevant rule sections with clarifications and errata.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Natural language question about game rules (e.g., "How does initiative work?", "Can heavy pistols fire full auto?")',
            },
            category: {
              type: 'string',
              description: 'Optional: Filter by rule category',
              enum: ['combat', 'magic', 'matrix', 'character_creation', 'skills', 'gear_mechanics', 'general', 'lore'],
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
        name: 'query_rules_advanced',
        description: 'Advanced multi-topic search that automatically searches for related concepts and includes general clarifications. Best for complex questions involving multiple game mechanics.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Complex question or scenario (e.g., "shooting full auto in darkness with thermographic vision and smartlink")',
            },
            topics: {
              type: 'array',
              items: { type: 'string' },
              description: 'Optional: Specific topics to search (e.g., ["full auto", "darkness", "smartlink"]). If not provided, will be inferred from query.',
            },
            category: {
              type: 'string',
              description: 'Optional: Filter by rule category',
              enum: ['combat', 'magic', 'matrix', 'character_creation', 'skills', 'gear_mechanics', 'general', 'lore'],
            },
          },
          required: ['query'],
        },
      },
      {
        name: 'explain_mechanic',
        description: 'Get a detailed explanation of a specific game mechanic by combining related rules and clarifications into a comprehensive answer.',
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
      {
        name: 'get_clarifications',
        description: 'Search for clarifications, errata, limitations, and house rules. Useful for finding official corrections or common misconceptions.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'What to search for (e.g., "heavy pistol", "smartlink", "initiative ties")',
            },
            type: {
              type: 'string',
              description: 'Optional: Filter by clarification type',
              enum: ['errata', 'limitation', 'clarification', 'house_rule', 'faq'],
            },
          },
          required: ['query'],
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

        const result = await queryEngine.simpleQuery(query, category, limit);
        
        if (result.count === 0) {
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
        let response = `Found ${result.count} rule(s) for: "${query}"\n`;
        response += `*Query executed in ${result.executionTime}ms*\n\n`;
        
        result.results.forEach((rule, index) => {
          response += `## ${index + 1}. ${rule.title}\n`;
          response += `**Category:** ${rule.category}`;
          if (rule.subcategory) {
            response += ` > ${rule.subcategory}`;
          }
          response += '\n\n';
          response += `${rule.content}\n`;
          
          if (rule.tags && rule.tags.length > 0) {
            response += `\n*Tags: ${rule.tags.join(', ')}*\n`;
          }
          
          // Add clarifications if any
          if (rule.clarifications && rule.clarifications.length > 0) {
            response += formatClarifications(rule.clarifications);
          }
          
          response += '\n---\n\n';
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

      case 'query_rules_advanced': {
        const { query, topics, category } = args;
        
        if (!query) {
          throw new Error('Query parameter is required');
        }

        let result;
        
        if (topics && topics.length > 0) {
          // Use provided topics
          result = await queryEngine.multiTopicQuery(topics, 3);
        } else {
          // Use advanced query with general clarifications
          result = await queryEngine.advancedQuery(query, { category, includeGeneralClarifications: true });
        }
        
        let response = `# Advanced Search Results\n\n`;
        response += `Query: "${query}"\n`;
        response += `*Executed in ${result.executionTime}ms*\n\n`;
        
        if (topics && topics.length > 0) {
          // Multi-topic results
          if (result.topicCount === 0) {
            return {
              content: [
                {
                  type: 'text',
                  text: `No rules found for the specified topics.\n\nTry different search terms or use query_rules for a simpler search.`,
                },
              ],
            };
          }
          
          result.results.forEach((topicResult) => {
            response += `## Topic: ${topicResult.topic}\n\n`;
            
            topicResult.results.forEach((rule, index) => {
              response += `### ${index + 1}. ${rule.title}\n`;
              response += `**Category:** ${rule.category}`;
              if (rule.subcategory) {
                response += ` > ${rule.subcategory}`;
              }
              response += '\n\n';
              response += `${rule.content}\n`;
              
              if (rule.clarifications && rule.clarifications.length > 0) {
                response += formatClarifications(rule.clarifications);
              }
              
              response += '\n';
            });
            
            response += '---\n\n';
          });
        } else {
          // Advanced query results
          if (result.count === 0) {
            return {
              content: [
                {
                  type: 'text',
                  text: `No rules found matching: "${query}"\n\nTry rephrasing your question or use list_rule_categories to see available topics.`,
                },
              ],
            };
          }
          
          response += `## Matching Rules\n\n`;
          
          result.results.forEach((rule, index) => {
            response += `### ${index + 1}. ${rule.title}\n`;
            response += `**Category:** ${rule.category}`;
            if (rule.subcategory) {
              response += ` > ${rule.subcategory}`;
            }
            response += '\n\n';
            response += `${rule.content}\n`;
            
            if (rule.clarifications && rule.clarifications.length > 0) {
              response += formatClarifications(rule.clarifications);
            }
            
            response += '\n';
          });
          
          // Add general clarifications
          if (result.generalClarifications && result.generalClarifications.length > 0) {
            response += `## General Clarifications\n\n`;
            response += formatClarifications(result.generalClarifications);
          }
        }

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

        const result = await queryEngine.advancedQuery(mechanic, { limit: 5, includeGeneralClarifications: true });
        
        if (result.count === 0) {
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
        explanation += `This explanation combines ${result.count} related rule section(s):\n\n`;
        
        result.results.forEach((rule, index) => {
          explanation += `## ${rule.title}\n\n`;
          explanation += `${rule.content}\n`;
          
          if (rule.clarifications && rule.clarifications.length > 0) {
            explanation += formatClarifications(rule.clarifications);
          }
          
          explanation += '\n';
        });
        
        // Add general clarifications
        if (result.generalClarifications && result.generalClarifications.length > 0) {
          explanation += `## Additional Clarifications\n\n`;
          explanation += formatClarifications(result.generalClarifications);
        }

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
        const categories = await queryEngine.getCategories();

        if (categories.length === 0) {
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
        
        for (const cat of categories) {
          response += `## ${cat.category} (${cat.count} rules)\n`;
          
          // Get subcategories
          const subcats = await queryEngine.getSubcategories(cat.category);
          if (subcats.length > 0) {
            response += `Subcategories: ${subcats.map(s => `${s.subcategory} (${s.count})`).join(', ')}\n`;
          }
          response += '\n';
        }

        return {
          content: [
            {
              type: 'text',
              text: response,
            },
          ],
        };
      }

      case 'get_clarifications': {
        const { query, type } = args;
        
        if (!query) {
          throw new Error('Query parameter is required');
        }

        const clarifications = await queryEngine.getGeneralClarifications(query, 10);
        
        // Filter by type if specified
        const filtered = type 
          ? clarifications.filter(c => c.clarification_type === type)
          : clarifications;
        
        if (filtered.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: `No clarifications found for: "${query}"${type ? ` (type: ${type})` : ''}`,
              },
            ],
          };
        }

        let response = `# Clarifications for: "${query}"\n\n`;
        response += `Found ${filtered.length} clarification(s)\n\n`;
        response += formatClarifications(filtered);

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
    console.error('Tool error:', error);
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
      {
        uri: 'shadowrun://clarifications/all',
        name: 'All Clarifications',
        description: 'All active clarifications and errata',
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
    const categories = await queryEngine.getCategories();
    const text = categories.map(c => `${c.category}: ${c.count} rules`).join('\n');
    
    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text,
        },
      ],
    };
  }
  
  if (uri === 'shadowrun://clarifications/all') {
    const clarifications = await queryEngine.getGeneralClarifications('', 100);
    const text = clarifications.map(c => 
      `[${c.clarification_type}] ${c.title}\n${c.content}\n---`
    ).join('\n\n');
    
    return {
      contents: [
        {
          uri,
          mimeType: 'text/plain',
          text,
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
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Shadowrun GM MCP Server (Enhanced) running on stdio');
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
