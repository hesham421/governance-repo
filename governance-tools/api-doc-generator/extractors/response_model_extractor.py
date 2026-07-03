"""
Derives the shared ApiResponse<T> envelope shape once per module, so it can
be documented in a single shared section instead of being repeated on every
endpoint. The envelope is identical across the whole system (success /
message / data / error / timestamp) — only "data" varies per endpoint, and
that variation is already covered by each endpoint's own Response section.

Detection: springdoc names each generic ApiResponse<T> instantiation
differently (e.g. "ApiResponseLegalEntityResponse"), so this looks for any
schema in components.schemas matching the envelope's key set rather than a
fixed name.
"""

from typing import Optional

from extractors import dto_extractor, validation_extractor
from models.api_doc_model import FieldSpec, ResponseEnvelope


def find_envelope(openapi: dict) -> Optional[ResponseEnvelope]:
    components = openapi.get("components", {})
    schemas = components.get("schemas", {})

    envelope_name = None
    envelope_schema = None
    for name, schema in schemas.items():
        if dto_extractor.is_envelope_shape(schema):
            envelope_name, envelope_schema = name, schema
            break

    if not envelope_schema:
        return None

    def _resolve(s: dict):
        return dto_extractor.resolve_ref(s, components)

    props = envelope_schema.get("properties", {})
    fields: list[FieldSpec] = []
    for key in ("success", "message", "data", "error", "timestamp"):
        prop = props.get(key)
        if prop is None:
            continue
        if key == "data":
            fields.append(FieldSpec(name="data", type="object", description="Endpoint-specific payload — see each endpoint's Response section"))
            continue
        if key == "error":
            resolved, ref_name = _resolve(prop)
            if ref_name:
                fields.append(FieldSpec(name="error", type=ref_name, description="Present only when success=false"))
                error_props = resolved.get("properties", {})
                required = set(resolved.get("required", []))
                for err_key, err_prop in error_props.items():
                    spec = validation_extractor.build_field_spec(f"error.{err_key}", err_prop, err_key in required, _resolve)
                    fields.append(spec)
            else:
                fields.append(FieldSpec(name="error", type="object", description="Present only when success=false"))
            continue
        fields.append(validation_extractor.build_field_spec(key, prop, False, _resolve))

    return ResponseEnvelope(schema_name=envelope_name, fields=fields)
