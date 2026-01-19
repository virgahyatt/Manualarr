import re
import unicodedata
from typing import Tuple, Optional, Any, Union
from io import IOBase, BytesIO
import pymupdf

class MetadataExtractor:
    # Expanded list of brands
    COMMON_BRANDS = {
        "Sony", "Samsung", "LG", "Panasonic", "Philips", "Toshiba", "Sharp",
        "Dell", "HP", "Lenovo", "Asus", "Acer", "Apple", "Microsoft",
        "Whirlpool", "GE", "Bosch", "Siemens", "Electrolux", "Maytag", "KitchenAid",
        "Dyson", "Shark", "Ninja", "Instant Pot", "Cuisinart", "Breville",
        "Canon", "Nikon", "Brother", "Epson", "Logitech", "Razer", "Corsair",
        "ECO-WORTHY", "Renogy", "Victron", "Growatt", "Pylontech", "GoodWe", "SMA",
        "Huawei", "Fronius", "SolarEdge", "Enphase", "Fusion Pacific", "GECKO"
    }

    # Ordered patterns: Most specific first
    MODEL_PATTERNS = [
        # Explicit labels: Model: XXXXX, Model No: XXXXX, Models: XXXXX
        r"(?:Models?|Mod\.|M/N)\s*[:#\.]?\s*([A-Za-z0-9\-\.]+)",
        r"(?:Models?|Mod\.|M/N)\s*[:#\.]?\s*([A-Za-z0-9]+-[A-Za-z0-9\-]+)",
        r"Series\s*([A-Za-z0-9\-]+)",
        # Heuristic: prominent uppercase alphanumeric codes (e.g., WH-1000XM4)
        r"\b([A-Z]{2,}[-][A-Z0-9]+)\b", # Hyphenated codes like ECO-LFP...
        r"\b([A-Z]{2,}[0-9]{3,}[A-Z0-9]*)\b" # Codes like X1000...
    ]
    
    # Terms to ignore if found as model (false positives)
    IGNORE_TERMS = {"LIFEPO4", "BATTERY", "MANUAL", "LITHIUM", "V1.0", "V2.0", "VERSION", "OWNER", "INSTRUCTIONS", "SAFETY"}

    def extract(self, file_input: Union[str, IOBase, bytes]) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts Brand and Model from a PDF file (path, file-like object, or bytes).
        Returns (brand, model).
        """
        doc = None
        try:
            if isinstance(file_input, str):
                doc = pymupdf.open(file_input)
            elif isinstance(file_input, (bytes, bytearray)):
                doc = pymupdf.open(stream=file_input, filetype="pdf")
            elif isinstance(file_input, IOBase):
                # BytesIO or similar
                file_input.seek(0)
                stream_data = file_input.read()
                doc = pymupdf.open(stream=stream_data, filetype="pdf")
            else:
                return None, None

            # Analyze only the first 3 pages
            text = ""
            for i in range(min(3, len(doc))):
                page_text = doc[i].get_text()
                if page_text:
                    text += page_text + "\n"
            
            return self._analyze_text(text)
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return None, None
        finally:
            if doc:
                doc.close()

    def _analyze_text(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        # Normalize text to handle full-width characters (e.g. ： -> :)
        text = unicodedata.normalize("NFKC", text)
        
        brand = self._find_brand(text)
        model = self._find_model(text, exclude=brand)
        return brand, model

    def _find_brand(self, text: str) -> Optional[str]:
        # Simple case-insensitive match against known brands
        text_lower = text.lower()
        # Sort brands by length (descending) to match "ECO-WORTHY" before "ECO" if both existed
        sorted_brands = sorted(self.COMMON_BRANDS, key=len, reverse=True)
        
        for brand in sorted_brands:
            if brand.lower() in text_lower:
                # Use word boundary check
                pattern = r"\b" + re.escape(brand.lower()) + r"\b"
                if re.search(pattern, text_lower):
                    return brand
        return None

    def _find_model(self, text: str, exclude: Optional[str] = None) -> Optional[str]:
        for pattern in self.MODEL_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                candidate = match.group(1).strip()
                # Clean up punctuation at end if captured (like dot)
                candidate = candidate.rstrip(".")
                
                # Validation
                if len(candidate) > 2 and candidate.upper() not in self.IGNORE_TERMS:
                    # Check against exclude
                    if exclude and candidate.lower() == exclude.lower():
                        continue
                    # Ignore underscores (blank lines)
                    if "_" in candidate:
                        continue
                        
                    return candidate
        return None