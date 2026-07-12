<!-- Source: PHASE:DOC -->

## PHASE DOC — Contract Stabilization
─────────────────────────────────────────────────────────────────
Gate Required    : SVC+API ✓
Gate This Phase  : DOC ✓
Gate Status      : PASSED ✓
─────────────────────────────────────────────────────────────────

### DOC-1: API Contract Summary
```
API-ID        │ Endpoint                                          │ Method │ Stability
──────────────┼────────────────────────────────────────────────────┼────────┼──────────
API-NOTIF-001 │ /api/v1/notifications/send                        │ POST   │ STABLE
API-NOTIF-002 │ /api/v1/notifications/schedule                    │ POST   │ STABLE
API-NOTIF-003 │ /api/v1/notifications/history                     │ GET    │ STABLE
API-NOTIF-004 │ /api/v1/notifications/unread                      │ GET    │ UNSTABLE — DRV-NOTIF-003 (recommended SRS amendment)
API-NOTIF-005 │ /api/v1/notifications/{id}/read                   │ PUT    │ UNSTABLE — DRV-NOTIF-003 (recommended SRS amendment)
API-NOTIF-006 │ /api/v1/notifications/templates                   │ GET    │ STABLE
API-NOTIF-007 │ /api/v1/notifications/templates                   │ POST   │ STABLE
API-NOTIF-008 │ /api/v1/notifications/templates/{id}               │ PUT    │ STABLE
API-NOTIF-009 │ /api/v1/notifications/templates/{id}/deactivate    │ PUT    │ STABLE
API-NOTIF-010 │ /api/v1/notifications/templates/{id}               │ GET    │ STABLE
API-NOTIF-011 │ /api/v1/notifications/channel-configs              │ GET    │ STABLE
API-NOTIF-012 │ /api/v1/notifications/channel-configs/{id}         │ PUT    │ STABLE
```
Unstable APIs: API-NOTIF-004, API-NOTIF-005 — blocked on DRV-NOTIF-003 (missing DB column — recommended SRS amendment, see Escalation Note).
Frontend-governed contracts: None.

### DOC-2: DTO Typing Rules
LOV field typing: String (notificationTypeId, notificationStatusId, channelTypeId) — never ENUM.
Business Code: N/A — no entity in this module has a Business Code.

### DOC-3: Pagination & Filter Standards
Standard platform rule applies as-is. Used by API-NOTIF-003, API-NOTIF-006.

**DOC GATE CHECK:**
```
[ ✓ ] All API-IDs from SVC+API appear in API Contract Summary
[ ✓ ] Error Catalog complete with Arabic + English messages
[ ✓ ] All APIs marked STABLE or explicitly UNSTABLE (2 UNSTABLE — documented)
[ ✓ ] Pagination standard declared
DOC Gate: PASSED ✓ (2 APIs UNSTABLE — does not fail the gate, tracked via DRV-NOTIF-003 / Escalation Note)
```
