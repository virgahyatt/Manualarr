# Generic REST Tool Integration

For any assistant that supports HTTP/REST tool calling.

**Endpoint:** `GET /api/search/context`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `q` | string | Yes | Search query |
| `brand` | string | No | Filter by brand |
| `model` | string | No | Filter by model |
| `limit` | int | No | Max results (default: 10) |

**Example Request:**

```bash
curl "http://manualarr:8080/api/search/context?q=max+temperature&brand=Eco-Spa&limit=5"
```

**Example Response:**

```json
[
  {
    "manual_id": 2,
    "brand": "Eco-Spa",
    "model": "E3",
    "filename": "ECO-SPA-MANUAL.pdf",
    "page_number": 16,
    "snippet": "...temperature Set Point limit has been preset at the factory to not exceed 104°F (40°C)..."
  }
]
```
