# POST /api/v1/org/departments

**Create Department**

إنشاء قسم جديد

Operation ID: `API-ORG-019`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: DEPARTMENT_CREATE (found on service:DepartmentService)

## Request Body

Schema: `DepartmentCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| branchFk | integer (int64) | Yes |  | Parent Branch ID - معرف الفرع الأب | 1 |
| nameAr | string | Yes | maxLength: 200 | Arabic name - الاسم بالعربية | قسم المبيعات |
| nameEn | string | Yes | maxLength: 100 | English name - الاسم بالإنجليزية | Sales Department |
| parentDepartmentFk | integer (int64) | No |  | Parent Department ID — null for a root node - معرف القسم الأب |  |
| nodeTypeId | string | Yes | maxLength: 50 | Node type (LOV-ORG-003: SUMMARY, DETAIL) - نوع العقدة. Immutable after save. | DETAIL |
| notes | string | No | maxLength: 2000 | Notes - ملاحظات | Handles regional sales |

**Request Example**

```json
{
  "branchFk": 1,
  "nameAr": "قسم المبيعات",
  "nameEn": "Sales Department",
  "nodeTypeId": "DETAIL",
  "notes": "Handles regional sales"
}
```

## Response `200` — OK

Shape: `DepartmentResponse`

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
