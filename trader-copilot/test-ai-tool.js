// Test the actual AI SDK tool format
const { CoreTool } = require('ai');

// Try creating a tool directly
const testTool = {
  type: 'function',
  function: {
    name: 'testTool',
    description: 'Test tool',
    parameters: {
      type: 'object',
      properties: {
        test: { type: 'string' }
      },
      required: ['test']
    }
  }
};

console.log('Tool structure for OpenAI:');
console.log(JSON.stringify(testTool, null, 2));