# OpenAPI Generator

This directory contains the tooling to generate a TypeScript Axios client from the FastAPI backend's OpenAPI specification.

## Overview

The generator performs two main tasks:

1. **Extract OpenAPI Schema** - Imports the FastAPI application and generates the OpenAPI JSON specification
2. **Generate TypeScript Client** - Uses OpenAPI Generator CLI (via Docker) to create a typed Axios client

## Prerequisites

- **Python 3.x** with the backend dependencies installed
- **Docker** - Required to run the OpenAPI Generator CLI

## Directory Structure

```
openapi/
├── README.md                 # This file
├── generate.py               # Main generator script
├── openapi.json              # Generated OpenAPI specification
└── templates/
    └── typescript-axios/
        └── baseApi.mustache  # Custom template for base API configuration
```

## Usage

Run the generator from the project root:

```bash
cd /path/to/inquiro
python openapi/generate.py
```

This will:

1. Load environment variables from `backend/dev.env`
2. Import the FastAPI app from `app.main`
3. Generate `openapi/openapi.json` from the app's routes
4. Run the OpenAPI Generator CLI via Docker
5. Output the TypeScript Axios client to `frontend/src/api/`

## Generated Output

The generator creates the following structure in `frontend/src/api/`:

```
frontend/src/api/
├── api.ts              # Aggregated API exports
├── base.ts             # Base API class with Axios configuration
├── common.ts           # Common utilities
├── configuration.ts    # API configuration options
├── index.ts            # Main entry point
├── apis/               # Generated API classes by tag
│   ├── authentication-api.ts
│   ├── users-api.ts
│   ├── projects-api.ts
│   ├── paper-api.ts
│   └── search-api.ts
└── models/             # TypeScript interfaces for request/response types
    ├── index.ts
    ├── user-create.ts
    ├── user-response.ts
    └── ...
```

## Configuration

The generator uses these settings in `generate.py`:

| Variable | Description |
|----------|-------------|
| `BACKEND_APP_IMPORT` | Python module path to FastAPI app (`app.main`) |
| `OUTPUT_SCHEMA` | Path for generated OpenAPI JSON |
| `CLIENT_OUTPUT_DIR` | Output directory for TypeScript client |

### OpenAPI Generator Options

The Docker command includes these options:

- `-g typescript-axios` - Generate TypeScript client using Axios
- `-t /local/openapi/templates/typescript-axios` - Use custom templates
- `--skip-validate-spec` - Skip OpenAPI spec validation
- `supportsES6=true` - Generate ES6 compatible code
- `withSeparateModelsAndApi=true` - Separate models and API files
- `apiPackage=apis` - Place API files in `apis/` subdirectory
- `modelPackage=models` - Place model files in `models/` subdirectory

## Custom Templates

The `templates/typescript-axios/baseApi.mustache` template customizes the base API class to:

- Use Vite's environment variable `VITE_API_BASE_URL` for the API base path
- Configure the default Axios instance

## Environment Variables

The generated client expects the following environment variable in the frontend:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Docker Permission Issues

If you encounter Docker permission errors, ensure your user is in the `docker` group:

```bash
sudo usermod -aG docker $USER
```

### Module Import Errors

If the FastAPI app fails to import, ensure:

1. You're running from the project root directory
2. Backend dependencies are installed (`pip install -r backend/requirements.txt`)
3. The `backend/dev.env` file exists with required environment variables
