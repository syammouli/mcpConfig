from typing import Any, Set


def get_schema_dependencies(spec: dict, schema_name: str) -> Set[str]:
    schemas = spec.get("components", {}).get("schemas", {})
    if schema_name not in schemas:
        raise ValueError(f"Schema '{schema_name}' not found in components.schemas")

    dependencies: Set[str] = set()
    visited_schemas: Set[str] = {schema_name}
    stack: list[Any] = [schemas[schema_name]]

    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                ref_schema = ref.split("/")[-1]
                dependencies.add(ref_schema)
                if ref_schema not in visited_schemas and ref_schema in schemas:
                    visited_schemas.add(ref_schema)
                    stack.append(schemas[ref_schema])
            for value in node.values():
                stack.append(value)
        elif isinstance(node, list):
            for item in node:
                stack.append(item)

    dependencies.discard(schema_name)
    return dependencies


def get_schema_dependencies_with_recursion(spec: dict, schema_name: str) -> Set[str]:
    schemas = spec.get("components", {}).get("schemas", {})
    if schema_name not in schemas:
        raise ValueError(f"Schema '{schema_name}' not found in components.schemas")

    dependencies: Set[str] = set()
    visited: Set[str] = set()

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
                ref_schema = ref.split("/")[-1]
                if ref_schema not in dependencies:
                    dependencies.add(ref_schema)
                if ref_schema not in visited:
                    visited.add(ref_schema)
                    target = schemas.get(ref_schema)
                    if target is not None:
                        walk(target)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    visited.add(schema_name)
    walk(schemas[schema_name])
    dependencies.discard(schema_name)
    return dependencies
