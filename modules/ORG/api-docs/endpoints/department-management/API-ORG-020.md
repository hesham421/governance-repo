# GET /api/v1/org/departments/tree

**Get Department tree**

جلب الهيكل الشجري للأقسام

Operation ID: `API-ORG-020`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: DEPARTMENT_VIEW (found on service:DepartmentService)

## Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| branchFk | integer | Yes |  |
| isActiveFl | boolean | No |  |

## Response `200` — OK

Shape: `array of DepartmentTreeNodeResponse`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |
| code | string | No |  | Business code - الرمز |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |
| nodeTypeId | string | No |  | Node type (LOV-ORG-003: SUMMARY, DETAIL) - نوع العقدة |
| isActive | boolean | No |  | Active status - حالة التفعيل |
| children | object | No |  | Child nodes - العقد الفرعية |
