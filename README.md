# Manualarr

**Manualarr** is a self-hosted web application designed to store, organize, and retrieve user manuals for appliances and products. It runs on Docker (target: Asustor 6604T) and features automated manual discovery and an LLM-friendly API.

## Features

- **Semantic Search (RAG):** Uses local embeddings (`fastembed`) to understand the meaning of your queries, not just keywords.
- **Hybrid Search Engine:** Combines SQLite FTS5 with vector similarity for high-precision results.
- **Privacy First:** All embedding generation and searching happens locally on your hardware.
- **Barcode Scanning:** Automatically identify products from photos of barcodes.
- **Home Assistant Integration:** Built-in support for Home Assistant's Assist via a custom tool.
- **Mobile Friendly:** Simple UI for uploading and searching manuals on the go.


## Installation (Docker)

The simplest way to run Manualarr is using Docker.

### Prerequisites
- Docker & Docker Compose installed on your system (or NAS).

### Quick Start
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/manualarr.git
   cd manualarr
   ```

2. Run the install script:
   ```bash
   ./install.sh
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:8080
   ```
   *(Replace `localhost` with your NAS IP address if installing remotely)*

## Development

### Backend (Python/FastAPI)
```bash
cd backend
# Create venv and install deps
uv venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# Run dev server
uvicorn main:app --reload
```

### Frontend (React/Vite)
```bash
cd frontend
npm install
npm run dev
```
**Note**: In development, the frontend expects the backend at `localhost:8000`.

## Tech Stack
- **Backend**: Python (FastAPI)
- **Frontend**: React (TypeScript), Bootstrap
- **Database**: SQLite
- **Deployment**: Docker Compose, Nginx