import { openai } from '@ai-sdk/openai';
import { streamText, UIMessage, convertToModelMessages, tool, stepCountIs, generateText } from 'ai';
import { z } from 'zod';

// Allow streaming responses up to 30 seconds
export const maxDuration = 30;

// Types based on serialize_result from pinecone_retriever.py
interface SearchResult {
  video_id: string;
  chunk_index: string | number;
  creator_id: string;
  text: string;
  score: number | null;
}

interface FormattedSearchResults {
  found_relevant_content: boolean;
  relevant_chunks: FormattedChunk[];
  total_matches: number;
  error?: string;
}

interface FormattedChunk {
  content: string;
  relevance_score: number | null;
  video_id: string;
  chunk_index: string | number;
}

async function callFastAPI(endpoint: string, method: 'GET' | 'POST' = 'GET', data?: unknown) {
  try {
    let url = endpoint;
    let body = undefined;

    if (method === 'GET' && data) {
      const params = new URLSearchParams();
      Object.entries(data as Record<string, any>).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params.append(key, String(value));
        }
      });
      url = `${endpoint}?${params.toString()}`;
    } else if (method === 'POST' && data) {
      body = JSON.stringify(data);
    }

    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body,
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

async function searchKnowledgeBase(query: string, creatorId: string): Promise<SearchResult[]> {
  try {
    const apiUrl = process.env.FASTAPI_BASE_URL || 'http://localhost:8000';
    
    const results = await callFastAPI(
      `${apiUrl}/retrieve_pinecone_data`,
      'GET',
      { creator_id: creatorId, search_query: query }
    ) as SearchResult[];
    console.log('searchKnowledgeBase results:', results);
    return results;
  } catch (error) {
    console.error('Knowledge base search failed:', error);
    return [];
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
          const creator_id = "t3dotgg";
          const results = await searchKnowledgeBase(query, creator_id);
          console.log('searchKnowledgeBase tool called:', query, 'for creator:', creator_id);
          console.log('RAG results:', results);
          
          // Format the results for the LLM - results is an array of search results
          const isValidResults = Array.isArray(results) && results.length > 0;
          
          const formattedResults: FormattedSearchResults = {
            found_relevant_content: isValidResults,
            total_matches: isValidResults ? results.length : 0,
            relevant_chunks: isValidResults ? results.slice(0, 3).map((chunk: SearchResult): FormattedChunk => ({
              content: chunk.text !== "N/A" ? chunk.text.substring(0, 300) + "..." : "No content available",
              relevance_score: chunk.score,
              video_id: chunk.video_id,
              chunk_index: chunk.chunk_index
            })) : []
          };
          
          if (!isValidResults && !Array.isArray(results)) {
            formattedResults.error = "Failed to retrieve knowledge base results";
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
