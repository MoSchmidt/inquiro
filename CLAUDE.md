# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Inquiro is an AI-powered research discovery platform that matches user research interests with relevant scientific papers using semantic ranking. It uses SPECTER2 embeddings for paper similarity and pgvector for vector search.

## Development Commands

### Database
```bash
docker compose up -d      # Start PostgreSQL with pgvector
```

### Backend (from /backend directory)
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt    # Includes ruff and pre-commit
pre-commit install                      # Setup git hooks for linting
uvicorn app.main:app --reload          # Start dev server on :8000
```

Requires `dev.env` file (copy from `.env.example`).

### Frontend (from /frontend directory)
```bash
npm install
npm run dev              # Start Vite dev server on :5173
npm run lint             # ESLint check
npm run lint:fix         # ESLint fix
npm run format           # Prettier
npm run build            # Production build
```

### API Client Generation
```bash
cd openapi
python generate.py       # Regenerates frontend/src/api/ from OpenAPI spec
```
Requires Docker. Generates TypeScript Axios client from FastAPI OpenAPI schema.

## Architecture

### Backend (FastAPI + SQLAlchemy async)
- `app/main.py` - FastAPI app entry point, registers all routers
- `app/core/config.py` - Settings via pydantic-settings (loads from `dev.env`)
- `app/core/database.py` - Async SQLAlchemy engine, session factory, Base model
- `app/routes/` - API endpoint handlers (auth, users, papers, projects, search)
- `app/services/` - Business logic layer
- `app/repositories/` - Database access layer
- `app/models/` - SQLAlchemy ORM models
- `app/schemas/` - Pydantic DTOs (*_dto.py)
- `app/llm/embeddings/specter2.py` - SPECTER2 embeddings for semantic paper search
- `app/llm/openai/` - OpenAI integration for paper summaries
- `ingestion/` - Scripts for ingesting papers from arXiv

Database: PostgreSQL 18 with pgvector extension for vector similarity search.

### Frontend (Vue 3 + TypeScript)
- Uses Composition API with `<script setup>`
- `src/api/` - Auto-generated Axios client from OpenAPI (do not edit manually)
- `src/services/` - Service wrappers around API client
- `src/stores/` - Pinia stores with persistence (auth uses sessionStorage)
- `src/components/` - Atomic design: atoms, molecules, organisms, templates
- `src/pages/` - Route-level page components
- `src/composables/` - Reusable composition functions (useTheme, useScrollToTop)
- UI: Vuetify 3 + Tailwind CSS + Lucide icons

### API Communication
Frontend API types are generated from backend OpenAPI schema. When backend endpoints change:
1. Update backend routes/schemas
2. Run `python openapi/generate.py` to regenerate frontend types

## Code Style

### Backend
- Ruff for linting and formatting (configured in pyproject.toml)
- Line length: 100 characters
- Pre-commit hooks run ruff on commit

### Frontend
- ESLint + Prettier
- Husky + lint-staged for pre-commit hooks
