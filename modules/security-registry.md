# registry-security.md
════════════════════════════════════════
Module       : SECURITY
Version      : 2.4.0
Last Updated : 2026-07-08
════════════════════════════════════════

---

## 1. ENTITIES & DB ST> **Naming-convention note**: PK column names (`USERS_PK`, `ROLES_PK`, `PERMISSIONS_PK`, `REFRESH_TOKENS_PK`, `SEC_PAGES_PK`) and FK constraint names (`FK_*`) are both real and grep-able in `erp-security/src/main/java` (`@Column(name = ...)` and `@JoinColumn(foreignKey = @ForeignKey(name = ...))` respectively) — matching how `erp-org`/`erp-masterdata` already name things, and this project's own `create-entity` skill (rules A.1.2, A.1.15). **PK constraint names**, however, cannot be set via any JPA/Hibernate annotation (verified by decompiling `hibernate-core-7.2.0.Final.jar`: neither `PhysicalNamingStrategy` nor `ImplicitNamingStrategy` has a PK-constraint hook) — those are enforced only by the `pg_constraint`-driven block in `001_security_schema_migration_and_seed.sql`, and only take effect once a DBA runs it (`ddl-auto=none`, no Flyway wired up for `erp-security`). `CK_*` (check constraint) names are not asserted anywhere in this document — no `@Check` usage exists in this project; get real CHECK definitions from the DBA/live schema.

### 1.1 `USERS` → `UserAccount.java`

| Column      | Type                            | Nullable | Default | Constraints                    |
|-------------|---------------------------------|----------|---------|--------------------------------|
| USERS_PK    | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | — | Primary Key             |
| USERNAME    | VARCHAR(80)                     | NOT NULL | —       | UK: `UK_USERS_USERNAME`        |
| PASSWORD    | VARCHAR(200)                    | NOT NULL | —       | BCrypt hash                    |
| ENABLED     | SMALLINT                        | NOT NULL | 1       | Boolean flag (0/1)             |
| CREATED_AT  | TIMESTAMP                       | NOT NULL | —       | Audit                          |
| CREATED_BY  | VARCHAR(100)                    | NOT NULL | —       | Audit                          |
| UPDATED_AT  | TIMESTAMP                       | NULL     | —       | Audit                          |
| UPDATED_BY  | VARCHAR(100)                    | NULL     | —       | Audit                          |

- **Primary Key**: `USERS_PK` (column and constraint both use this name; renamed from `ID`, see §9) — column rename applied via `001_security_schema_migration_and_seed.sql`, pending DBA execution
- **Indexes**: `IDX_USERS_ENABLED`, `IDX_USERS_USERNAME`
- **FK Fields**: none (join table `USER_ROLES` links to `ROLES`)
- **Flag Fields**: `ENABLED` (SMALLINT → converted to Boolean via `BooleanNumberConverter`)
- **System Fields**: `CREATED_AT`, `CREATED_BY`, `UPDATED_AT`, `UPDATED_BY`
- **Java Entity**: `UserAccount extends AuditableEntity`
- **Relationships**: `@ManyToMany` → `ROLES` via join table `USER_ROLES` (`USER_ROLES.USER_ID_FK` → `USERS.USERS_PK`, `USER_ROLES.ROLE_ID_FK` → `ROLES.ROLES_PK`)

---

### 1.2 `ROLES` → `Role.java`

| Column      | Type                            | Nullable | Default | Constraints                   |
|-------------|---------------------------------|----------|---------|-------------------------------|
| ROLES_PK    | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | — | Primary Key             |
| NAME        | VARCHAR(60)                     | NOT NULL | —       | UK: `UK_ROLES_NAME`           |
| ROLE_CODE   | VARCHAR(60)                     | NOT NULL | —       | UK: `UK_ROLES_ROLE_CODE`      |
| DESCRIPTION | VARCHAR(500)                    | NULL     | —       | —                             |
| IS_ACTIVE   | SMALLINT                        | NOT NULL | 1       | Boolean flag (0/1)            |
| CREATED_AT  | TIMESTAMP                       | NOT NULL | —       | Audit                         |
| CREATED_BY  | VARCHAR(100)                    | NOT NULL | —       | Audit                         |
| UPDATED_AT  | TIMESTAMP                       | NULL     | —       | Audit                         |
| UPDATED_BY  | VARCHAR(100)                    | NULL     | —       | Audit                         |

- **Primary Key**: `ROLES_PK` (column and constraint both use this name; renamed from `ID`, see §9) — column rename applied via `001_security_schema_migration_and_seed.sql`, pending DBA execution
- **Indexes**: `IDX_ROLES_IS_ACTIVE`
- **Flag Fields**: `IS_ACTIVE` (SMALLINT → Boolean via `BooleanNumberConverter`)
- **System Fields**: `CREATED_AT`, `CREATED_BY`, `UPDATED_AT`, `UPDATED_BY`
- **Java Entity**: `Role extends AuditableEntity`
- **Java Field Mapping**:
  - `NAME` DB column → Java `roleName` field (legacy `getName()` deprecated alias)
  - `ROLE_CODE` DB column → Java `roleCode` field — now persisted (previously `@Transient`); backfilled from `NAME`, which historically held the uppercased code (see §9)
  - `DESCRIPTION` DB column → Java `description` field — now persisted (previously `@Transient`)
