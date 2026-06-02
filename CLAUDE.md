# CLAUDE.md

## Project
This project is a Python Dash app for Singapore land transport and weather insights, and is being extended into a Claude-powered mobility assistant for commuters, planners, and operators.

## Stack
- Framework/UI: Dash, Dash Bootstrap Components, Dash Leaflet, Dash DAQ
- Language/runtime: Python 3.12
- Data layer: Live API integrations (Data.gov.sg, LTA DataMall, OneMap) plus cached local files in `data/` (no primary relational database)
- Packaging/tooling: `uv`, Hatch (`pyproject.toml`), `pytest`, `pylint`
- Deployment target: Plotly Cloud (WSGI via `gunicorn`)

## Commands
- Install dependencies: `uv sync`
- Run app (recommended): `uv run app.py`
- Run app (venv active): `python app.py`
- Run tests: `uv run pytest`
- Run lint: `uv run pylint app.py callbacks components conf utils auth`


## Architecture
- `app.py` -> Dash app entrypoint, layout composition, callback registration, startup initialization
- `callbacks/` -> Dash callback registration and UI interaction orchestration per feature/tab
- `components/` -> Reusable UI builders and display components
- `utils/` -> API clients, data transforms, parsing, caching helpers, geospatial/data utilities
- `auth/` -> External service authentication flows (for example OneMap token handling)
- `conf/` -> Constants and configuration (intervals, page layout values, cache settings)
- `assets/` -> Static CSS/images used by Dash
- `data/` -> Runtime-downloaded datasets and cached local artifacts
- `tests/` -> Unit and integration tests for business logic and callback behavior

## Rules
- Keep callback functions thin; move API logic, transforms, and parsing into `utils/`.
- Preserve backwards-compatible behavior for existing dashboard tabs unless the task explicitly requests UX or behavior changes.
- Never hardcode secrets or tokens; read credentials from environment variables only.
- Validate Singapore-specific assumptions (coordinates, station/road names, transport lines) against existing data mappings before changing logic.
- IMPORTANT: Make minimal, scoped edits; do not refactor unrelated modules while implementing a feature.

## Workflow
- Ask clarifying questions before starting complex or ambiguous tasks
- Make minimal changes - DO NOT refactor unrelated code
- Run tests after every change; fix failures before moving on
- Create separate commits per logical change
- When unsure between approaches, explain both and let me choose

## Out of scope
- `.env`, production secrets, and credential values (never edit or commit them)
- External API contracts and account settings on Data.gov.sg, LTA DataMall, OneMap, and Plotly Cloud
- Large visual redesigns across all tabs unless explicitly requested for the task
- Any infrastructure or services outside this repository