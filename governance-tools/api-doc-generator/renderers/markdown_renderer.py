"""
Markdown renderer: one index.md (module overview + shared sections) plus one
file per endpoint under endpoints/<group>/<slug>.md. Every subsection is
conditional on data actually being present — nothing here invents content;
absent data just means the subsection doesn't get written.
"""

import json
import re

from models.api_doc_model import ApiDocument, Endpoint, ErrorCode, FieldSpec, Parameter, ResponseEnvelope
from renderers.base import Renderer


def _slugify(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9]+", "-", text.strip()).strip("-").lower()
    return text or "root"


def _constraints_text(f: FieldSpec) -> str:
    parts = []
    if f.max_length is not None:
        parts.append(f"maxLength: {f.max_length}")
    if f.min_length not in (None, 0):
        parts.append(f"minLength: {f.min_length}")
    if f.pattern:
        parts.append(f"pattern: `{f.pattern}`")
    if f.enum:
        parts.append(f"enum: {', '.join(f.enum)}")
    return "; ".join(parts)


def _field_table(fields: list[FieldSpec]) -> str:
    if not fields:
        return ""
    has_examples = any(f.example for f in fields)
    header = ["Field", "Type", "Required", "Constraints", "Description"]
    if has_examples:
        header.append("Example")
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    for f in fields:
        row = [f.name, f.type, "Yes" if f.required else "No", _constraints_text(f), f.description or ""]
        if has_examples:
            row.append(f.example or "")
        lines.append("| " + " | ".join(c.replace("\n", " ") for c in row) + " |")
    return "\n".join(lines)


def _param_table(params: list[Parameter]) -> str:
    if not params:
        return ""
    lines = [
        "| Name | Type | Required | Description |",
        "|---|---|---|---|",
    ]
    for p in params:
        lines.append(f"| {p.name} | {p.type} | {'Yes' if p.required else 'No'} | {p.description or ''} |")
    return "\n".join(lines)


def _example_json(fields: list[FieldSpec]) -> str:
    obj = {}
    for f in fields:
        if not f.example:
            continue
        try:
            obj[f.name] = json.loads(f.example)
        except (json.JSONDecodeError, TypeError):
            obj[f.name] = f.example
    if not obj:
        return ""
    return "```json\n" + json.dumps(obj, indent=2, ensure_ascii=False) + "\n```"


def _envelope_section(title: str, envelope: ResponseEnvelope | None) -> str:
    if not envelope:
        return ""
    parts = [f"## {title}", ""]
    if envelope.schema_name:
        parts.append(f"Schema: `{envelope.schema_name}`")
        parts.append("")
    table = _field_table(envelope.fields)
    if table:
        parts.append(table)
        parts.append("")
    return "\n".join(parts)


def _error_codes_section(codes: list[ErrorCode]) -> str:
    if not codes:
        return ""
    lines = ["## Known Error Codes", "", "| Code | Value | Source |", "|---|---|---|"]
    for c in codes:
        lines.append(f"| {c.name} | `{c.value}` | {c.source_file} |")
    lines.append("")
    return "\n".join(lines)


def _auth_section(ep: Endpoint) -> str:
    lines = ["**Authentication**", ""]
    if ep.requires_auth is None:
        lines.append("Not determined from the OpenAPI document.")
    elif ep.requires_auth:
        schemes = ", ".join(ep.security_schemes) if ep.security_schemes else "unspecified scheme"
        lines.append(f"Required ({schemes}).")
    else:
        lines.append("Not required.")
    if ep.permission:
        source = f" (found on {ep.permission_source})" if ep.permission_source else ""
        lines.append("")
        lines.append(f"**Required permission(s)**: {', '.join(ep.permission)}{source}")
    lines.append("")
    return "\n".join(lines)


