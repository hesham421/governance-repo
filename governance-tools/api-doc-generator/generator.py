#!/usr/bin/env python3
"""
generator.py — standalone API documentation generator
════════════════════════════════════════════════════════════════════
Generates frontend-ready API documentation directly from an implemented
Spring Boot module. The ONLY source of truth is the compiled application's
OpenAPI document (springdoc-openapi) plus, optionally, its Java source for
two best-effort sections (permissions, known error codes).

No governance. No execution-plan. No comparison. No drift detection.
Works generically for any Spring Boot module — nothing here is specific to
any one module's domain.

    python3 generator.py \\
        --module ORG \\
        --openapi http://localhost:7273/api-docs/4-organization \\
        --source ../../../backend/erp-org/src/main/java \\
        --output ../../modules/ORG/api-docs/

--openapi accepts either a live http(s) URL or a local JSON file path.
--source is optional — omit it to skip the two best-effort, source-derived
sections (per-endpoint permissions, module error-code appendix); every other
section still renders fully from the OpenAPI document alone.

Design principle: every extractor either finds real metadata or leaves the
field empty. The renderer never prints a placeholder for missing data — it
omits the subsection. Nothing here is ever invented.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extractors import dto_extractor, exception_extractor, openapi_extractor, response_model_extractor, security_extractor
from models.api_doc_model import ResponseEnvelope
from renderers.markdown_renderer import MarkdownRenderer


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--module", required=True, help="Module label, e.g. ORG (used only for the doc title)")
    ap.add_argument("--openapi", required=True, help="OpenAPI JSON: local file path or http(s) URL")
    ap.add_argument("--source", help="Path to the module's src/main/java (enables permission + error-code sections)")
    ap.add_argument("--output", required=True, type=Path, help="Output directory for generated documentation")
    args = ap.parse_args()

    try:
        openapi = openapi_extractor.load_openapi(args.openapi)
    except Exception as exc:  # noqa: BLE001 - surface any load failure (network/file/JSON) to the user
        print(f"ERROR: could not load OpenAPI document from '{args.openapi}': {exc}", file=sys.stderr)
        return 1

    document = openapi_extractor.build_document(openapi, args.module)
    document.response_envelope = response_model_extractor.find_envelope(openapi)

    page_schema_name, page_fields = dto_extractor.find_page_envelope(openapi)
    if page_schema_name:
        document.pagination_envelope = ResponseEnvelope(schema_name=page_schema_name, fields=page_fields)

    if args.source:
        source_root = Path(args.source)
        if not source_root.exists():
            print(f"ERROR: --source path not found: {source_root}", file=sys.stderr)
            return 1

        document.error_codes = exception_extractor.find_error_codes(source_root)

        for ep in document.endpoints:
            controller_file, method_name = security_extractor.find_controller_for_endpoint(source_root, ep.method, ep.path)
            if not controller_file or not method_name:
                continue
            controller_source = controller_file.read_text(encoding="utf-8")
            permission, source_label = security_extractor.resolve_permission(controller_source, method_name, source_root)
            ep.permission = permission
            ep.permission_source = source_label

    files = MarkdownRenderer().render(document)

    args.output.mkdir(parents=True, exist_ok=True)
    for rel_path, content in files.items():
        out_path = args.output / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")

    print(f"Module      : {args.module}")
    print(f"Endpoints   : {len(document.endpoints)}")
    print(f"Groups      : {len(document.groups())}")
    print(f"Error codes : {len(document.error_codes)}")
    print(f"Output      : {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
