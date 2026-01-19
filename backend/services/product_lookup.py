import requests
from typing import Optional, Tuple
from pyzbar.pyzbar import decode
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

class ProductLookupService:
    def lookup(self, barcode: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Lookup product by barcode.
        Tries OpenProductsFacts first, then UPCitemdb.
        Returns (brand, model/product_name).
        """
        # 1. Try OpenProductsFacts
        try:
            url = f"https://world.openproductsfacts.org/api/v0/product/{barcode}.json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == 1:
                    product = data.get("product", {})
                    brand = product.get("brands", "").split(",")[0].strip()
                    product_name = product.get("product_name", "")
                    if brand or product_name:
                        logger.info(f"Found in OpenProductsFacts: {brand} - {product_name}")
                        return brand, product_name
        except Exception as e:
            logger.error(f"OpenProductsFacts lookup failed: {e}")

        # 2. Try UPCitemdb (Fallback)
        try:
            # Free trial endpoint (100 req/day, no key needed)
            url = "https://api.upcitemdb.com/prod/trial/lookup"
            response = requests.get(url, params={"upc": barcode}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("total", 0) > 0:
                    item = data["items"][0]
                    brand = item.get("brand", "")
                    title = item.get("title", "")
                    # Model often hidden in title or description, but title is a good fallback for model
                    if brand or title:
                        logger.info(f"Found in UPCitemdb: {brand} - {title}")
                        return brand, title
        except Exception as e:
            logger.error(f"UPCitemdb lookup failed: {e}")

        return None, None

    def scan_barcode(self, image_data: bytes) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Scan an image for barcodes and look up the first one found.
        Returns (brand, model, raw_barcode)
        """
        try:
            image = Image.open(io.BytesIO(image_data))
            logger.info(f"Scanning image: {image.format} {image.size} {image.mode}")
            
            barcodes = decode(image)
            logger.info(f"Detected {len(barcodes)} barcodes.")
            
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                barcode_type = barcode.type
                logger.info(f"Processing barcode: {barcode_data} ({barcode_type})")
                
                brand, model = self.lookup(barcode_data)
                if brand or model:
                    logger.info(f"Match found for {barcode_data}: {brand} {model}")
                    return brand, model, barcode_data
                else:
                    logger.info(f"No product found for {barcode_data}")
                    return None, None, barcode_data
            
            return None, None, None
        except Exception as e:
            logger.error(f"Barcode scanning failed: {e}")
            return None, None, None
