# POST /api/v1/org/departments/search

**Search Departments**

بحث في الأقسام

Operation ID: `API-ORG-021`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: DEPARTMENT_VIEW (found on service:DepartmentService)

## Request Body

Schema: `DepartmentSearchRequest` (application/json)

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| filters | array<ContractFilter> | No |  |  |
| sorts | array<ContractSort> | No |  |  |
| page | integer (int32) | No |  |  |
| size | integer (int32) | No |  |  |

## Response `200` — OK

Shape: `paginated list of DepartmentResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |
| departmentCode | string | No |  | System-generated business code (DEP-[BR_CODE]-NNNNN) - الرمز الآلي |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |
| branchFk | integer (int64) | No |  | Parent Branch ID - معرف الفرع الأب |
| parentDepartmentFk | integer (int64) | No |  | Parent Department ID — null for a root node - معرف القسم الأب |
| nodeTypeId | string | No |  | Node type (LOV-ORG-003: SUMMARY, DETAIL) - نوع العقدة |
| isActive | boolean | No |  | Active status - حالة التفعيل |
| notes | string | No |  | Notes - ملاحظات |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |
| createdBy | string | No |  | Created by - أنشئ بواسطة |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |
