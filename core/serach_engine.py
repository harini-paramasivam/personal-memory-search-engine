import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize the embedding model
try:
    model = SentenceTransformer('all-MiniLM-L6-v2')
except:
    # Fallback for demo purposes
    model = None

def search_memories(query, memories, top_k=10):
    """
    Search for memories matching the query
    
    Args:
        query (str): The search query
        memories (list): List of memory dictionaries
        top_k (int): Number of results to return
        
    Returns:
        list: Sorted list of matching memories
    """
    if not memories:
        return []
        
    # If no model is available, fall back to simple keyword matching
    if model is None:
        return keyword_search(query, memories, top_k)
        
    # Get query embedding
    query_embedding = model.encode([query])[0]
    
    # Calculate scores for each memory
    scores = []
    
    for i, memory in enumerate(memories):
        score = 0
        
        # Check title
        if 'title' in memory:
            title_embedding = model.encode([memory['title']])[0]
            title_score = cosine_similarity([query_embedding], [title_embedding])[0][0]
            score += title_score * 0.4  # Give title higher weight
        
        # Check content
        if 'content' in memory:
            # For simplicity, we'll just embed the first 200 chars of content
            content = memory['content'][:200]
            content_embedding = model.encode([content])[0]
            content_score = cosine_similarity([query_embedding], [content_embedding])[0][0]
            score += content_score * 0.6
        
        scores.append((i, score))
    
    # Sort by score and get top_k
    scores.sort(key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, _ in scores[:top_k]]
    
    # Return matched memories
    return [memories[idx] for idx in top_indices]

def keyword_search(query, memories, top_k=10):
    """
    Simple keyword-based search fallback
    
    Args:
        query (str): The search query
        memories (list): List of memory dictionaries
        top_k (int): Number of results to return
        
    Returns:
        list: Sorted list of matching memories
    """
    query_terms = query.lower().split()
    results = []
    
    for memory in memories:
        score = 0
        
        # Check title
        if 'title' in memory:
            title = memory['title'].lower()
            for term in query_terms:
                if term in title:
                    score += 10  # Higher weight for title matches
        
        # Check content
        if 'content' in memory:
            content = memory['content'].lower()
            for term in query_terms:
                score += content.count(term) * 2
        
        # Check entities
        if 'entities' in memory and memory['entities']:
            for entity in memory['entities']:
                if isinstance(entity, dict):
                    entity_text = entity.get('text', '').lower()
                else:
                    entity_text = str(entity).lower()
                    
                for term in query_terms:
                    if term in entity_text:
                        score += 5  # Higher weight for entity matches
        
        if score > 0:
            results.append((memory, score))
    
    # Sort by score
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Return top k memories
    return [memory for memory, _ in results[:top_k]]