- **Relationships**: `@ManyToMany` → `PERMISSIONS` via `ROLE_PERMISSIONS` (`ROLE_PERMISSIONS.ROLE_ID_FK` → `ROLES.ROLES_PK`, `ROLE_PERMISSIONS.PERM_ID_FK` → `PERMISSIONS.PERMISSIONS_PK`)

---

### 1.3 `SEC_PAGES` → `Page.java`

| Column        | Type           | Nullable | Default | Constraints                       |
|---------------|----------------|----------|---------|-----------------------------------|
| SEC_PAGES_PK  | BIGINT         | NOT NULL | SEQ     | Primary Key, uses sequence `SEC_PAGES_SEQ` (sequence name real: `@SequenceGenerator(sequenceName = "SEC_PAGES_SEQ")`) |
| PAGE_CODE     | VARCHAR(50)    | NOT NULL | —       | UK: `UK_PAGES_CODE`               |
| NAME_AR       | VARCHAR(100)   | NOT NULL | —       | Arabic name                       |
| NAME_EN       | VARCHAR(100)   | NOT NULL | —       | English name                      |
| ROUTE         | VARCHAR(200)   | NOT NULL | —       | UK: `UK_PAGES_ROUTE`              |
| ICON          | VARCHAR(50)    | NULL     | —       | —                                 |
| MODULE        | VARCHAR(50)    | NULL     | —       | e.g., SECURITY, FINANCE, GL       |
| PARENT_ID_FK  | BIGINT         | NULL     | —       | Self-reference (hierarchy) — plain `@Column`, not a JPA relationship, so no `@ForeignKey` name applies (see note below) |
| DISPLAY_ORDER | BIGINT         | NULL     | —       | Sort order                        |
| IS_ACTIVE     | SMALLINT       | NULL     | 1       | Boolean flag (0/1)                |
| DESCRIPTION   | VARCHAR(500)   | NULL     | —       | —                                 |
| CREATED_AT    | TIMESTAMP      | NOT NULL | —       | Audit                             |
| CREATED_BY    | VARCHAR(100)   | NOT NULL | —       | Audit                             |
| UPDATED_AT    | TIMESTAMP      | NULL     | —       | Audit                             |
| UPDATED_BY    | VARCHAR(100)   | NULL     | —       | Audit                             |

- **Primary Key**: `SEC_PAGES_PK` (column and constraint both use this name; renamed from the generic `ID_PK`, see §9) — uses sequence `SEC_PAGES_SEQ`; column rename applied via `001_security_schema_migration_and_seed.sql`, pending DBA execution
- **FK Fields**: `PARENT_ID_FK` (self-reference to `SEC_PAGES.SEC_PAGES_PK`) — stored as a raw `Long` via `@Column`, not a `@ManyToOne`/`@JoinColumn` relationship, so there's no site to attach an `@ForeignKey` name to
- **Flag Fields**: `IS_ACTIVE` (NUMBER(1) → Boolean)
- **Indexes**: `IDX_PAGES_MODULE`, `IDX_PAGES_ACTIVE`, `IDX_PAGES_PARENT`
- **Java Entity**: `Page extends AuditableEntity`
- **`@PrePersist`**: Normalizes `pageCode` to UPPERCASE, sets `active = true` if null
- **`@PreUpdate`**: Normalizes `pageCode` to UPPERCASE
- **NOTE**: `getActiveStatus()` used instead of `isActive()` to avoid Hibernate phantom column conflict

---

### 1.4 `PERMISSIONS` → `Permission.java`

| Column          | Type                            | Nullable | Default | Constraints                    |
|-----------------|---------------------------------|----------|---------|--------------------------------|
| PERMISSIONS_PK  | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | — | Primary Key              |
| NAME            | VARCHAR(150)                    | NOT NULL | —       | UK: `UK_PERMS_NAME`            |
| PAGE_ID_FK      | BIGINT                          | NULL     | —       | FK → `SEC_PAGES.SEC_PAGES_PK` (`FK_PERMS_PAGE`) |
| PERMISSION_TYPE | VARCHAR(20)                     | NULL     | —       | Enum: VIEW, CREATE, UPDATE, DELETE |
| CREATED_AT      | TIMESTAMP                       | NOT NULL | —       | Audit                          |
| CREATED_BY      | VARCHAR(100)                    | NOT NULL | —       | Audit                          |
| UPDATED_AT      | TIMESTAMP                       | NULL     | —       | Audit                          |
| UPDATED_BY      | VARCHAR(100)                    | NULL     | —       | Audit                          |

- **Primary Key**: `PERMISSIONS_PK` (column and constraint both use this name; renamed from `ID`, see §9) — column rename applied via `001_security_schema_migration_and_seed.sql`, pending DBA execution
- **FK Fields**: `PAGE_ID_FK` → `SEC_PAGES(SEC_PAGES_PK)` (nullable for system permissions), named `FK_PERMS_PAGE` via `@JoinColumn(foreignKey = @ForeignKey(name = ...))`
- **Indexes**: `IDX_PERMS_NAME`, `IDX_PERMS_PAGE_FK`, `IDX_PERMS_TYPE`
- **Naming Pattern**: `PERM_<PAGE_CODE>_<TYPE>` (e.g., `PERM_USER_VIEW`, `PERM_ROLE_CREATE`)
- **Java Entity**: `Permission extends AuditableEntity`
- **Enum**: `PermissionType` {VIEW, CREATE, UPDATE, DELETE}

