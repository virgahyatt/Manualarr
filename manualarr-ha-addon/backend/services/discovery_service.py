from typing import List, Dict, Optional
from internetarchive import search_items, get_item
import requests
import os

class DiscoveryService:
    def search(self, brand: str, model: str) -> List[Dict]:
        """
        Search for manuals on Internet Archive.
        Returns a list of candidates:
        [
            {
                "source": "Internet Archive",
                "title": "Sony WH-1000XM4 User Manual",
                "identifier": "sony-wh-1000xm4-manual",
                "filename": "manual.pdf",
                "url": "https://archive.org/download/...",
                "cover_url": "..." (optional)
            },
            ...
        ]
        """
        candidates = []
        
        # Construct queries
        # 1. Precise: Brand + Model + collection:manuals
        queries = [
            f'title:({brand} {model}) AND collection:manuals',
            f'({brand} {model}) AND collection:manuals', # Search full text in collection
            f'title:({brand} {model}) AND mediatype:texts' # Broader
        ]
        
        seen_identifiers = set()
        
        for query in queries:
            if len(candidates) >= 10:
                break
                
            try:
                print(f"Searching IA: {query}")
                results = search_items(query)
                
                for result in results:
                    identifier = result['identifier']
                    if identifier in seen_identifiers:
                        continue
                    
                    if len(candidates) >= 10:
                        break

                    # Inspect item to find PDF
                    item_candidates = self._process_item(identifier)
                    if item_candidates:
                        for cand in item_candidates:
                            candidates.append(cand)
                            seen_identifiers.add(identifier)
            except Exception as e:
                print(f"Error searching IA for {query}: {e}")
                
        return candidates

    def _process_item(self, identifier: str) -> List[Dict]:
        """
        Check if an item has a PDF and return candidate info.
        """
        try:
            item = get_item(identifier)
            candidates = []
            
            # Find PDF files
            pdf_files = [f for f in item.files if f['name'].lower().endswith('.pdf')]
            
            if not pdf_files:
                return []
                
            # Pick the best PDF (largest? or named 'manual'?)
            # For now, return all PDFs or the largest one. 
            # Often items have 'orig.pdf' and 'text.pdf'. Usually we want the original.
            
            # Simple heuristic: ignore 'text.pdf' if others exist.
            valid_pdfs = [f for f in pdf_files if '_text.pdf' not in f['name']]
            if not valid_pdfs:
                valid_pdfs = pdf_files
                
            for file in valid_pdfs:
                filename = file['name']
                download_url = f"https://archive.org/download/{identifier}/{filename}"
                
                candidates.append({
                    "source": "Internet Archive",
                    "title": item.metadata.get('title', identifier),
                    "identifier": identifier,
                    "filename": filename,
                    "url": download_url,
                    "size": int(file.get('size', 0))
                })
                
            return candidates
        except Exception as e:
            print(f"Error processing item {identifier}: {e}")
            return []

    def download(self, url: str, dest_path: str) -> bool:
        """
        Download a file from a URL to a local path.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Download failed: {e}")
            if os.path.exists(dest_path):
                os.remove(dest_path)
            return False
