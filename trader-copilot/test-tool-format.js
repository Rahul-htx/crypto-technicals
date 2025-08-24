// Test to understand AI SDK tool format
const { tool } = require('ai');
const { z } = require('zod');

// Log what tool function returns
const testTool = tool({
  description: 'Test tool',
  parameters: z.object({
    test: z.string()
  }),
  execute: async ({ test }) => {
    return { result: test };
  }
});

console.log('Tool object structure:');
console.log(JSON.stringify(testTool, null, 2));

// Check if there's a schema property
console.log('\nTool properties:');
console.log(Object.keys(testTool));

// Check parameters
if (testTool.parameters) {
  console.log('\nParameters type:', typeof testTool.parameters);
  console.log('Parameters:', testTool.parameters);
}