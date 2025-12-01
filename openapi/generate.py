import importlib
import json
import subprocess
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

# --- ENV SETUP ---
BACKEND_ENV = Path(__file__).parent.parent / "backend" / "dev.env"
if BACKEND_ENV.exists():
    load_dotenv(BACKEND_ENV)
    print(f"Loaded environment from {BACKEND_ENV}")
else:
    print(f"WARNING: No environment file found at {BACKEND_ENV}")

# --- CONFIG ---
ROOT = Path(__file__).parent.parent
BACKEND_APP_IMPORT = "app.main"  # FastAPI module
OUTPUT_SCHEMA = Path(__file__).parent / "openapi.json"
CLIENT_OUTPUT_DIR = ROOT / "frontend" / "src" / "api"


def find_fastapi_app(module):
    """Search module attributes to find the FastAPI instance."""
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, FastAPI):
            return attr
    raise RuntimeError("No FastAPI instance found in the module.")


def generate_openapi_schema():
    print("=== 1. Generating OpenAPI schema from FastAPI ===")

    module = importlib.import_module(BACKEND_APP_IMPORT)
    app = find_fastapi_app(module)

    schema = get_openapi(
        title=getattr(app, "title", "API"),
        version=getattr(app, "version", "1.0.0"),
        description=getattr(app, "description", ""),
        routes=app.routes,
    )

    OUTPUT_SCHEMA.write_text(json.dumps(schema, indent=2))
    print(f"OpenAPI schema written to: {OUTPUT_SCHEMA}")


def generate_typescript_client_docker():
    print("=== 2. Generating TypeScript Axios client using DOCKER ===")

    cmd = [
        "docker", "run", "--rm",
        "-v", f"{ROOT}:/local",
        "openapitools/openapi-generator-cli",
        "generate",
        "-i", "/local/openapi/openapi.json",
        "-g", "typescript-axios",
        "-o", "/local/frontend/src/api",
        "-t", "/local/openapi/templates/typescript-axios",
        "--skip-validate-spec",
        "--global-property=apiDocs=false,modelDocs=false,apiTests=false,modelTests=false",
        "--additional-properties="
        "supportsES6=true,"
        "withSeparateModelsAndApi=true,"
        "apiPackage=apis,"
        "modelPackage=models"
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    print(f"Axios client generated in {CLIENT_OUTPUT_DIR}")


if __name__ == "__main__":
    generate_openapi_schema()
    generate_typescript_client_docker()
    print("=== DONE ===")
