# OpenAPI Specification Archive

## Migration to FastAPI

This directory previously contained the `openapi.yaml` file used by Connexion for API route generation.

With the migration to FastAPI, **the OpenAPI specification is now auto-generated** from the Python code using FastAPI decorators and type hints.

## Accessing the OpenAPI Specification

The OpenAPI specification is now available at runtime at the following endpoints:

- **JSON format**: `http://localhost:8000/openapi.json`
- **Interactive documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative documentation (ReDoc)**: `http://localhost:8000/redoc`

## Benefits of Auto-Generated OpenAPI

1. **Single Source of Truth**: API specification is derived directly from code
2. **Always in Sync**: Documentation automatically updates with code changes
3. **Type Safety**: Leverages Python type hints for validation
4. **Less Maintenance**: No need to manually keep YAML file in sync with code

## Legacy OpenAPI File

The original `openapi.yaml` file has been kept for historical reference but is **no longer used** by the application.

If you need to export the current OpenAPI specification:

```bash
# Start the server
python -m app.main

# In another terminal, download the spec
curl http://localhost:8000/openapi.json > openapi.json
```

## Migration Date

FastAPI migration completed: 2024-11-19

