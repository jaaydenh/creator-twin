import { openai } from '@ai-sdk/openai';
import { streamText, UIMessage, convertToModelMessages, tool, stepCountIs, generateText } from 'ai';
import { z } from 'zod';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

// Example function showing how to use tool results for additional prompts
async function processWeatherResult(location: string, temperature: number) {
  // You could make an additional LLM call based on the tool result
  const additionalContext = await generateText({
    model: openai('gpt-4o-mini'),
    prompt: `Based on the weather data for ${location} with temperature ${temperature}°F, 
             provide clothing recommendations and activity suggestions. Be concise.`,
  });
  
  return additionalContext.text;
}

// Helper function to call FastAPI endpoints
async function callFastAPI(endpoint: string, method: 'GET' | 'POST' = 'GET', data?: unknown) {
  try {
    const response = await fetch(endpoint, {
      method,
      headers: {
        'Content-Type': 'application/json',
        // Add authentication headers if needed
        // 'Authorization': `Bearer ${process.env.API_TOKEN}`,
      },
      body: data ? JSON.stringify(data) : undefined,
    });

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('FastAPI call error:', error);
    throw error;
  }
}

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  // Alternative approach: You could modify messages based on previous tool results
  // const enrichedMessages = await enrichMessagesWithContext(messages);

  const result = streamText({
    model: openai('gpt-4o-mini'),
    messages: convertToModelMessages(messages),
    stopWhen: stepCountIs(5),
    tools: {
        weather: tool({
          description: 'Get the weather in a location (fahrenheit)',
          inputSchema: z.object({
            location: z.string().describe('The location to get the weather for'),
          }),
          execute: async ({ location }) => {
            try {
              const apiUrl = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
              
              const weatherData = await callFastAPI(
                `${apiUrl}/weather?location=${encodeURIComponent(location)}`
              );
              
              return {
                location,
                temperature: weatherData.temperature,
                condition: weatherData.condition,
                humidity: weatherData.humidity,
              };
            } catch (error) {
              // Fallback to mock data if API fails
              console.error('Weather API failed, using mock data:', error);
              const temperature = Math.round(Math.random() * (90 - 32) + 32);
              return {
                location,
                temperature,
                condition: 'Unknown',
                humidity: 50,
                error: 'API unavailable, using mock data'
              };
            }
          },
        }),
      },
      onStepFinish: async (step) => {
        console.log('Step completed');
        
        if (step.toolCalls) {
          step.toolCalls.forEach((toolCall) => {
            console.log('Tool called:', toolCall.toolName);
            console.log('Tool input:', toolCall.input);
            
            // You can access the tool execution result from step.toolResults
          });
        }
        
        if (step.toolResults) {
          for (const toolResult of step.toolResults) {
            console.log('Tool result:', toolResult.output);
          }
        }
      }
  });

  return result.toUIMessageStreamResponse();
}

// Alternative approach: Enrich messages with additional context
// async function enrichMessagesWithContext(messages: UIMessage[]): Promise<UIMessage[]> {
//   const enrichedMessages = [...messages];
//   
//   // Add system message with additional context based on previous tool results
//   // You could store tool results in a database and retrieve them here
//   enrichedMessages.unshift({
//     id: 'system-context',
//     role: 'system',
//     content: 'You have access to weather data. Use it to provide helpful recommendations.'
//   });
//   
//   return enrichedMessages;
// }