---

### 1.5 `REFRESH_TOKENS` → `RefreshToken.java`

| Column            | Type                            | Nullable | Default | Constraints                          |
|-------------------|---------------------------------|----------|---------|--------------------------------------|
| REFRESH_TOKENS_PK | BIGINT GENERATED ALWAYS AS IDENTITY | NOT NULL | — | Primary Key                     |
| JTI               | VARCHAR(64)                     | NOT NULL | —       | UK: `UK_REFRESH_TOKENS_JTI`         |
| USER_ID_FK        | BIGINT                          | NOT NULL | —       | FK → `USERS.USERS_PK` (`FK_RT_USER`)|
| CREATED_AT        | TIMESTAMP                       | NOT NULL | —       | Auto via `@CreationTimestamp`        |
| EXPIRES_AT        | TIMESTAMP                       | NOT NULL | —       | Expiry timestamp                     |
| REVOKED           | SMALLINT                        | NOT NULL | 0       | Boolean flag (0/1)                   |

- **Primary Key**: `REFRESH_TOKENS_PK` (column and constraint both use this name; renamed from `ID`, see §9) — column rename applied via `001_security_schema_migration_and_seed.sql`, pending DBA execution
- **FK Fields**: `USER_ID_FK` → `USERS(USERS_PK)`, named `FK_RT_USER` via `@JoinColumn(foreignKey = @ForeignKey(name = ...))` (column renamed from `USER_ID`)
- **Flag Fields**: `REVOKED` (SMALLINT → Boolean)
- **JTI**: UUID used as refresh token identifier (stored in cookie)

---

### 1.6 Join Tables

#### `USER_ROLES`
| Column     | Type   | Constraints                                  |
|------------|--------|----------------------------------------------|
| USER_ID_FK | BIGINT | FK → `USERS(USERS_PK)` (`FK_UR_USER`) + PK  |
| ROLE_ID_FK | BIGINT | FK → `ROLES(ROLES_PK)` (`FK_UR_ROLE`) + PK  |

PK: `USER_ROLES_PK (USER_ID_FK, ROLE_ID_FK)` — composite PK constraint, not annotatable in JPA (same limitation as above); enforced via `001_security_schema_migration_and_seed.sql`, pending DBA execution. FK names are real (`@JoinColumn(foreignKey = @ForeignKey(name = ...))`); columns renamed from `USER_ID`/`ROLE_ID`, see §9.
ing DBA execution. FK names are real (`@JoinColumn(foreignKey = @ForeignKey(name = ...))`); columns renamed from `USER_ID`/`ROLE_ID`, see §9.

#### `ROLE_PERMISSIONS`
| Column     | Type   | Constraints                                      |
|------------|--------|--------------------------------------------------|
| ROLE_ID_FK | BIGINT | FK → `ROLES(ROLES_PK)` (`FK_RP_ROLE`) + PK       |
| PERM_ID_FK | BIGINT | FK → `PERMISSIONS(PERMISSIONS_PK)` (`FK_RP_PERM`) + PK |

PK: `ROLE_PERMISSIONS_PK (ROLE_ID_FK, PERM_ID_FK)` — same treatment as `USER_ROLES` above. FK names are real; columns renamed from `ROLE_ID`/`PERM_ID`, see §9.

---

## 2. IMPLEMENTED APIs

### 2.1 Authentication → `/api/auth`

| Method | Path                    | Description                                               |
|--------|-------------------------|-----------------------------------------------------------|
| POST   | `/api/auth/login`       | Authenticate user → returns `accessToken` + refresh cookie |
| POST   | `/api/auth/login-token` | Authenticate → returns `UserInfo` (tokens + roles/perms)  |
| POST   | `/api/auth/refresh`     | Refresh access token using `refresh_token` cookie         |
| POST   | `/api/auth/logout`      | Revoke refresh token + clear cookie                       |

**POST `/api/auth/login`**
- Request: `{ "username": "string", "password": "string" }`
- Response: `{ "accessToken": "string", "expiresIn": 900 }`
- Side effect: Sets `refresh_token` HttpOnly cookie
- Validation: `@NotBlank` on username and password
- Rate-limited: see §5.8. Exceeding the limit → `429` `RATE_LIMIT_LOGIN_EXCEEDED` with a `Retry-After` header (seconds)

**POST `/api/auth/login-token`**
- Request: same as login
- Response: `UserInfo` record: `{ accessToken, expiresIn, refreshToken, refreshExpiresIn, userId, username, enabled, roles[], permissions[] }`

**POST `/api/auth/refresh`**
- Request: no body — reads `refresh_token` cookie
- Response: `{ "accessToken": "string", "expiresIn": 900 }`
- Side effect: Old JTI revoked, new refresh cookie issued (token rotation)

**POST `/api/auth/logout`**
- No body required
- Response: `204 No Content`
- Behavior: Idempotent — succeeds even if cookie is missing

---

### 2.2 User Management → `/api/users`

| Method | Path                        | Permission Required       |
|--------|-----------------------------|---------------------------|
| POST   | `/api/users`                | `PERM_USER_CREATE`        |
| GET    | `/api/users`                | `PERM_USER_VIEW`          |
| POST   | `/api/users/search`         | `PERM_USER_VIEW`          |
| PUT    | `/api/users/{userId}/roles` | `PERM_USER_UPDATE`        |
| GET    | `/api/users/{userId}/roles` | `PERM_USER_VIEW`          |
| DELETE | `/api/users/{userId}`       | `PERM_USER_DELETE`        |
| PUT    | `/api/users/{userId}`       | `PERM_USER_UPDATE`        |

