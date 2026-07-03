# api-doc-generator

Standalone tool that generates frontend-ready API documentation directly
from an implemented Spring Boot module. It replaces the old
governance-driven contract-verification workflow (deleted) — there is no
governance coupling, no execution-plan parsing, no drift/contract
verification here. **The implemented backend is the only source of truth.**

## Purpose

Frontend developers need accurate, up-to-date API documentation. Hand-written
docs drift from the real implementation the moment either side changes. This
tool regenerates documentation from the actual running/compiled backend every
time, so it can never be stale — if it's wrong, the backend is wrong (or
under-annotated), not the doc generator.

## Architecture

```
generator.py            CLI entrypoint: extract -> render
models/
  api_doc_model.py       Dataclasses shared by every extractor and renderer.
                         Every field is Optional — absence means "not
                         discoverable", never "invent something reasonable".
extractors/
  openapi_extractor.py   Loads the OpenAPI JSON (file or URL), walks paths/
                         operations into Endpoint objects: method, path,
                         summary/description, tag, path & query params,
                         auth requirement + scheme names.
  dto_extractor.py       Resolves $ref schemas into field lists. Understands
                         three recurring response shapes in this codebase:
                         the ApiResponse<T> envelope, Spring's Page<T>
                         serialization, and plain arrays.
  validation_extractor.py  Turns one resolved schema property into a
                         FieldSpec (required / minLength / maxLength /
                         pattern / format / enum) — these are Bean
                         Validation constraints springdoc already translated
                         into OpenAPI keywords; nothing here re-reads Java.
  security_extractor.py  BEST-EFFORT, only runs when --source is given.
                         Locates a controller method's real Java source (by
                         re-deriving its route from @RequestMapping/@XxxMapping
                         and matching verb+path — not by guessing off the
                         method name, since names like "create"/"search"
                         repeat across every controller), then looks for
                         @PreAuthorize/@Secured on that method or on the
                         service method it delegates to. Extracts only the
                         SecurityPermissions.XXX identifiers, never evaluates
                         the SpEL expression.
  exception_extractor.py  BEST-EFFORT, only runs when --source is given.
                         Finds every `*ErrorCodes.java` file under the
                         module's source tree and lists its constants as a
                         module-level "Known Error Codes" appendix.
  response_model_extractor.py  Detects the shared ApiResponse<T> envelope
                         shape once (springdoc names each generic
                         instantiation differently, e.g.
                         "ApiResponseLegalEntityResponse", so this matches by
                         key-set rather than a fixed schema name) so it can
                         be documented once instead of repeated per endpoint.
renderers/
  base.py                Renderer interface: render(ApiDocument) -> {path: text}.
                         A renderer only renders — it must never call an
                         extractor or infer missing data itself.
  markdown_renderer.py   v1 output: index.md (module overview + shared
                         sections) + endpoints/<group>/<slug>.md per endpoint.
```

## Data flow

```
compiled Spring Boot app
        │  springdoc-openapi
        ▼
   OpenAPI JSON  ──────────────►  openapi_extractor  ──►  Endpoint list
        │                              │
        │                              ├─► dto_extractor (+ validation_extractor)
        │                              │      per operation's request/response
        │                              │
        │                         (needs --source, optional)
        │                              ├─► security_extractor   → permissions
        │                              └─► exception_extractor  → error codes
        │
        └─────────────────────────►  response_model_extractor  → shared envelope
                                     dto_extractor.find_page_envelope → pagination envelope

                    ApiDocument (fully populated)
                              │
                              ▼
                     MarkdownRenderer.render()
                              │
                              ▼
                    {relative_path: file_content}
                              │
                              ▼
                  written under --output by generator.py
```

Extraction and rendering are fully separated: extractors never format text,
renderers never call `json.load` or open a Java file. To add a new output
format later (OpenAPI YAML, Postman/Insomnia collection, frontend model
stubs), write a new `Renderer` subclass — no extractor changes needed.

## How to execute

