#!/usr/bin/env python3
"""
Hybrid Search Module for Shadowrun GM
Combines vector similarity search (OpenAI embeddings + pgvector) 
with PostgreSQL full-text search using Reciprocal Rank Fusion (RRF)

Ported from server-unified.js to Python
"""
import os
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
import psycopg
from openai import OpenAI

load_dotenv()


class HybridSearch:
    """
    Hybrid search combining vector similarity and keyword search
    """
    
    def __init__(self, conn: psycopg.Connection):
        """
        Initialize hybrid search
        
        Args:
            conn: PostgreSQL connection with pgvector extension enabled
        """
        self.conn = conn
        self.openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Register pgvector type
        try:
            from pgvector.psycopg import register_vector
            register_vector(conn)
        except ImportError:
            print("Warning: pgvector not installed. Vector search will not work.")
            print("Install with: pip install pgvector")
    
    def generate_embedding(self, query: str) -> List[float]:
        """
        Generate OpenAI embedding for a query
        
        Args:
            query: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.openai.embeddings.create(
                model='text-embedding-3-small',
                input=query
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Error generating embedding: {e}")
            raise
    
    def vector_search(
        self, 
        query: str, 
        categories: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search using pgvector
        
        Args:
            query: Search query
            categories: Optional list of categories to filter by
            content_types: Optional list of content types to filter by
            limit: Maximum number of results
            
        Returns:
            List of result dictionaries with similarity scores
        """
        # Generate embedding for query
        embedding = self.generate_embedding(query)
        
        # Build SQL query
        sql = """
            SELECT 
                id,
                title,
                content,
                category,
                subcategory,
                tags,
                content_type,
                source_file,
                1 - (embedding <=> %s::vector) as similarity_score
            FROM rules_content
            WHERE embedding IS NOT NULL
        """
        
        params = [embedding]
        param_count = 1
        
        # Add category filter
        if categories:
            param_count += 1
            sql += f" AND category = ANY(%s)"
            params.append(categories)
        
        # Add content type filter
        if content_types:
            param_count += 1
            sql += f" AND content_type = ANY(%s)"
            params.append(content_types)
        
        # Order by similarity (lower distance = higher similarity)
        sql += f" ORDER BY embedding <=> %s::vector LIMIT %s"
        params.append(embedding)
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        
        # Convert to list of dicts
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            result = dict(zip(columns, row))
            results.append(result)
        
        cursor.close()
        return results
    
    def keyword_search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        PostgreSQL full-text search
        
        Args:
            query: Search query
            categories: Optional list of categories to filter by
            content_types: Optional list of content types to filter by
            limit: Maximum number of results
            
        Returns:
            List of result dictionaries with rank scores
        """
        sql = """
            SELECT 
                id,
                title,
                content,
                category,
                subcategory,
                tags,
                content_type,
                source_file,
                ts_rank(
                    to_tsvector('english', title || ' ' || content),
                    plainto_tsquery('english', %s)
                ) as rank
            FROM rules_content
            WHERE to_tsvector('english', title || ' ' || content) 
                  @@ plainto_tsquery('english', %s)
        """
        
        params = [query, query]
        param_count = 2
        
        # Add category filter
        if categories:
            param_count += 1
            sql += f" AND category = ANY(%s)"
            params.append(categories)
        
        # Add content type filter
        if content_types:
            param_count += 1
            sql += f" AND content_type = ANY(%s)"
            params.append(content_types)
        
        sql += f" ORDER BY rank DESC LIMIT %s"
        params.append(limit)
        
        cursor = self.conn.cursor()
        cursor.execute(sql, params)
        
        # Convert to list of dicts
        columns = [desc[0] for desc in cursor.description]
        results = []
        for row in cursor.fetchall():
            result = dict(zip(columns, row))
            results.append(result)
        
        cursor.close()
        return results
    
    def reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        k: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Combine results using Reciprocal Rank Fusion (RRF)
        
        RRF formula: score = sum(1 / (k + rank)) for each result list
        
        Args:
            vector_results: Results from vector search
            keyword_results: Results from keyword search
            k: Constant for RRF (default 60)
            
        Returns:
            Fused and sorted results
        """
        scores = {}
        
        # Score vector results (rank 1 = highest score)
        for rank, result in enumerate(vector_results, start=1):
            result_id = result['id']
            score = 1 / (k + rank)
            
            scores[result_id] = {
                **result,
                'rrf_score': score,
                'vector_rank': rank,
                'vector_score': result.get('similarity_score', 0)
            }
        
        # Add keyword results (boost if already in vector results)
        for rank, result in enumerate(keyword_results, start=1):
            result_id = result['id']
            score = 1 / (k + rank)
            
            if result_id in scores:
                # Item in both results - add scores
                scores[result_id]['rrf_score'] += score
                scores[result_id]['keyword_rank'] = rank
                scores[result_id]['keyword_score'] = result.get('rank', 0)
            else:
                # Only in keyword results
                scores[result_id] = {
                    **result,
                    'rrf_score': score,
                    'keyword_rank': rank,
                    'keyword_score': result.get('rank', 0)
                }
        
        # Sort by combined RRF score (highest first)
        fused_results = sorted(
            scores.values(),
            key=lambda x: x['rrf_score'],
            reverse=True
        )
        
        return fused_results
    
    def hybrid_search(
        self,
        query: str,
        categories: Optional[List[str]] = None,
        content_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and keyword search
        
        Args:
            query: Search query
            categories: Optional list of categories to filter by
            content_types: Optional list of content types to filter by
            limit: Maximum number of final results
            
        Returns:
            Fused and ranked results
        """
        try:
            # Run both searches (get more results for better fusion)
            vector_results = self.vector_search(
                query, 
                categories=categories,
                content_types=content_types,
                limit=20
            )
            
            keyword_results = self.keyword_search(
                query,
                categories=categories,
                content_types=content_types,
                limit=20
            )
            
            # Fuse results using RRF
            fused_results = self.reciprocal_rank_fusion(
                vector_results,
                keyword_results
            )
            
            # Return top N
            return fused_results[:limit]
            
        except Exception as e:
            print(f"Hybrid search error: {e}")
            print("Falling back to keyword-only search")
            # Fallback to keyword search if vector search fails
            return self.keyword_search(
                query,
                categories=categories,
                content_types=content_types,
                limit=limit
            )
    
    def search_spells(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for spell information in rules content
        
        Args:
            query: Spell name or description
            limit: Maximum results
            
        Returns:
            Spell-related content chunks
        """
        return self.hybrid_search(
            query,
            categories=['magic'],
            content_types=['rule_mechanic', 'stat_block'],
            limit=limit
        )
    
    def search_gear(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for gear/equipment information
        
        Args:
            query: Gear name or type
            limit: Maximum results
            
        Returns:
            Gear-related content chunks
        """
        return self.hybrid_search(
            query,
            categories=['gear_mechanics'],
            content_types=['stat_block', 'table'],
            limit=limit
        )
    
    def search_rules(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for game rules and mechanics
        
        Args:
            query: Rule or mechanic description
            limit: Maximum results
            
        Returns:
            Rules-related content chunks
        """
        return self.hybrid_search(
            query,
            content_types=['rule_mechanic', 'table'],
            limit=limit
        )
    
    def search_lore(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for lore and setting information
        
        Args:
            query: Lore topic
            limit: Maximum results
            
        Returns:
            Lore-related content chunks
        """
        return self.hybrid_search(
            query,
            content_types=['flavor_text', 'introduction'],
            limit=limit
        )


# Convenience function for quick searches
def quick_search(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Quick hybrid search with default connection
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        Search results
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    conn = psycopg.connect(
        host=os.getenv('POSTGRES_HOST', '127.0.0.1'),
        port=int(os.getenv('POSTGRES_PORT', '5434')),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD'),
        dbname=os.getenv('POSTGRES_DB', 'postgres')
    )
    
    try:
        searcher = HybridSearch(conn)
        return searcher.hybrid_search(query, limit=limit)
    finally:
        conn.close()


if __name__ == "__main__":
    # Test the hybrid search
    print("Testing Hybrid Search...")
    print("=" * 80)
    
    results = quick_search("initiative combat", limit=3)
    
    print(f"\nFound {len(results)} results:\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   Category: {result['category']}")
        print(f"   RRF Score: {result['rrf_score']:.4f}")
        if 'vector_rank' in result:
            print(f"   Vector Rank: {result['vector_rank']}")
        if 'keyword_rank' in result:
            print(f"   Keyword Rank: {result['keyword_rank']}")
        print(f"   Content: {result['content'][:200]}...")
        print()