**POST `/api/users`** → Create User
- Request: `CreateUserRequest { username (3–80 chars, NotBlank), password (6–120 chars, NotBlank) }`
- Response: `ApiResponse<UserDto>`
- Auto-assigns `ROLE_USER` if it exists
- Default `enabled = true`

**GET `/api/users`** → List Users (Paginated)
- Query params: `page`, `size` (default 20), `sort` (e.g., `username,asc`)
- Pagination enforced via `PageableUtils.enforceConstraints()`
- Allowed sort fields: `id`, `username`, `enabled`, `createdAt`

**POST `/api/users/search`** → Dynamic Search
- Request: `UserSearchContractRequest { filters[], page, size, sortBy, sortDir }`
- Allowed filter fields: `id`, `username`, `enabled`, `createdAt`
- Operators: EQ, NE, GT, GE, LT, LE, LIKE, IN, IS_NULL, IS_NOT_NULL, BETWEEN

**PUT `/api/users/{userId}/roles`** → Assign Roles (Full Replace)
- Request: `AssignRolesRequest { roleNames: Set<String> }`
- Replaces ALL existing roles

**DELETE `/api/users/{userId}`** → Delete User
- Blocked if user has active refresh tokens (`USER_HAS_ACTIVE_REFRESH_TOKENS`)
- Response: `204 No Content`

---

### 2.3 Role Management → `/api/roles`

| Method | Path                               | Permission Required    |
|--------|------------------------------------|------------------------|
| POST   | `/api/roles`                       | `PERM_ROLE_CREATE`    |
| POST   | `/api/roles/search`                | `PERM_ROLE_VIEW`      |
| GET    | `/api/roles/{roleId}`              | `PERM_ROLE_VIEW`      |
| PUT    | `/api/roles/{roleId}`              | `PERM_ROLE_UPDATE`    |
| DELETE | `/api/roles/{roleId}`              | `PERM_ROLE_DELETE`    |
| PUT    | `/api/roles/{roleId}/toggle-active`| `PERM_ROLE_UPDATE`    |
| GET    | `/api/roles/{roleId}/pages`        | `PERM_ROLE_VIEW`      |
| POST   | `/api/roles/{roleId}/pages`        | `PERM_ROLE_UPDATE`    |
| PUT    | `/api/roles/{roleId}/pages`        | `PERM_ROLE_UPDATE`    |
| DELETE | `/api/roles/{roleId}/pages/{pageCode}` | `PERM_ROLE_UPDATE` |
| POST   | `/api/roles/{roleId}/copy-from/{sourceRoleId}` | `PERM_ROLE_UPDATE` |

**POST `/api/roles`** → Create Role
- Request: `CreateRoleRequest { roleCode (uppercase pattern ^[A-Z][A-Z0-9_]*$), roleName, description, active }`
- `roleCode` is normalized to UPPERCASE and persisted to its own `ROLE_CODE` column; `roleName` and `description` are persisted as given to `NAME`/`DESCRIPTION`
- Duplicate `roleCode` → `409` `DUPLICATE_ROLE_CODE`; duplicate `roleName` → `409` `DUPLICATE_ROLE_NAME`
- Response: `ApiResponse<RoleDto>`

**PUT `/api/roles/{roleId}/toggle-active`**
- Request: `ToggleRoleActiveRequest { active: boolean }`

**GET `/api/roles/{roleId}/pages`** → Get Role Pages Matrix
- Response: `RolePagesMatrixResponse { roleId, roleName, assignments[{ pageCode, pageName, pageNameAr, permissions[] }] }`
- VIEW permission is excluded from `permissions[]` (implicit)

**POST `/api/roles/{roleId}/pages`** → Add Page to Role
- Request: `AddPageToRoleRequest { pageCode, permissions[] }` (permissions: CREATE/UPDATE/DELETE only)
- VIEW always auto-added
- Returns `409` if page already assigned to role

**PUT `/api/roles/{roleId}/pages`** → Sync Pages (Full Replace)
- Request: `SyncRolePagesRequest { assignments[{ pageCode, permissions[] }] }`
- Empty array removes all page access
- Replaces all current page-related permissions (identified by `PERM_` prefix)

**DELETE `/api/roles/{roleId}/pages/{pageCode}`** → Remove Page from Role
- Removes VIEW + all CRUD permissions for that page from the role

**POST `/api/roles/{roleId}/copy-from/{sourceRoleId}`** → Copy Permissions From Role
- `roleId` = target role, `sourceRoleId` = source role
- **Scope (page-scoped only, not full-role copy)**: reads source role's `ROLE_PERMISSIONS` filtered to `Permission.isPagePermission()` (i.e. joined `PERMISSIONS.PAGE_ID_FK IS NOT NULL`); Full-Replaces the target's page-scoped `ROLE_PERMISSIONS` rows with that set. The target's system-level permissions (`PAGE_ID_FK IS NULL`, e.g. `PERM_SYSTEM_ADMIN`) are left untouched — this is a deliberate privilege-escalation guard (Rule 25), not an oversight: a naive full-row copy would let an admin silently hand the target role any system-level permission the source happened to hold.
- `targetRoleId == sourceRoleId` → `400 Bad Request` (`INVALID_OPERATION`)
- Source has zero page-scoped permissions → `409 Conflict` (`NO_PERMISSIONS_TO_COPY`) — Rule 24
- Response: `CopyPermissionsResponse { roleId, roleName, copiedFrom { roleId, roleName }, assignments[] }`
- Service: `RoleAccessService.copyPermissionsFromRole()`

