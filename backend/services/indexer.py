import fitz  # pymupdf
import numpy as np
import json
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastembed import TextEmbedding
from typing import List, Dict, Any

class IndexerService:
    def __init__(self):
        # Initialize the embedding model. This will download once on first run.
        # BAAI/bge-small-en-v1.5 is very efficient for Pi 5.
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def index_manual(self, db: Session, manual_id: int, file_path: str):
        """
        Extracts text from the PDF, chunks it, generates embeddings, 
        and indexes it into both FTS and vector tables.
        """
        try:
            doc = fitz.open(file_path)
            print(f"Indexing manual {manual_id}: {file_path}")
            
            # Clear existing index for this manual
            db.execute(text("DELETE FROM manual_fts WHERE manual_id = :mid"), {"mid": manual_id})
            db.execute(text("DELETE FROM manual_embeddings WHERE manual_id = :mid"), {"mid": manual_id})
            
            all_chunks = []
            pages_indexed = 0
            total_chars = 0
            
            for page_num, page in enumerate(doc):
                content = page.get_text()
                if not content.strip():
                    continue
                
                # 1. Index in FTS (for exact keyword matches)
                db.execute(
                    text("INSERT INTO manual_fts (manual_id, page_number, content) VALUES (:mid, :pn, :content)"),
                    {"mid": manual_id, "pn": page_num + 1, "content": content}
                )
                
                # 2. Prepare for Semantic Indexing
                # Simple chunking by paragraph/newlines to keep context
                chunks = [c.strip() for c in content.split('\n\n') if len(c.strip()) > 20]
                for i, chunk in enumerate(chunks):
                    all_chunks.append({
                        "manual_id": manual_id,
                        "page_number": page_num + 1,
                        "chunk_index": i,
                        "content": chunk
                    })
                
                pages_indexed += 1
                total_chars += len(content)
            
            # Generate and store embeddings in batches
            if all_chunks:
                chunk_texts = [c["content"] for c in all_chunks]
                embeddings = list(self.embedding_model.embed(chunk_texts))
                
                for i, chunk in enumerate(all_chunks):
                    # Convert numpy array to bytes for storage
                    emb_bytes = embeddings[i].tobytes()
                    db.execute(
                        text("""
                            INSERT INTO manual_embeddings (manual_id, page_number, chunk_index, content, embedding)
                            VALUES (:mid, :pn, :ci, :content, :emb)
                        """),
                        {
                            "mid": chunk["manual_id"],
                            "pn": chunk["page_number"],
                            "ci": chunk["chunk_index"],
                            "content": chunk["content"],
                            "emb": emb_bytes
                        }
                    )
            
            db.commit()
            doc.close()
            print(f"Successfully indexed manual {manual_id}: {pages_indexed} pages, {len(all_chunks)} semantic chunks.")
            return True
        except Exception as e:
            db.rollback()
            print(f"Indexing failed for manual {manual_id}: {e}")
            return False

    def delete_manual_index(self, db: Session, manual_id: int):
        db.execute(text("DELETE FROM manual_fts WHERE manual_id = :mid"), {"mid": manual_id})
        db.execute(text("DELETE FROM manual_embeddings WHERE manual_id = :mid"), {"mid": manual_id})
        db.commit()

    def search(self, db: Session, query: str, brand: str = None, model: str = None, limit: int = 10):
        """
        Hybrid search combining FTS and Semantic similarity.
        """
        # 1. Get Semantic Results
        semantic_results = self._semantic_search(db, query, brand, model, limit)
        
        # 2. Get FTS Results
        fts_results = self._fts_search(db, query, brand, model, limit)
        
        # 3. Combine and Deduplicate (Prioritize Semantic for quality, FTS for exactness)
        # In a true RAG, we'd use Reciprocal Rank Fusion, but for a Pi 5 we'll keep it simple:
        # We merge them, keeping the best rank for each unique page/snippet.
        combined = []
        seen = set() # (manual_id, page_number)
        
        for res in semantic_results:
            key = (res["manual_id"], res["page_number"])
            if key not in seen:
                combined.append(res)
                seen.add(key)
        
        for res in fts_results:
            key = (res["manual_id"], res["page_number"])
            if key not in seen:
                combined.append(res)
                seen.add(key)
                
        return combined[:limit]

    def _semantic_search(self, db: Session, query: str, brand: str, model: str, limit: int):
        # Generate embedding for the query
        query_embedding = list(self.embedding_model.embed([query]))[0]
        
        # Fetch all candidate embeddings (optionally filtered by brand/model)
        # Note: On a Pi 5 with small collections, brute force cosine similarity in Python is fast.
        # For larger collections, we'd use a dedicated vector index.
        sql = """
            SELECT e.manual_id, e.page_number, e.content, e.embedding, m.brand, m.model, m.filename
            FROM manual_embeddings e
            JOIN manuals m ON m.id = e.manual_id
            WHERE 1=1
        """
        params = {}
        
        if brand and brand.strip() and brand.lower() not in ['none', 'null', 'undefined', '']:
            sql += " AND m.brand LIKE :brand"
            params["brand"] = f"%{brand}%"
        if model and model.strip() and model.lower() not in ['none', 'null', 'undefined', '']:
            sql += " AND m.model LIKE :model"
            params["model"] = f"%{model}%"
            
        rows = db.execute(text(sql), params).fetchall()
        
        if not rows:
            return []
            
        results = []
        for row in rows:
            # Reconstruct numpy array from blob
            emb = np.frombuffer(row.embedding, dtype=np.float32)
            # Simple Cosine Similarity (dot product since BGE embeddings are normalized)
            score = np.dot(query_embedding, emb)
            
            results.append({
                "manual_id": row.manual_id,
                "brand": row.brand,
                "model": row.model,
                "filename": row.filename,
                "page_number": row.page_number,
                "snippet": row.content,
                "score": float(score)
            })
            
        # Sort by similarity score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]

    def _fts_search(self, db: Session, query: str, brand: str, model: str, limit: int):
        words = ''.join(e for e in query if e.isalnum() or e.isspace()).split()
        if not words:
            return []
        
        fts_query = ' AND '.join(words)
        sql = """
            SELECT 
                m.id as manual_id, m.brand, m.model, m.filename,
                fts.page_number,
                snippet(manual_fts, 2, '<b>', '</b>', '...', 128) as snippet
            FROM manual_fts fts
            JOIN manuals m ON m.id = fts.manual_id
            WHERE manual_fts MATCH :query
        """
        params = {"query": fts_query}
        
        if brand and brand.strip() and brand.lower() not in ['none', 'null', 'undefined', '']:
            sql += " AND m.brand LIKE :brand"
            params["brand"] = f"%{brand}%"
        if model and model.strip() and model.lower() not in ['none', 'null', 'undefined', '']:
            sql += " AND m.model LIKE :model"
            params["model"] = f"%{model}%"
            
        sql += " ORDER BY rank LIMIT :limit"
        params["limit"] = limit
        
        result = db.execute(text(sql), params)
        return [dict(row._mapping) for row in result]