import { openai } from '@ai-sdk/openai';
import { streamText, UIMessage, convertToModelMessages, tool, stepCountIs, generateText } from 'ai';
import { z } from 'zod';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

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

// Helper function to search knowledge base using RAG
async function searchKnowledgeBase(query: string) {
  try {
    const apiUrl = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
    
    const ragResults = await callFastAPI(
      `${apiUrl}/rag/search`,
      'POST',
      { query, top_k: 5 }
    );

    return ragResults;
  } catch (error) {
    console.error('Knowledge base search failed:', error);
    return {
      context_chunks: [],
      personality_summary: "",
      total_matches: 0,
      error: "Knowledge base unavailable"
    };
  }
}

export async function POST(req: Request) {
  const { messages }: { messages: UIMessage[] } = await req.json();

  const result = streamText({
    model: openai('gpt-4o-mini'),
    messages: convertToModelMessages(messages),
    system: `You are a YouTube creator with a distinctive personality based on your video content. 
    
    IMPORTANT: Before answering ANY question, you MUST search your knowledge base to find relevant personality information and content that helps you respond authentically.
    
    When you find relevant context from your knowledge base:
    1. Use the personality traits and speaking style to inform your response tone
    2. Reference specific examples or content when relevant
    3. Maintain consistency with your established personality
    
    Information from your knowledge base takes precedence over general knowledge. Always respond as yourself based on your content and personality.`,
    stopWhen: stepCountIs(5),
    tools: {
      searchKnowledgeBase: tool({
        description: 'Search your knowledge base for relevant content and personality information to inform your response. Always use this tool on the first request in a conversation.',
        inputSchema: z.object({
          query: z.string().describe('The search query to find relevant personality information and content'),
        }),
        execute: async ({ query }) => {
          const results = await searchKnowledgeBase(query);
          console.log('searchKnowledgeBase tool called:', query);
          console.log('RAG results:', results);
          
          // Format the results for the LLM
          let formattedResults: {
            found_relevant_content: boolean;
            personality_summary: any;
            relevant_chunks: any[];
            error?: string;
          } = {
            found_relevant_content: results.total_matches > 0,
            personality_summary: results.personality_summary,
            relevant_chunks: results.context_chunks?.slice(0, 3).map((chunk: any) => ({
              content: chunk.chunk_text?.substring(0, 300) + "...",
              relevance_score: chunk.relevance_score,
              topics: chunk.topics,
              speaking_style: chunk.speaking_style
            })) || []
          };
          
          if (results.error) {
            formattedResults.error = results.error;
            formattedResults.found_relevant_content = false;
          }
          
          return formattedResults;
        },
      }),
    },
    onStepFinish: async (step) => {
      console.log('Step completed');
      
      if (step.toolCalls) {
        step.toolCalls.forEach((toolCall) => {
          console.log('Tool called:', toolCall.toolName);
          console.log('Tool input:', toolCall.input);
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