---

### 2.4 Pages Management → `/api/pages`

| Method | Path                         | Permission Required    |
|--------|------------------------------|------------------------|
| POST   | `/api/pages`                 | `PERM_PAGE_CREATE`    |
| POST   | `/api/pages/search`          | `PERM_PAGE_VIEW` ✓    |
| GET    | `/api/pages/active`          | `PERM_PAGE_VIEW` ✓    |
| GET    | `/api/pages/{id}`            | `PERM_PAGE_VIEW` ✓    |
| PUT    | `/api/pages/{id}`            | `PERM_PAGE_UPDATE`    |
| PUT    | `/api/pages/{id}/deactivate` | `PERM_PAGE_DELETE` ✓  |
| PUT    | `/api/pages/{id}/reactivate` | `PERM_PAGE_UPDATE` ✓  |

**POST `/api/pages`** → Create Page
- Request: `CreatePageRequest { pageCode, nameAr, nameEn, route, icon, module, parentId, displayOrder, active, description }`
- Auto-generates 4 permission records: `PERM_<CODE>_VIEW`, `PERM_<CODE>_CREATE`, `PERM_<CODE>_UPDATE`, `PERM_<CODE>_DELETE`
- Validations: pageCode uppercase alphanumeric+underscore, length 2–50, route starts with `/`, no spaces
- Response: `PageResponse { ...fields..., permissionKeys: Map<String,String> }`

**GET `/api/pages/active`** → Get Active Pages
- No pagination; returns full list of active pages for dropdowns

**PUT `/api/pages/{id}/deactivate`** → Soft Delete
- Sets `IS_ACTIVE = 0`

**PUT `/api/pages/{id}/reactivate`** → Reactivate
- Sets `IS_ACTIVE = 1`

---

### 2.5 Permissions Management → `/api/permissions`

| Method | Path                      | Permission Required              |
|--------|---------------------------|----------------------------------|
| POST   | `/api/permissions`        | `PERM_PERMISSION_CREATE` ✓       |
| POST   | `/api/permissions/search` | `PERM_PERMISSION_VIEW` ✓         |

Allowed filter fields: `name`, `module`
Allowed sort fields: `id`, `name`, `module`, `createdAt`, `updatedAt`

---

### 2.6 Menu → `/api/menu`

| Method | Path                         | Permission Required   |
|--------|------------------------------|-----------------------|
| GET    | `/api/menu/user-menu`        | (authenticated only)  |
| GET    | `/api/menu/user-menu/{userId}` | `PERM_USER_VIEW`   |

**GET `/api/menu/user-menu`**
- Builds dynamic menu tree (`parent → children`) from `SEC_PAGES`
- Filters pages where user has `PERM_*_VIEW` permission (resolved via `PAGE_ID_FK`)
- Only `IS_ACTIVE = 1` pages included
- Response: `List<MenuItemDto>` (tree structure)

---

## 3. BUSINESS RULES & VALIDATIONS

1. **The system MUST reject login if username/password combination is invalid** — Spring Security `DaoAuthenticationProvider` + BCrypt verification.

2. **The system MUST generate a UUID-based JTI for each refresh token** — Stored in `REFRESH_TOKENS.JTI` and sent in `refresh_token` HttpOnly cookie.

3. **The system MUST revoke the old refresh token and issue a new one on every refresh call** — Token rotation pattern. Old JTI set `REVOKED = 1`.

4. **The system MUST reject refresh if JTI is revoked or expired** — Throws `REFRESH_EXPIRED_OR_REVOKED` or `REFRESH_REVOKED`.

5. **The system MUST make logout idempotent** — Does not fail if refresh cookie is missing or already revoked.

6. **The system MUST prevent duplicate usernames globally** — DB: `UK_USERS_USERNAME`. Service: explicit pre-check → `USERNAME_ALREADY_EXISTS`.

7. **The system MUST prevent deleting a user who has active refresh tokens** — Pre-check: `countByUser_Id()` → `USER_HAS_ACTIVE_REFRESH_TOKENS`.

8. **The system MUST auto-assign `ROLE_USER` to newly created users** — if `ROLE_USER` exists.

9. **The system MUST prevent duplicate role names globally** — DB: `UK_ROLES_NAME`. Service: explicit pre-check → `DUPLICATE_ROLE_NAME`.

9a. **The system MUST prevent duplicate role codes globally** — DB: `UK_ROLES_ROLE_CODE`. Service: explicit pre-check → `DUPLICATE_ROLE_CODE`.

10. **The system MUST prevent deleting a role that is assigned to users** — Pre-check: `hasUserAssignments()` → `ROLE_IN_USE` (Status 409 Conflict).

11. **The system MUST auto-generate 4 permission records (VIEW/CREATE/UPDATE/DELETE) when a new page is created** — Pattern: `PERM_<PAGE_CODE>_VIEW`, etc.

