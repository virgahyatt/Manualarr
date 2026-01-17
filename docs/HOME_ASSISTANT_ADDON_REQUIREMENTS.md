# Home Assistant Add-on Requirements

## Overview

Package Manualarr as an all-in-one Home Assistant add-on that allows users to:
1. Store and index product manuals (PDFs)
2. Search manual contents via a web UI
3. Expose manual search as a tool for Home Assistant's AI conversation agents

## Goals

- **Easy installation**: Single add-on install from HACS or community add-on repository
- **Zero configuration**: Works out of the box with sensible defaults
- **LLM integration**: Automatically registers as a conversation agent tool
- **Resource efficient**: Suitable for Raspberry Pi 4+ deployments

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Home Assistant                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │            Manualarr Add-on                      │    │
│  │  ┌─────────────┐  ┌─────────────┐               │    │
│  │  │   Backend   │  │  Frontend   │               │    │
│  │  │  (FastAPI)  │  │  (nginx)    │               │    │
│  │  │  Port 8000  │  │  Port 80    │               │    │
│  │  └──────┬──────┘  └─────────────┘               │    │
│  │         │                                        │    │
│  │  ┌──────▼──────┐                                │    │
│  │  │   SQLite    │                                │    │
│  │  │  + FTS5     │                                │    │
│  │  └─────────────┘                                │    │
│  └─────────────────────────────────────────────────┘    │
│                         │                                │
│                         ▼                                │
│  ┌─────────────────────────────────────────────────┐    │
│  │         Conversation Agent Integration           │    │
│  │  (Exposes search_manuals tool to LLM agents)    │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

## Components

### 1. Add-on Container

Single Docker container running:
- **Supervisor**: s6-overlay or similar to manage processes
- **Backend**: FastAPI application (uvicorn)
- **Frontend**: nginx serving static files + reverse proxy to backend
- **Database**: SQLite with FTS5 stored in persistent volume

### 2. Conversation Agent Integration

The add-on registers a tool with Home Assistant's conversation agent system:

```yaml
tool:
  name: search_manuals
  description: >
    Search product manuals for specifications, instructions,
    troubleshooting steps, or other information. Use this when
    the user asks about their devices, appliances, or equipment.
  parameters:
    query:
      type: string
      description: Search terms (e.g., "max temperature", "error codes")
      required: true
    brand:
      type: string
      description: Filter by brand name (e.g., "ECO-WORTHY", "Eco-Spa")
      required: false
    model:
      type: string
      description: Filter by model number
      required: false
```

### 3. Ingress Support

- Web UI accessible via Home Assistant's ingress (sidebar integration)
- No need to expose additional ports externally
- Authentication handled by Home Assistant

## User Flow

### Installation
1. User adds Manualarr repository to HACS or Add-on Store
2. User clicks Install
3. Add-on starts and is accessible from HA sidebar

### Adding Manuals
1. User opens Manualarr from HA sidebar
2. Uploads PDF or imports from Internet Archive
3. Manual is indexed automatically (background task)

### Using with AI Assistant
1. User asks Home Assistant: "What's the max temperature for my hot tub?"
2. LLM conversation agent calls `search_manuals` tool with query
3. Tool returns relevant snippets from indexed manuals
4. LLM formulates answer using the retrieved context

## Configuration Options

```yaml
# Add-on configuration (config.yaml)
name: Manualarr
description: Product manual library with AI search
version: "1.0.0"
slug: manualarr
arch:
  - aarch64
  - amd64
  - armv7

# User-configurable options
options:
  log_level: info
  max_search_results: 10

schema:
  log_level: list(debug|info|warning|error)
  max_search_results: int(1,50)

# Ingress configuration
ingress: true
ingress_port: 8080
ingress_stream: true
panel_icon: mdi:book-open-page-variant
panel_title: Manuals

# Storage
map:
  - share:rw       # For manual PDF storage
  - config:ro      # Read HA config if needed

# Ports (optional external access)
ports:
  8080/tcp: null   # Disabled by default, use ingress
```

## API Endpoints

Existing Manualarr API endpoints to be used:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/manuals/` | GET | List all manuals |
| `/api/manuals/` | POST | Upload new manual |
| `/api/manuals/{id}` | DELETE | Delete manual |
| `/api/manuals/search` | GET | Search Internet Archive |
| `/api/manuals/import` | POST | Import from URL |
| `/api/search/context` | GET | **Primary LLM endpoint** - Full-text search |

### LLM Integration Endpoint

The `/api/search/context` endpoint is designed for LLM consumption:

**Request:**
```
GET /api/search/context?q=temperature+limit&brand=Eco-Spa&limit=5
```

**Response:**
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

## Resource Requirements

### Minimum
- **RAM**: 512MB available (Pi 4 2GB with HA)
- **Storage**: 100MB for add-on + space for PDFs
- **CPU**: Any HA-supported platform

### Recommended
- **RAM**: 1GB available
- **Storage**: SSD recommended for faster PDF indexing

### Performance Notes
- PDF indexing is CPU/memory intensive but happens once per manual
- Search queries are lightweight (SQLite FTS)
- Idle memory footprint: ~50-80MB

## Implementation Phases

### Phase 1: Basic Add-on
- [ ] Create add-on repository structure
- [ ] Dockerfile combining frontend + backend
- [ ] s6-overlay process supervision
- [ ] Basic config.yaml for HA add-on
- [ ] Ingress support for web UI
- [ ] Persistent storage for database and PDFs

### Phase 2: Conversation Integration
- [ ] Research HA conversation agent tool registration
- [ ] Implement tool registration on add-on startup
- [ ] Test with Extended OpenAI Conversation
- [ ] Test with local LLM (Ollama)
- [ ] Test with Google Generative AI

### Phase 3: Polish
- [ ] Add-on icon and branding
- [ ] Documentation
- [ ] HACS repository setup
- [ ] Community add-on store submission (optional)

## File Structure

```
manualarr-ha-addon/
├── manualarr/
│   ├── config.yaml          # Add-on configuration
│   ├── Dockerfile           # Combined container
│   ├── rootfs/
│   │   ├── etc/
│   │   │   ├── s6-overlay/  # Process supervision
│   │   │   └── nginx/       # nginx config
│   │   └── app/
│   │       ├── backend/     # FastAPI app
│   │       └── frontend/    # Built static files
│   ├── icon.png
│   ├── logo.png
│   └── DOCS.md
├── repository.yaml          # Add-on repository metadata
└── README.md
```

## Open Questions

1. **Conversation agent registration**: How to programmatically register tools with HA's conversation system? May require a companion custom component.

2. **Authentication**: Should the API require authentication when accessed outside of ingress?

3. **Multi-instance**: Support for multiple Manualarr instances (e.g., per-user manual libraries)?

4. **Backup integration**: Include database in HA backups automatically?

## References

- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons)
- [Home Assistant Conversation Agents](https://developers.home-assistant.io/docs/core/entity/conversation/)
- [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation)
- [s6-overlay](https://github.com/just-containers/s6-overlay)