```bash
# 1) Build and run the module (any way you like — jar, IDE run config, etc.)
#    Make sure a GroupedOpenApi bean exists for it in OpenApiConfig.java so
#    you can target it in isolation, e.g.:
#      GroupedOpenApi.builder().group("4-organization")
#          .packagesToScan("com.example.erp.org.controller").build()

# 2) Point the generator at the running app's per-group OpenAPI doc.
#    NOTE: springdoc serves grouped docs at a PATH segment, not a query
#    param — /api-docs/<group>, not /api-docs?group=<group>.
python3 generator.py \
    --module ORG \
    --openapi http://localhost:7272/api-docs/4-organization \
    --source ../../../backend/erp-org/src/main/java \
    --output ../../modules/ORG/api-docs/

# Offline / CI: --openapi also accepts a saved JSON file
python3 generator.py --module ORG --openapi ./openapi.json --output ../../modules/ORG/api-docs/
```

Output goes under the target module's own folder in `governance-repo/modules/`, alongside its
other governance packages (`P0`–`P4`, `packages/`) — one `api-docs/` per module, not a shared
`output/` under the tool itself:

```
modules/ORG/api-docs/
├── index.md                          module overview, auth, shared response/
│                                      pagination envelopes, known error codes,
│                                      API catalog grouped by tag
└── endpoints/
    └── <group-slug>/
        └── <operationId-or-method-path-slug>.md
```

## Supported Spring Boot features

- Any HTTP method/path springdoc exposes, grouped by `@Tag`.
- Path/query parameters (works whether pagination is a custom `SearchRequest`
  DTO body, a raw `Pageable` method parameter, or ad-hoc `@RequestParam`s —
  all three are already fully visible in the OpenAPI JSON, no special-casing
  needed).
- Request/response DTO fields with `@NotBlank`/`@NotNull` → required,
  `@Size` → min/maxLength, `@Pattern` → pattern, `@Schema(description,
  example)` → description/example.
- `enum: [...]` values, when the schema actually has them (see Limitations).
- The shared `ApiResponse<T>` envelope and Spring `Page<T>` wrapper, each
  documented once rather than repeated on every endpoint.
- Global Bearer-auth requirement per operation.
- (best-effort, needs `--source`) Per-endpoint required permission, whether
  declared on the controller method or delegated to a service method.
- (best-effort, needs `--source`) Module-level known error codes from
  `*ErrorCodes.java`.

## Limitations

- **Per-endpoint error responses are not documented.** No controller in this
  codebase declares `@ApiResponse`/`@ApiResponses`, so there's nothing to
  extract per endpoint — only the module-level error-code appendix exists.
- **No `enum` schema arrays exist yet in this codebase** (e.g.
  finance-gl's `accountType` is a plain `String` documented only in
  free-text `@Operation` descriptions). The generator will render an
  `enum: [...]` list the moment a schema actually has one, but don't expect
  it today.
- **Permission discovery is a source-text heuristic, not a real Java
  parser.** It relies on: (a) one `@RequestMapping`/`@XxxMapping` per
  controller method with a literal string path (no path variables built via
  constants/expressions), and (b) a controller method delegating to at most
  one same-named service method. It's built specifically around the
  conventions actually observed across all 4 modules in this codebase.
  It will silently return nothing for anything it can't confidently resolve.
- **Requires `?group=` to actually work as a path segment**, not a query
  string — springdoc groups aren't filterable via `?group=x`.

## Extension points

- **New output format**: add a `Renderer` subclass in `renderers/` (e.g.
  `renderers/openapi_yaml.py`, `renderers/postman.py`). It receives the same
  fully-populated `ApiDocument` — no extractor changes needed.
- **New extractor**: add a module under `extractors/` and call it from
  `generator.py`, writing onto the existing `ApiDocument`/`Endpoint`
  dataclasses (add new Optional fields to `models/api_doc_model.py` as
  needed — never repurpose an existing field for a different meaning).
- **Smarter permission resolution**: if this codebase ever adopts a
  `MethodSecurityExpressionHandler` introspection endpoint, or a real Java
  parser (e.g. javalang), `security_extractor.py` is the only file that
  would need to change.