12. **The system MUST auto-add VIEW permission when assigning a page to a role** — VIEW is implicit and non-removable while page is assigned.

13. **The system MUST prevent assigning a page to a role if already assigned** — Check: VIEW permission for that page already in role → `PAGE_ALREADY_ASSIGNED_TO_ROLE`.

14. **The system MUST only accept CREATE/UPDATE/DELETE as optional permissions in page assignment** — `VIEW` is disallowed in the request body (auto-added server-side). Invalid types → `INVALID_PERMISSION_TYPE`.

15. **The system MUST normalize `pageCode` to UPPERCASE on create and update** — Both `@PrePersist` / `@PreUpdate` and service layer.

16. **The system MUST reject `pageCode` with invalid format** — Only `^[A-Z0-9_]+$` allowed, 2–50 characters.

17. **The system MUST reject route that does not start with `/`** — Validated in `PageService.createPage()` and `updatePage()`.

18. **The system MUST reject route that contains spaces** — Regex: `^/[a-zA-Z0-9/_-]+$`.

19. **The system MUST prevent duplicate routes globally** — DB: `UK_PAGES_ROUTE`. Service: explicit pre-check → `DUPLICATE_ROUTE`.

20. **The system MUST validate parent page exists before creating a child page** — `PARENT_PAGE_NOT_FOUND` if `parentId` is provided but not found.

21. **The system MUST build the user menu from `SEC_PAGES` filtered by `VIEW` permissions via `PAGE_ID_FK`** — Not via string pattern extraction; uses FK for resilience against page code renaming.

22. **The system MUST enforce pagination size limits** — `PageableUtils.enforceConstraints()` applied in `UserController.all()`.

23. **The system MUST validate sort field whitelists** — `PageableValidator.validateSortFields()` to prevent injection via sort params.

24. **The system MUST reject Copy Permissions if the source role has zero page-scoped permissions** — `RoleAccessService.copyPermissionsFromRole()` → `NO_PERMISSIONS_TO_COPY` (Status `CONFLICT` → HTTP 409, same pattern as `ROLE_IN_USE`).

25. **The system MUST only copy page-scoped permissions (`PAGE_ID_FK IS NOT NULL`) in Copy Permissions, never system-level permissions** — `Permission.isPagePermission()` filters both the source read and the target's existing-row deletion; the target's pre-existing system-level permissions are preserved. Privilege-escalation guard (see §9).

26. **The system MUST purge expired refresh tokens periodically** — `RefreshTokenCleanupJob` (`@Scheduled`, cron `erp.security.token-cleanup.cron`, default daily 03:00) calls `RefreshTokenRepository.deleteByExpiresAtBefore(now())`.

27. **The system MUST purge revoked refresh tokens older than a configured retention window** — same `RefreshTokenCleanupJob` run, `RefreshTokenRepository.deleteByRevokedTrueAndCreatedAtBefore(cutoff)`, cutoff = now − `erp.security.token-cleanup.revoked-retention-days` (default 30). `REFRESH_TOKENS` has no separate "revoked at" timestamp, so `CREATED_AT` is used as the age reference — a revoked token is retained at most `retention-days` from when it was originally issued, not from when it was revoked.

28. **The system MUST rate-limit login attempts by IP+username** — `LoginRateLimitFilter` (§5.8). Exceeding `erp.security.rate-limit.login.max-attempts` within `window-seconds` blocks that IP+username pair for `lockout-seconds` → `429` `RATE_LIMIT_LOGIN_EXCEEDED`.

---

## 4. LOOKUP & REFERENCE USAGE

- **No external Lookup tables (MD_MASTER_LOOKUP / MD_LOOKUP_DETAIL) used** within the security module.
- `PermissionType` is an in-module enum (VIEW, CREATE, UPDATE, DELETE) — not a DB lookup.
- Module grouping (`MODULE` field on `SEC_PAGES`) is a free-text string (e.g., SECURITY, FINANCE, GL) — no FK to a lookup table.
- ⚠️ NOT FOUND: No LOV table backing the `MODULE` field — it is a raw string.

---

## 5. SECURITY & PERMISSIONS

### 5.1 Defined Permissions (from `SecurityPermissions.java`)

