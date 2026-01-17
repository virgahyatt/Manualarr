# Manualarr

**Manualarr** is a self-hosted web application designed to store, organize, and retrieve user manuals for appliances and products. It runs on Docker (target: Asustor 6604T) and features automated manual discovery and an LLM-friendly API.

## Core Features
- **Centralized Storage**: Store and manage PDF manuals locally.
- **Auto-Discovery**: Find and download manuals from online sources (e.g., Internet Archive) using Brand/Model.
- **Barcode Scanning**: Scan product barcodes to automatically identify devices and fetch manuals.
- **LLM Integration**: API endpoints optimized for Large Language Models to search and reference manual content.
- **Manual Upload**: Support for direct file uploads.

## Tech Stack
- **Backend**: Python (FastAPI)
- **Frontend**: React (TypeScript)
- **Database**: SQLite
- **Deployment**: Docker Compose

## Development
- **Branching**: `feature/*` -> `develop` -> `main`
- **Methodology**: Test-Driven Development (TDD)
