import json

from fastmcp import FastMCP

from servers.openapi_specification.schemas.helper_functions.schema_helpers import get_schema_dependencies

openapi_actions_server = FastMCP("OpenAPI - Actions")


def _load_openapi_spec(openapi_json_path: str) -> dict:
    """Read and parse an OpenAPI spec from a local JSON file.

    Args:
        openapi_json_path: Filesystem path to the openapi.json file to read.

    Returns:
        The full OpenAPI spec as a dict.

    Raises:
        FileNotFoundError: If no file exists at the given path.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    with open(openapi_json_path, encoding="utf-8") as spec_file:
        return json.load(spec_file)


@openapi_actions_server.tool()
def get_openapi_spec(openapi_json_path: str) -> dict:
    """Fetch the entire OpenAPI specification as a parsed dict.

    Args:
        openapi_json_path: Filesystem path to the openapi.json file to read.

    Returns:
        The full OpenAPI spec as a dict, including all paths, components, and metadata.

    Raises:
        FileNotFoundError: If no file exists at the given path.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    return _load_openapi_spec(openapi_json_path)


@openapi_actions_server.tool()
def list_api_paths(openapi_json_path: str) -> list[dict]:
    """List all API paths and their HTTP methods from an OpenAPI spec.

    Args:
        openapi_json_path: Filesystem path to the openapi.json file to read.

    Returns:
        A list of dicts, each with keys: api_path, api_method, summary.
        Example: [{"api_path": "/api/v1/users", "api_method": "get", "summary": "List users"}]

    Raises:
        FileNotFoundError: If no file exists at the given path.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    openapi_dict = _load_openapi_spec(openapi_json_path)

    api_list = []
    for path, path_attributes in openapi_dict["paths"].items():
        for api_method in path_attributes.keys():
            api_list.append({
                "api_path": path,
                "api_method": api_method,
                "summary": openapi_dict["paths"][path][api_method].get("summary", ""),
            })
    return api_list


@openapi_actions_server.tool()
def get_api_details(openapi_json_path: str, api_path: str, api_method: str) -> dict:
    """Get the full details of a specific API endpoint.

    Returns the complete OpenAPI definition for the given path and method, including
    request parameters, request body schema, and all response schemas.

    Args:
        openapi_json_path: Filesystem path to the openapi.json file to read.
        api_path: The API path, e.g. "/api/v1/users/{userId}".
        api_method: The HTTP method, e.g. "get", "post", "delete" (case-insensitive).

    Returns:
        A dict with the full endpoint definition: parameters, requestBody, responses, etc.

    Raises:
        ValueError: If the path or method is not found in the spec.
        FileNotFoundError: If no file exists at the given path.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    openapi_paths = _load_openapi_spec(openapi_json_path)["paths"]

    if api_path not in openapi_paths:
        raise ValueError(f"Path '{api_path}' not found in spec. Use list_api_paths to discover available paths.")

    method = api_method.lower()
    if method not in openapi_paths[api_path]:
        raise ValueError(f"Method '{api_method}' not found for path '{api_path}'.")

    return openapi_paths[api_path][method]


@openapi_actions_server.tool()
def get_schema(openapi_json_path: str, schema_name: str) -> dict:
    """Get the full definition of a named schema, including all referenced sub-schemas.

    Resolves all $ref dependencies recursively so the returned dict is self-contained
    and can be read without cross-referencing the rest of the spec.

    Args:
        openapi_json_path: Filesystem path to the openapi.json file to read.
        schema_name: The name of the schema in components/schemas, e.g. "User", "OrderResponse".

    Returns:
        A dict keyed by schema name — the requested schema plus all its dependencies.
        Example: {"User": {...}, "Address": {...}, "Role": {...}}

    Raises:
        ValueError: If schema_name is not found in components/schemas.
        FileNotFoundError: If no file exists at the given path.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    spec = _load_openapi_spec(openapi_json_path)
    openapi_schemas = spec["components"]["schemas"]

    dependencies = list(get_schema_dependencies(spec=spec, schema_name=schema_name))
    all_schemas = [schema_name] + dependencies

    return {schema: openapi_schemas[schema] for schema in all_schemas}


@openapi_actions_server.tool()
def get_api_response_schema_by_status_code(
    openapi_json_path: str,
    api_path: str,
    api_method: str,
    status_code: str,
) -> dict:
    """Get the response schema for a specific API endpoint and HTTP status code.

    Use this to inspect the exact field names and types returned by an endpoint
    for a given response status (e.g. "200", "404", "422").

    Args:
        openapi_json_path: Filesystem path to the openapi.json file to read.
        api_path: The API path, e.g. "/api/v1/users/{userId}".
        api_method: The HTTP method, e.g. "get", "post" (case-insensitive).
        status_code: The response status code as a string, e.g. "200", "404".

    Returns:
        A dict with the response definition for that status code, including
        description and content schema (may contain $ref pointers to components/schemas).

    Raises:
        ValueError: If the path, method, or status code is not found in the spec.
        FileNotFoundError: If no file exists at the given path.
        json.JSONDecodeError: If the file does not contain valid JSON.
    """
    openapi_dict = _load_openapi_spec(openapi_json_path)

    method = api_method.lower()
    paths = openapi_dict["paths"]

    if api_path not in paths:
        raise ValueError(f"Path '{api_path}' not found in spec. Use list_api_paths to discover available paths.")
    if method not in paths[api_path]:
        raise ValueError(f"Method '{api_method}' not found for path '{api_path}'.")

    responses = paths[api_path][method].get("responses", {})
    if status_code not in responses:
        available = list(responses.keys())
        raise ValueError(f"Status code '{status_code}' not found for {api_method.upper()} {api_path}. Available: {available}")

    return {status_code: responses[status_code]}