| Group         | Permission Constant       | Value                     |
|---------------|---------------------------|---------------------------|
| User          | `USER_VIEW`               | `PERM_USER_VIEW`          |
| User          | `USER_CREATE`             | `PERM_USER_CREATE`        |
| User          | `USER_UPDATE`             | `PERM_USER_UPDATE`        |
| User          | `USER_DELETE`             | `PERM_USER_DELETE`        |
| User          | `USER_MANAGE_ROLES`       | `PERM_USER_UPDATE`        |
| Role          | `ROLE_VIEW`               | `PERM_ROLE_VIEW`          |
| Role          | `ROLE_CREATE`             | `PERM_ROLE_CREATE`        |
| Role          | `ROLE_UPDATE`             | `PERM_ROLE_UPDATE`        |
| Role          | `ROLE_DELETE`             | `PERM_ROLE_DELETE`        |
| Permission    | `PERMISSION_VIEW`         | `PERM_PERMISSION_VIEW`    |
| Permission    | `PERMISSION_CREATE`       | `PERM_PERMISSION_CREATE`  |
| Permission    | `PERMISSION_UPDATE`       | `PERM_PERMISSION_UPDATE`  |
| Permission    | `PERMISSION_DELETE`       | `PERM_PERMISSION_DELETE`  |
| Menu          | `MENU_VIEW`               | `PERM_MENU_VIEW`          |
| Menu          | `MENU_CREATE`             | `PERM_MENU_CREATE`        |
| Menu          | `MENU_UPDATE`             | `PERM_MENU_UPDATE`        |
| Menu          | `MENU_DELETE`             | `PERM_MENU_DELETE`        |
| Page          | `PAGE_VIEW`               | `PERM_PAGE_VIEW`          |
| Page          | `PAGE_CREATE`             | `PERM_PAGE_CREATE`        |
| Page          | `PAGE_UPDATE`             | `PERM_PAGE_UPDATE`        |
| Page          | `PAGE_DELETE`             | `PERM_PAGE_DELETE`        |
| Master Lookup | `MASTER_LOOKUP_VIEW`      | `PERM_MASTER_LOOKUP_VIEW` |
| Lookup Detail | `LOOKUP_DETAIL_VIEW`      | `PERM_LOOKUP_DETAIL_VIEW` |
| Activity      | `ACTIVITY_VIEW`           | `PERM_ACTIVITY_VIEW`      |
| GL Account    | `GL_ACCOUNT_VIEW`         | `PERM_GL_ACCOUNT_VIEW`    |
| GL Rule       | `GL_RULE_VIEW`            | `PERM_GL_RULE_VIEW`       |
| GL Journal    | `GL_JOURNAL_VIEW`         | `PERM_GL_JOURNAL_VIEW`    |
| GL Journal    | `GL_JOURNAL_APPROVE`      | `PERM_GL_JOURNAL_APPROVE` |
| GL Journal    | `GL_JOURNAL_POST`         | `PERM_GL_JOURNAL_POST`    |
| GL Journal    | `GL_JOURNAL_REVERSE`      | `PERM_GL_JOURNAL_REVERSE` |
| GL Journal    | `GL_JOURNAL_CANCEL`       | `PERM_GL_JOURNAL_CANCEL`  |
| GL Posting    | `GL_POSTING_VIEW`         | `PERM_GL_POSTING_VIEW`    |
| Legal Entity  | `LEGAL_ENTITY_VIEW`       | `PERM_LEGAL_ENTITY_VIEW`  |
| System Admin  | `SYSTEM_ADMIN`            | `PERM_SYSTEM_ADMIN`       |

### 5.2 Authorization Enforcement

- **Method-level security**: `@EnableMethodSecurity` active on `SecurityConfig`
- **`@PreAuthorize`**: Applied in service layer (Rule 19.1 — thin controllers)
- **JWT Filter**: `JwtAuthenticationFilter extends OncePerRequestFilter`
  - Extracts `Bearer` token from `Authorization` header
  - Extracts `userId` and `authorities` from token claims
  - Loads `UserDetails` via `CustomUserDetailsService.loadUserById()` (uses ID, not username for performance)
  - Populates `SecurityContextHolder`
- **Public endpoints** (no auth required): `/api/auth/**`, `/swagger-ui/**`, `/v3/api-docs/**`, `/actuator/health`
- **Session**: `STATELESS` — no server-side sessions

### 5.3 Token Configuration (`JwtProperties`)

| Property                                       | Description                               | Default  |
|------------------------------------------------|-------------------------------------------|----------|
| `erp.security.jwt.secret`                      | HS256 signing key (≥ 256 bits / 32 chars) | required |
| `erp.security.jwt.access-expiration-seconds`   | Access token TTL                          | 3600     |
| `erp.security.jwt.refresh-expiration-seconds`  | Refresh token TTL                         | 604800   |

**Access Token Claims**: `sub` (username), `authorities[]`, `userId`
**Refresh Token Claims**: `sub` (username), `jti` (UUID)

### 5.4 Cookie Configuration (`CookieProperties`)

- Cookie name: `refresh_token`
- `HttpOnly`, `Secure` (configurable)
- `SameSite`: STRICT / LAX / NONE (configurable)
- Domain and path configurable via `erp.security.cookie.*`

### 5.5 CORS Configuration (`CorsProperties`)

- Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
- Credentials: `true`
- Allowed origins: configurable via `erp.security.cors.allowed-origins`

### 5.6 Cache Configuration

- `@EnableCaching` is active in both `RedisCacheConfig.java` and `ErpMainApplication.java` (see §7.4 — two independent `@SpringBootApplication` entry points, both with caching enabled).
- **Currently zero active `@Cacheable` methods in the module.** `PermissionService`'s `@CacheEvict`s on `permissionByName`/`permissionsList` are eviction-only with no populate-side `@Cacheable` — currently inert no-ops. `UserService`'s USERS-derived data is deliberately never cached (freshness/security policy).
- `application-prod.properties` and `application.properties` both set `spring.cache.type=redis` (previously mismatched: prod used `simple`). Redis runs as its own container in `deploy/docker-compose.yml`, with the backend's startup gated on its healthcheck.
- `ErpMainApplication`'s `excludeName` no longer references `RedisAutoConfiguration`/`RedisRepositoriesAutoConfiguration` — confirmed no-op before removal (`RedisCacheConfig.cacheManager(RedisConnectionFactory)` has no other bean source for its constructor param, so Boot's real autoconfiguration was supplying it regardless).

### 5.7 Scheduled Jobs

