# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dify plugin that integrates Google Search via the Google Custom Search JSON API (`google-api-python-client` SDK). Provides two tools: web search and image search. Built with Python 3.12 using the `dify-plugin` framework.

## Commands

```bash
# Install dependencies
poetry install

# Format code (black, 100-char line length)
poetry run black . -C -l 100

# Lint and auto-fix
poetry run ruff check --fix

# Format + lint together
poetry run black . -C -l 100 && poetry run ruff check --fix

# Run the plugin
poetry run python main.py
```

There are no automated tests in this project.

## Architecture

**Entry point:** `main.py` creates a `Plugin(DifyPluginEnv())` instance and calls `plugin.run()`.

**Plugin registration** is driven by YAML configs:
- `manifest.yaml` → declares the plugin and points to `provider/google.yaml`
- `provider/google.yaml` → defines `google_api_key` and `google_cx_id` credentials, registers both tool YAML files
- `tools/google_search.yaml` and `tools/google_image_search.yaml` → declare tool parameters, labels, and UI metadata

**Provider** (`provider/google.py`): `GoogleProvider` extends `dify_plugin.ToolProvider`. Validates credentials by making a test API call via `googleapiclient.discovery.build('customsearch', 'v1', ...)`.

**Tools** (in `tools/`): Both `GoogleSearchTool` and `GoogleImageSearchTool` extend `dify_plugin.Tool` and implement `_invoke()` as a generator yielding `ToolInvokeMessage` objects. They use `service.cse().list().execute()` from the Google API Python client. Image search uses `searchType="image"` on the same endpoint.

**Dual output format:** Web search returns JSON (for Chatflow/Workflow nodes) and XML-formatted text (for Agent mode, controlled by the `as_agent_tool` parameter). Image search returns markdown + JSON with image metadata.

**Shared utilities** (`tools/utils.py`):
- `SearchRef` / `InstantSearchResponse` — Pydantic models for structured results
- `to_refs()` — parses Google CSE `items[]` array into `SearchRef` list
- `VALID_COUNTRIES` / `VALID_LANGUAGES` — sets loaded at module level from `google-countries.json` and `google-languages.json` for input validation

## Key Conventions

- Tool parameters and credentials are declared in YAML files, not in Python code. Adding a new parameter means editing the corresponding `.yaml` file.
- Python source files for providers/tools are linked from YAML via the `extra.python.source` field.
- The project uses Poetry for dependency management. Dependencies are declared in `pyproject.toml`.
- Google CSE returns max 10 results per request. The `num` parameter is capped at 10.
