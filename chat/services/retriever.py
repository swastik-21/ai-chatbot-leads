import os
import json
from typing import List, Dict, Any
from django.conf import settings
import faiss
import numpy as np


class FAISSRetriever:
    """FAISS-based retriever for RAG (Retrieval Augmented Generation)."""
    
    def __init__(self):
        self.index_path = settings.FAISS_PATH
        self.dimension = 384  # Dimension for simple embeddings
        self.index = None
        self.documents = []
        self._load_or_create_index()
    
    def _load_or_create_index(self):
        """Load existing FAISS index or create new one."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        index_file = f"{self.index_path}.index"
        docs_file = f"{self.index_path}.docs"
        
        if os.path.exists(index_file) and os.path.exists(docs_file):
            # Load existing index
            self.index = faiss.read_index(index_file)
            with open(docs_file, 'r', encoding='utf-8') as f:
                self.documents = json.load(f)
        else:
            # Create new index
            self.index = faiss.IndexFlatIP(self.dimension)  # Inner product for cosine similarity
            self.documents = []
            self._save_index()
    
    def _save_index(self):
        """Save FAISS index and documents to disk."""
        index_file = f"{self.index_path}.index"
        docs_file = f"{self.index_path}.docs"
        
        faiss.write_index(self.index, index_file)
        with open(docs_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
    
    def _simple_embedding(self, text: str) -> np.ndarray:
        """Create a simple embedding using basic text features."""
        # Simple bag-of-words style embedding
        words = text.lower().split()
        embedding = np.zeros(self.dimension)
        
        # Simple hash-based embedding
        for word in words:
            hash_val = hash(word) % self.dimension
            embedding[hash_val] += 1
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding.astype('float32')
    
    def add_documents(self, documents: List[Dict[str, str]]):
        """
        Add documents to the FAISS index.
        
        Args:
            documents: List of dicts with 'title' and 'content' keys
        """
        if not documents:
            return
        
        # Extract texts and create embeddings
        texts = []
        for doc in documents:
            text = f"{doc.get('title', '')} {doc.get('content', '')}".strip()
            texts.append(text)
        
        # Generate embeddings
        embeddings = np.array([self._simple_embedding(text) for text in texts])
        
        # Add to index
        self.index.add(embeddings)
        
        # Store documents
        self.documents.extend(documents)
        
        # Save to disk
        self._save_index()
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents with scores
        """
        if self.index.ntotal == 0:
            return []
        
        # Generate query embedding
        query_embedding = self._simple_embedding(query)
        
        # Search
        scores, indices = self.index.search(query_embedding.reshape(1, -1), top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.documents):
                doc = self.documents[idx].copy()
                doc['score'] = float(score)
                results.append(doc)
        
        return results
    
    def get_context(self, query: str, top_k: int = 3) -> str:
        """
        Get context string from relevant documents.
        
        Args:
            query: Search query
            top_k: Number of documents to include
            
        Returns:
            Formatted context string
        """
        results = self.search(query, top_k)
        
        if not results:
            return ""
        
        context_parts = []
        for i, doc in enumerate(results, 1):
            title = doc.get('title', 'Untitled')
            content = doc.get('content', '')
            context_parts.append(f"{i}. {title}: {content}")
        
        return "\n\n".join(context_parts)


# Global instance
retriever = FAISSRetriever()
