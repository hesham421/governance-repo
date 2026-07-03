# PUT /api/v1/org/departments/{id}

**Update Department**

تحديث قسم

Operation ID: `API-ORG-022`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: DEPARTMENT_UPDATE (found on service:DepartmentService)

## Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

## Request Body

Schema: `DepartmentUpdateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| nameAr | string | No | maxLength: 200 | Arabic name - الاسم بالعربية | قسم المبيعات |
| nameEn | string | No | maxLength: 100 | English name - الاسم بالإنجليزية | Sales Department |
| parentDepartmentFk | integer (int64) | No |  | New parent Department ID (cycle-checked, RULE-ORG-007) - معرف القسم الأب الجديد | 2 |
| notes | string | No | maxLength: 2000 | Notes - ملاحظات | Handles regional sales |

**Request Example**

```json
{
  "nameAr": "قسم المبيعات",
  "nameEn": "Sales Department",
  "parentDepartmentFk": 2,
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
