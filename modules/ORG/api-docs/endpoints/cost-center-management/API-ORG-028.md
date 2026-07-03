# POST /api/v1/org/cost-centers/search

**Search Cost Centers**

بحث في مراكز التكلفة

Operation ID: `API-ORG-028`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: COST_CENTER_VIEW (found on service:CostCenterService)

## Request Body

Schema: `CostCenterSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| filters | array<ContractFilter> | No |  |  |
| sorts | array<ContractSort> | No |  |  |
| page | integer (int32) | No |  |  |
| size | integer (int32) | No |  |  |

## Response `200` — OK

Shape: `paginated list of CostCenterResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |
| costCenterCode | string | No |  | System-generated business code (CC-[BR_CODE]-NNNNN) - الرمز الآلي |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |
| branchFk | integer (int64) | No |  | Parent Branch ID - معرف الفرع الأب |
| parentCostCenterFk | integer (int64) | No |  | Parent Cost Center ID — null for a root node - معرف مركز التكلفة الأب |
| nodeTypeId | string | No |  | Node type (LOV-ORG-004: SUMMARY, DETAIL) - نوع العقدة |
| costCenterTypeId | string | No |  | Cost center type (LOV-ORG-005: DIRECT, INDIRECT, SHARED) - نوع مركز التكلفة |
| isActive | boolean | No |  | Active status - حالة التفعيل |
| notes | string | No |  | Notes - ملاحظات |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |
| createdBy | string | No |  | Created by - أنشئ بواسطة |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |
