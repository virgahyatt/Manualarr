import re
from typing import Tuple, Optional
from pypdf import PdfReader

class MetadataExtractor:
    # A small starting list of common brands. 
    # In a real app, this might come from a database or external API.
    COMMON_BRANDS = {
        "Sony", "Samsung", "LG", "Panasonic", "Philips", "Toshiba", "Sharp",
        "Dell", "HP", "Lenovo", "Asus", "Acer", "Apple", "Microsoft",
        "Whirlpool", "GE", "Bosch", "Siemens", "Electrolux", "Maytag", "KitchenAid",
        "Dyson", "Shark", "Ninja", "Instant Pot", "Cuisinart", "Breville",
        "Canon", "Nikon", "Brother", "Epson", "Logitech", "Razer", "Corsair"
    }

    MODEL_PATTERNS = [
        r"Model\s*[:#]?\s*([A-Za-z0-9\-]+)",
        r"M/N\s*[:.]?\s*([A-Za-z0-9\-]+)",
        r"Series\s*([A-Za-z0-9\-]+)",
        # Heuristic: prominent uppercase alphanumeric codes often appearing alone or with specific prefixes
        r"\b([A-Z]{2,}[0-9]+[A-Z0-9\-]*)\b" 
    ]

    def extract(self, file_path: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extracts Brand and Model from a PDF file.
        Returns (brand, model).
        """
        try:
            reader = PdfReader(file_path)
            # Analyze only the first 3 pages where metadata usually lives
            text = ""
            for i in range(min(3, len(reader.pages))):
                page_text = reader.pages[i].extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return self._analyze_text(text)
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return None, None

    def _analyze_text(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        brand = self._find_brand(text)
        model = self._find_model(text)
        return brand, model

    def _find_brand(self, text: str) -> Optional[str]:
        # Simple case-insensitive match against known brands
        # We prioritize the first one found, or maybe the most frequent?
        # Let's return the first one found in the text for now.
        text_lower = text.lower()
        for brand in self.COMMON_BRANDS:
            if brand.lower() in text_lower:
                # Basic check: ensure it's a whole word match
                pattern = r"\b" + re.escape(brand.lower()) + r"\b"
                if re.search(pattern, text_lower):
                    return brand
        return None

    def _find_model(self, text: str) -> Optional[str]:
        for pattern in self.MODEL_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
