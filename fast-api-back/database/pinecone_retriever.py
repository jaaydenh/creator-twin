from config.pinecone_config import settings
from pinecone import Pinecone

def semantic_search_by_creator(creator_id: str, search_query: str, min_score_threshold: float = 0.5):
    """
    Performs a semantic search across video content by a specific creator using metadata filtering,
    with an optional minimum score threshold.

    Args:
        creator_id (str): The ID of the creator.
        search_query (str): The search query.
        min_score_threshold (float): The minimum score threshold to include results.
    """
    if not settings:
        print("Settings not loaded. Cannot proceed with Pinecone initialization.")
        return []

    pc = None
    try:
        pc = Pinecone(api_key=settings.pinecone_api_key)
        print("Pinecone client initialized.")
    except Exception as e:
        print(f"An error occurred during Pinecone initialization: {e}")
        return []

    all_results = []
    dense_index = None
    sparse_index = None
    try:
        dense_index = pc.Index(name='character')
        print(f"Connected to Pinecone dense index: character")

        sparse_index = pc.Index(name='character-sparse')
        print(f"Connected to Pinecone sparse index: character-sparse")

        creator_filter = {"creator_id": {"$eq": creator_id}}

        retrieve_fields = ["text", "video_id", "chunk_index", "creator_id"]


        try:
            print(f"Performing dense search for creator ID: {creator_id}")
            dense_results = dense_index.search(
                namespace=settings.pinecone_namespace,
                query={
                    "inputs": {"text": search_query},
                    "top_k": settings.pinecone_top_k,
                    "filter": creator_filter,
                },
                fields=retrieve_fields
            )
            if hasattr(dense_results, 'result') and dense_results.result and hasattr(dense_results.result, 'hits'):
                all_results.extend(dense_results.result.hits)
            else:
                 print("Warning: Dense search response does not contain search results in the expected '.result.hits' format.")
                 print(f"Dense response type: {type(dense_results)}")
                 print(f"Dense response structure (first 1000 chars): {str(dense_results)[:1000]}")


        except Exception as e:
            print(f"An error occurred during dense Pinecone search for creator ID {creator_id}: {e}")
            print(f"Full Dense Response Object: {dense_results}")


        try:
            print(f"Performing sparse search for creator ID: {creator_id}")
            sparse_results = sparse_index.search(
                namespace=settings.pinecone_namespace,
                query={
                    "inputs": {"text": search_query},
                    "top_k": settings.pinecone_top_k,
                    "filter": creator_filter,
                },
                fields=retrieve_fields
            )
            if hasattr(sparse_results, 'result') and sparse_results.result and hasattr(sparse_results.result, 'hits'):
                all_results.extend(sparse_results.result.hits)
            else:
                print("Warning: Sparse search response does not contain search results in the expected '.result.hits' format.")
                print(f"Sparse response type: {type(sparse_results)}")
                print(f"Sparse response structure (first 1000 chars): {str(sparse_results)[:1000]}")


        except Exception as e:
            print(f"An error occurred during sparse Pinecone search for creator ID {creator_id}: {e}")
            print(f"Full Sparse Response Object: {sparse_results}")


    except Exception as e:
        print(f"An error occurred during Pinecone index connection: {e}")
    finally:
        pass

    filtered_results = [result for result in all_results if hasattr(result, '_score') and result._score >= min_score_threshold]


    try:
        filtered_results.sort(key=lambda x: x._score, reverse=True)
    except Exception as e:
        print(f"Error during sorting filtered results: {e}")
        print("Could not sort filtered results. Please examine the debugging output above to understand the structure of items in all_results.")


    top_n_results = filtered_results[:5]


    print(f"\n--- Combined Search Results (Top {len(top_n_results)} after filtering and sorting) ---")
    if not top_n_results:
        print("No relevant results found for the given creator and query above the minimum score threshold.")
    else:
        for result in top_n_results:
            try:
                fields = result.get('fields', {})
                video_id = fields.get('video_id', 'N/A')
                chunk_index = fields.get('chunk_index', 'N/A')
                result_creator_id = fields.get('creator_id', 'N/A')
                text = fields.get('text', 'N/A')

                score = result._score


                print(f"Video ID: {video_id}, Creator ID: {result_creator_id}, Score: {score:.4f}, Text: {text}")
            except Exception as e:
                print(f"Error processing search result: {e}")
                print(f"Problematic result object: {result}")


    return top_n_results


