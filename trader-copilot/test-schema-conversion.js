const { z } = require('zod');
const { zodToJsonSchema } = require('zod-to-json-schema');

// Define a test Zod schema
const testSchema = z.object({
  section: z.enum(['full', 'market', 'coin']).default('market').describe('Which section of the snapshot to return'),
  coin: z.string().optional().describe('Specific coin to get data for')
});

// Convert to JSON Schema
const jsonSchema = zodToJsonSchema(testSchema, {
  target: 'openApi3',
  $refStrategy: 'none'
});

console.log('Converted JSON Schema:');
console.log(JSON.stringify(jsonSchema, null, 2));