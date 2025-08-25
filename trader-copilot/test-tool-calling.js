// Test direct OpenAI tool calling with new models
// This tests that o3, gpt-5 etc can call tools properly

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const tools = [
  {
    type: "function",
    function: {
      name: "get_weather",
      description: "Get the current weather in a location",
      parameters: {
        type: "object",
        properties: {
          location: {
            type: "string",
            description: "The city and state, e.g. San Francisco, CA"
          }
        },
        required: ["location"],
        additionalProperties: false
      }
    }
  }
];

async function testModel(modelName) {
  console.log(`\n🧪 Testing ${modelName}...`);
  
  try {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${OPENAI_API_KEY}`,
      },
      body: JSON.stringify({
        model: modelName,
        messages: [
          {
            role: "system",
            content: "You are a helpful assistant."
          },
          {
            role: "user",
            content: "What's the weather like in New York?"
          }
        ],
        tools: tools,
        tool_choice: "auto",
        stream: false
      }),
    });

    if (!response.ok) {
      const error = await response.text();
      console.error(`❌ ${modelName} failed:`, error);
      return false;
    }

    const data = await response.json();
    
    // Check if the model made a tool call
    const toolCalls = data.choices[0].message.tool_calls;
    if (toolCalls && toolCalls.length > 0) {
      console.log(`✅ ${modelName} successfully called tool:`, toolCalls[0].function.name);
      console.log(`   Arguments:`, toolCalls[0].function.arguments);
      return true;
    } else {
      console.log(`⚠️  ${modelName} did not call any tools`);
      return false;
    }
  } catch (error) {
    console.error(`❌ ${modelName} error:`, error.message);
    return false;
  }
}

async function runTests() {
  console.log('Testing OpenAI Tool Calling with New Models');
  console.log('==========================================');
  
  const models = ['o3', 'o3-deep-research', 'o4-mini-deep-research', 'gpt-5'];
  
  for (const model of models) {
    await testModel(model);
    // Small delay between tests
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  console.log('\n✨ Testing complete!');
}

// Load env vars and run tests
require('dotenv').config({ path: '.env.local' });
runTests();