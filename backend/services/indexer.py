import fitz  # pymupdf
from sqlalchemy.orm import Session
from sqlalchemy import text

class IndexerService:
    def index_manual(self, db: Session, manual_id: int, file_path: str):
        """
        Extracts text from the PDF and indexes it into the FTS table.
        """
        try:
            doc = fitz.open(file_path)
            
            # Clear existing index for this manual
            db.execute(text("DELETE FROM manual_fts WHERE manual_id = :mid"), {"mid": manual_id})
            
            for page_num, page in enumerate(doc):
                content = page.get_text()
                if content.strip():
                    db.execute(
                        text("INSERT INTO manual_fts (manual_id, page_number, content) VALUES (:mid, :pn, :content)"),
                        {"mid": manual_id, "pn": page_num + 1, "content": content}
                    )
            
            db.commit()
            doc.close()
            return True
        except Exception as e:
            print(f"Indexing failed for manual {manual_id}: {e}")
            return False

    def delete_manual_index(self, db: Session, manual_id: int):
        db.execute(text("DELETE FROM manual_fts WHERE manual_id = :mid"), {"mid": manual_id})
        db.commit()

    def search(self, db: Session, query: str, brand: str = None, model: str = None, limit: int = 10):
        """
        Search for text snippets. Optionally filter by brand/model.
        """
        # Format query for FTS5 (simple word AND join)
        # Remove special chars that might break syntax
        clean_query = ''.join(e for e in query if e.isalnum() or e.isspace())
        fts_query = ' AND '.join(clean_query.split())
        
        if not fts_query:
            return []

        sql = """
            SELECT 
                m.id as manual_id,
                m.brand,
                m.model,
                m.filename,
                fts.page_number,
                snippet(manual_fts, 2, '<b>', '</b>', '...', 64) as snippet
            FROM manual_fts fts
            JOIN manuals m ON m.id = fts.manual_id
            WHERE manual_fts MATCH :query
        """
        
        params = {"query": fts_query}
        
        # Use fuzzy matching for brand/model (strip hyphens and spaces)
        # This allows "ecoworthy" to match "Eco-Worthy" or "Eco Worthy"
        if brand and brand.strip():
            clean_brand = ''.join(e for e in brand if e.isalnum())
            if clean_brand:
                sql += " AND REPLACE(REPLACE(m.brand, '-', ''), ' ', '') LIKE :brand"
                params["brand"] = f"%{clean_brand}%"
            
        if model and model.strip():
            clean_model = ''.join(e for e in model if e.isalnum())
            if clean_model:
                sql += " AND REPLACE(REPLACE(m.model, '-', ''), ' ', '') LIKE :model"
                params["model"] = f"%{clean_model}%"
            
        sql += " ORDER BY rank LIMIT :limit"
        params["limit"] = limit
        
        result = db.execute(text(sql), params)
        return [dict(row._mapping) for row in result]
