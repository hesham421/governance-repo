"""
Data model for the API documentation generator.

Every field below is Optional (or an empty list/dict by default). Absence of
a value means "not discoverable from the implemented backend" — extractors
must never fabricate a value to fill a gap, and renderers must skip a
subsection entirely rather than print a placeholder for missing data.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FieldSpec:
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None
    example: Optional[str] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    format: Optional[str] = None
    enum: list[str] = field(default_factory=list)
    is_array: bool = False
    item_type: Optional[str] = None


@dataclass
class Parameter:
    name: str
    location: str  # "path" | "query" | "header"
    type: str = "string"
    required: bool = False
    description: Optional[str] = None
    example: Optional[str] = None


@dataclass
class RequestBody:
    content_type: str = "application/json"
    schema_name: Optional[str] = None
    fields: list[FieldSpec] = field(default_factory=list)


@dataclass
class ResponseVariant:
    status_code: str
    description: Optional[str] = None
    content_type: Optional[str] = None
    schema_name: Optional[str] = None
    fields: list[FieldSpec] = field(default_factory=list)
    is_array: bool = False
    is_page: bool = False


@dataclass
class Endpoint:
    method: str
    path: str
    group: Optional[str] = None          # OpenAPI tag, used to bucket endpoints
    operation_id: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    path_params: list[Parameter] = field(default_factory=list)
    query_params: list[Parameter] = field(default_factory=list)
    request_body: Optional[RequestBody] = None
    responses: list[ResponseVariant] = field(default_factory=list)
    requires_auth: Optional[bool] = None      # None = undetermined, else True/False
    security_schemes: list[str] = field(default_factory=list)
    # Populated only by security_extractor.py, only when --source is given.
    permission: list[str] = field(default_factory=list)
    permission_source: Optional[str] = None   # "controller" | "service:<ClassName>"

    def slug(self) -> str:
        if self.operation_id:
            return self.operation_id
        cleaned = self.path.strip("/").replace("/", "-").replace("{", "").replace("}", "")
        return f"{self.method.lower()}-{cleaned}" if cleaned else self.method.lower()


@dataclass
class ErrorCode:
    name: str
    value: str
    source_file: str


@dataclass
class ResponseEnvelope:
    schema_name: str
    fields: list[FieldSpec] = field(default_factory=list)


@dataclass
class SecurityScheme:
    name: str
    type: Optional[str] = None
    scheme: Optional[str] = None
    bearer_format: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ApiDocument:
    module: str
    title: Optional[str] = None
    description: Optional[str] = None
    servers: list[str] = field(default_factory=list)
    security_schemes: list[SecurityScheme] = field(default_factory=list)
    endpoints: list[Endpoint] = field(default_factory=list)
    error_codes: list[ErrorCode] = field(default_factory=list)
    response_envelope: Optional[ResponseEnvelope] = None
    pagination_envelope: Optional[ResponseEnvelope] = None

    def groups(self) -> list[str]:
        seen: list[str] = []
        for ep in self.endpoints:
            g = ep.group or "Ungrouped"
            if g not in seen:
                seen.append(g)
        return seen
