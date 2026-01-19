# Manualarr Add-on Documentation

Manualarr is a product manual library with AI search capabilities.

## Configuration

- `log_level`: Set the logging level (debug, info, warning, error).
- `max_search_results`: Maximum number of snippets to return in an AI search.

## LLM Integration

This add-on exposes a tool for Home Assistant AI Conversation Agents.
The endpoint is `/api/search/context`.

Refer to the `assistant-configs` directory in the repository for ready-to-use templates for:
- Extended OpenAI Conversation
- Google Generative AI
- Ollama / Local LLM