- **`RefreshTokenCleanupJob`** (`com.example.security.scheduler`) — single `@Scheduled` job covering both Rule 26 (expired) and Rule 27 (revoked) token purges in one run.
  - `erp.security.token-cleanup.cron` — cron expression, default `0 0 3 * * *` (daily 03:00)
  - `erp.security.token-cleanup.revoked-retention-days` — retention window in days, default `30`
  - Both bound via `RefreshTokenCleanupProperties` (`@ConfigurationProperties(prefix = "erp.security.token-cleanup")`, registered in `SecurityPropertiesConfig`)
  - Requires `@EnableScheduling` — present on both `ErpMainApplication` and `SecurityOracleJwtApplication` (§7.4)

### 5.8 Login Rate Limiting

- **`LoginRateLimitFilter`** (`com.example.security.security`, `OncePerRequestFilter`) — registered in `SecurityConfig` via `addFilterBefore(loginRateLimitFilter, UsernamePasswordAuthenticationFilter.class)`, ahead of `JwtAuthenticationFilter`
  - Matches `POST /api/auth/login` and `POST /api/auth/signup` (path-matched generically so it covers signup once that endpoint exists — no code change needed there)
  - Reads the request body via `CachedBodyHttpServletRequest` (caches bytes so the `@RequestBody` argument resolver downstream can still read it) to extract `username`; IP taken from `X-Forwarded-For` (first entry) falling back to `getRemoteAddr()`
  - Rate-limit key: `"<ip>|<username-lowercased>"` — never IP alone, so one endpoint cannot be used to lock out unrelated accounts, and vice versa
  - Enforcement: `LoginRateLimiterService`, in-memory `Bucket4j` bucket per key (`com.bucket4j:bucket4j-core:8.10.1`) sized `max-attempts` per `window-seconds`; exceeding it additionally sets an explicit lockout of `lockout-seconds` (separate from the bucket's own refill) tracked in a side `ConcurrentHashMap`
  - **Not shared across instances** — acceptable for the current single-container deployment (`deploy/docker-compose.yml`). Must move to Redis if the backend is ever horizontally scaled.
  - On block: `429`, `Retry-After` header (seconds remaining), bilingual body via `LocalizationService` + the standard `ApiResponse`/`ApiError` envelope (message key `RATE_LIMIT_LOGIN_EXCEEDED`) — resolved directly from the `Accept-Language` header (not `LocaleContextHolder`, since this filter can run before Spring MVC's locale resolution is established)
- **`LoginRateLimitProperties`** (`@ConfigurationProperties(prefix = "erp.security.rate-limit.login")`): `max-attempts` (default 5), `window-seconds` (default 60), `lockout-seconds` (default 300)
- Frontend: `auth-login.component.ts` reads `Retry-After` on a `429` and disables the submit button with a live countdown (`AUTH.RETRY_IN_SECONDS`); does not auto-retry

---

## 6. APPROVAL WORKFLOW

⚠️ NOT FOUND — No approval workflow implemented in the Security module. All operations are direct CRUD without multi-step approval states.

---

## 7. CROSS-MODULE DEPENDENCIES

### 7.1 Security Module PROVIDES to Other Modules

- **`SecurityPermissions.java`** — Used by ALL modules as the single source of truth for permission constant strings in `@PreAuthorize` annotations
- **JWT infrastructure** — All modules rely on the access token issued by `/api/auth/login`

### 7.2 Security Module USES from Other Modules

- **`erp-common-utils`** module:
  - `AuditableEntity` — base entity superclass for all security entities
  - `BooleanNumberConverter` — NUMBER(1) → Boolean
  - `SecurityContextHelper` — getting current user from security context (`getUsernameOrSystem()`, `isAuthenticated()`)
  - `LocalizedException` — localized error throwing
  - `ServiceResult` / `Status` — service response wrapping
  - `ApiResponse` / `OperationCode` — REST response building
  - `CookieUtils` / `SameSite` — cookie management
  - `PageableUtils` / `PageableValidator` — pagination enforcement
  - `SpecBuilder` / `SetAllowedFields` / `DefaultFieldValueConverter` / `PageableBuilder` — dynamic search

### 7.3 SEC_PAGES Referenced by Other Modules

- Other modules (GL, Finance, etc.) seed their pages into `SEC_PAGES` as well — the Security module owns the `SEC_PAGES` table structure

### 7.4 Deployment Entry Points

There are **two** independent `@SpringBootApplication` classes that can boot the security module — this matters for any config decision that lives on the application class (`@EnableCaching`, `@EnableScheduling`, component scan, autoconfig excludes, etc.):

- **`com.erp.main.ErpMainApplication`** (`erp-main` module) — the **real production entry point**. Aggregates security + masterdata + finance-gl + org into one context, all APIs on port 7272. `backend/CLAUDE.md` confirms this is what actually ships.
- **`com.example.security.SecurityOracleJwtApplication`** (`erp-security` module) — a standalone/dev bootstrap for running the security module in isolation (also port 7272 standalone per its own Javadoc). Not used in the assembled production deployment; `erp-security` is packaged as a plain `jar`, not run directly.

Any `@Enable*` annotation, exclude, or app-level config added for this module must be applied to **`ErpMainApplication`** to take effect in production. `SecurityOracleJwtApplication` should be kept consistent for standalone-mode parity, but is not a substitute.