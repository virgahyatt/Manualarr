import requests
from typing import Optional, Tuple

class ProductLookupService:
    def lookup(self, barcode: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Lookup product by barcode using OpenProductsFacts.
        Returns (brand, model/product_name).
        """
        try:
            url = f"https://world.openproductsfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    product = data.get("product", {})
                    brand = product.get("brands", "").split(",")[0].strip()
                    # Product name often contains the model or is descriptive
                    product_name = product.get("product_name", "")
                    
                    # Try to extract a model code if possible, but product name is a good start
                    return brand, product_name
            return None, None
        except Exception as e:
            print(f"Barcode lookup failed: {e}")
            return None, None
