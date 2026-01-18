import requests
from typing import Optional, Tuple
from pyzbar.pyzbar import decode
from PIL import Image
import io

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

    def scan_barcode(self, image_data: bytes) -> Tuple[Optional[str], Optional[str]]:
        """
        Scan an image for barcodes and look up the first one found.
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            barcodes = decode(image)
            
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                brand, model = self.lookup(barcode_data)
                if brand or model:
                    return brand, model
            
            return None, None
        except Exception as e:
            print(f"Barcode scanning failed: {e}")
            return None, None
