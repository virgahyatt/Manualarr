# Home Assistant Add-on Requirements

## Overview

Package Manualarr as an all-in-one Home Assistant add-on that allows users to:
1. Store and index product manuals (PDFs)
2. Search manual contents via a web UI
3. Expose manual search as a tool for Home Assistant's AI conversation agents

## Goals

- **Easy installation**: Single add-on install from HACS or community add-on repository
- **Zero configuration**: Works out of the box with sensible defaults
- **LLM integration**: Provides config templates for popular AI assistants
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

## AI Assistant Configuration Templates

The add-on provides ready-to-use configuration templates for popular Home Assistant AI assistants. Users copy the appropriate config into their assistant setup.

### Extended OpenAI Conversation (HACS)

Works with OpenAI, Azure OpenAI, and OpenAI-compatible APIs (Ollama, LocalAI, etc.)

```yaml
# Add to Extended OpenAI Conversation configuration
functions:
  - spec:
      name: search_manuals
      description: >-
        Search product manuals for specifications, instructions, troubleshooting,
        or any other information. Use this when the user asks about their devices,
        appliances, equipment, or products they own.
      parameters:
        type: object
        properties:
          query:
            type: string
            description: >-
              Search terms to find in manuals (e.g., "max temperature",
              "error code E3", "installation steps", "warranty period")
          brand:
            type: string
            description: >-
              Optional brand filter (e.g., "ECO-WORTHY", "Eco-Spa", "Samsung")
          model:
            type: string
            description: >-
              Optional model number filter (e.g., "E3", "ECO-LFP4810002")
        required:
          - query
    function:
      type: rest
      resource: http://homeassistant.local:8081/api/search/context
      method: GET
      value_template: >-
        {% set params = {"q": query, "limit": 5} %}
        {% if brand is defined and brand %}{% set _ = params.update({"brand": brand}) %}{% endif %}
        {% if model is defined and model %}{% set _ = params.update({"model": model}) %}{% endif %}
        {{ params | to_json }}
```

### Google Generative AI Conversation

For Google Gemini models with function calling support.

```yaml
# configuration.yaml
conversation:
  - platform: google_generative_ai_conversation
    # ... other config ...

# Note: Google Generative AI integration requires custom component
# modification to add external tool support. See docs for workaround
# using a script + REST command approach below.
```

**Alternative using Scripts + REST:**

```yaml
# configuration.yaml
rest_command:
  search_manuals:
    url: "http://homeassistant.local:8081/api/search/context"
    method: GET
    query_params:
      q: "{{ query }}"
      brand: "{{ brand | default('') }}"
      model: "{{ model | default('') }}"
      limit: 5
    content_type: "application/json"

# Expose as a script the assistant can reference in prompts
script:
  search_product_manuals:
    alias: "Search Product Manuals"
    description: "Search indexed product manuals for information"
    fields:
      query:
        description: "Search terms"
        required: true
        selector:
          text:
      brand:
        description: "Brand filter (optional)"
        selector:
          text:
    sequence:
      - service: rest_command.search_manuals
        data:
          query: "{{ query }}"
          brand: "{{ brand | default('') }}"
```

### Ollama / Local LLM (via Open WebUI or LLM integration)

For local models running via Ollama.

```yaml
# If using Extended OpenAI Conversation pointed at Ollama:
# Use the Extended OpenAI Conversation config above with base_url:
#   base_url: http://localhost:11434/v1

# If using Home Assistant Ollama integration directly,
# function calling support depends on the model. Models that
# support tools include:
#   - llama3.1 (8B, 70B)
#   - mistral (with function calling)
#   - command-r
#
# Configure using Extended OpenAI Conversation template above.
```

### OpenAI Conversation (Built-in)

The built-in OpenAI Conversation integration has limited tool support. Recommended approach is to use Extended OpenAI Conversation (HACS) instead for full function calling.

```yaml
# For basic integration without function calling,
# add context about available manuals to the system prompt:

conversation:
  - platform: openai_conversation
    api_key: !secret openai_api_key
    # Add manual awareness to prompt
    prompt: >-
      You are a helpful home assistant. The user has product manuals
      indexed in their Manualarr system. If they ask about product
      specifications or instructions, tell them you'll check their
      manuals and suggest they ask: "Search my manuals for [topic]"

      Available manuals can be searched at:
      http://homeassistant.local:8081
```

### Custom LLM / Other Assistants

For any assistant that supports HTTP/REST tool calling:

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
curl "http://homeassistant.local:8081/api/search/context?q=max+temperature&brand=Eco-Spa&limit=5"
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

**Tool Description for LLM:**
```
Use this tool to search the user's product manual library. Returns relevant
excerpts from PDF manuals including the page number and context. Call this
when users ask about:
- Product specifications (dimensions, capacity, power ratings)
- Operating instructions or procedures
- Safety warnings or limits
- Troubleshooting or error codes
- Warranty or maintenance information
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

### Phase 2: Assistant Configuration Templates
- [ ] Create Extended OpenAI Conversation template
- [ ] Create Google Generative AI workaround template
- [ ] Create Ollama/local LLM template
- [ ] Test each template with real assistant setup
- [ ] Document template usage in DOCS.md

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
├── assistant-configs/        # Ready-to-use config templates
│   ├── README.md            # Which template to use
│   ├── extended-openai-conversation.yaml
│   ├── google-generative-ai.yaml
│   ├── ollama-local-llm.yaml
│   └── generic-rest-tool.md
├── repository.yaml          # Add-on repository metadata
└── README.md
```

## Open Questions

1. **Authentication**: Should the API require authentication when accessed outside of ingress?

2. **Multi-instance**: Support for multiple Manualarr instances (e.g., per-user manual libraries)?

3. **Backup integration**: Include database in HA backups automatically?

4. **Template updates**: How to notify users when assistant config templates are updated? Consider versioning templates.

## References

- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons)
- [Home Assistant Conversation Agents](https://developers.home-assistant.io/docs/core/entity/conversation/)
- [Extended OpenAI Conversation](https://github.com/jekalmin/extended_openai_conversation)
- [s6-overlay](https://github.com/just-containers/s6-overlay)