def _endpoint_markdown(ep: Endpoint) -> str:
    parts = [f"# {ep.method} {ep.path}", ""]
    if ep.summary:
        parts.append(f"**{ep.summary}**")
        parts.append("")
    if ep.description:
        parts.append(ep.description)
        parts.append("")
    if ep.operation_id:
        parts.append(f"Operation ID: `{ep.operation_id}`")
        parts.append("")

    parts.append(_auth_section(ep))

    path_table = _param_table(ep.path_params)
    if path_table:
        parts += ["## Path Parameters", "", path_table, ""]

    query_table = _param_table(ep.query_params)
    if query_table:
        parts += ["## Query Parameters", "", query_table, ""]

    if ep.request_body:
        parts.append("## Request Body")
        parts.append("")
        if ep.request_body.schema_name:
            parts.append(f"Schema: `{ep.request_body.schema_name}` ({ep.request_body.content_type})")
            parts.append("")
        table = _field_table(ep.request_body.fields)
        if table:
            parts.append(table)
            parts.append("")
        example = _example_json(ep.request_body.fields)
        if example:
            parts.append("**Request Example**")
            parts.append("")
            parts.append(example)
            parts.append("")

    for resp in ep.responses:
        parts.append(f"## Response `{resp.status_code}`" + (f" — {resp.description}" if resp.description else ""))
        parts.append("")
        if resp.schema_name:
            shape = resp.schema_name
            if resp.is_array:
                shape = f"array of {shape}"
            elif resp.is_page:
                shape = f"paginated list of {shape} (see Pagination Envelope in index.md)"
            parts.append(f"Shape: `{shape}`")
            parts.append("")
        table = _field_table(resp.fields)
        if table:
            parts.append(table)
            parts.append("")
        example = _example_json(resp.fields)
        if example:
            parts.append("**Response Example**")
            parts.append("")
            parts.append(example)
            parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def _catalog_table(endpoints: list[Endpoint], group: str) -> str:
    lines = ["| Method | Path | Summary | Doc |", "|---|---|---|---|"]
    for ep in endpoints:
        if (ep.group or "Ungrouped") != group:
            continue
        link = f"endpoints/{_slugify(group)}/{ep.slug()}.md"
        lines.append(f"| {ep.method} | `{ep.path}` | {ep.summary or ''} | [{ep.slug()}]({link}) |")
    return "\n".join(lines)


def _index_markdown(doc: ApiDocument) -> str:
    parts = [f"# {doc.module} API Documentation", ""]
    if doc.title:
        parts.append(f"_{doc.title}_")
        parts.append("")
    if doc.description:
        parts.append(doc.description)
        parts.append("")

    if doc.servers:
        parts.append("## Servers")
        parts.append("")
        for s in doc.servers:
            parts.append(f"- {s}")
        parts.append("")

    if doc.security_schemes:
        parts.append("## Authentication")
        parts.append("")
        for s in doc.security_schemes:
            desc = f" — {s.description}" if s.description else ""
            kind = s.scheme or s.type or ""
            fmt = f" ({s.bearer_format})" if s.bearer_format else ""
            parts.append(f"- **{s.name}**: {kind}{fmt}{desc}")
        parts.append("")

    parts.append(_envelope_section("Common Response Envelope", doc.response_envelope))
    parts.append(_envelope_section("Pagination Envelope", doc.pagination_envelope))
    parts.append(_error_codes_section(doc.error_codes))

    parts.append("## API Catalog")
    parts.append("")
    for group in doc.groups():
        parts.append(f"### {group}")
        parts.append("")
        parts.append(_catalog_table(doc.endpoints, group))
        parts.append("")

    return "\n".join(p for p in parts if p is not None).strip() + "\n"


class MarkdownRenderer(Renderer):

    def render(self, document: ApiDocument) -> dict[str, str]:
        files: dict[str, str] = {"index.md": _index_markdown(document)}
        for ep in document.endpoints:
            group_slug = _slugify(ep.group or "Ungrouped")
            files[f"endpoints/{group_slug}/{ep.slug()}.md"] = _endpoint_markdown(ep)
        return files
