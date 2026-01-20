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
            print(f"Indexing manual {manual_id}: {file_path}")
            
            # Clear existing index for this manual
            db.execute(text("DELETE FROM manual_fts WHERE manual_id = :mid"), {"mid": manual_id})
            
            pages_indexed = 0
            total_chars = 0
            for page_num, page in enumerate(doc):
                content = page.get_text()
                if content.strip():
                    db.execute(
                        text("INSERT INTO manual_fts (manual_id, page_number, content) VALUES (:mid, :pn, :content)"),
                        {"mid": manual_id, "pn": page_num + 1, "content": content}
                    )
                    pages_indexed += 1
                    total_chars += len(content)
            
            db.commit()
            doc.close()
            print(f"Successfully indexed manual {manual_id}: {pages_indexed} pages, {total_chars} characters.")
            if total_chars == 0:
                print(f"WARNING: No text extracted from manual {manual_id}. Is it a scanned image?")
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
        # Try precise search (AND) first, then fallback to loose search (OR)
        words = ''.join(e for e in query if e.isalnum() or e.isspace()).split()
        if not words:
            return []

        results = self._execute_search(db, ' AND '.join(words), brand, model, limit)
        
        if not results and len(words) > 1:
            print(f"No results for precise search '{query}', trying loose search...")
            results = self._execute_search(db, ' OR '.join(words), brand, model, limit)
            
        return results

    def _execute_search(self, db: Session, fts_query: str, brand: str, model: str, limit: int):
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
        
        print(f"Executing search: FTS='{fts_query}' Brand='{brand}' Model='{model}'")
        result = db.execute(text(sql), params)
        rows = [dict(row._mapping) for row in result]
        print(f"Search found {len(rows)} results.")
        return rows
