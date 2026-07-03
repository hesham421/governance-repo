# GET /api/v1/org/cost-centers/tree

**Get Cost Center tree**

جلب الهيكل الشجري لمراكز التكلفة

Operation ID: `API-ORG-027`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: COST_CENTER_VIEW (found on service:CostCenterService)

## Query Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| branchFk | integer | Yes |  |
| isActiveFl | boolean | No |  |

## Response `200` — OK

Shape: `array of CostCenterTreeNodeResponse`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |
| code | string | No |  | Business code - الرمز |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |
| nodeTypeId | string | No |  | Node type (LOV-ORG-004: SUMMARY, DETAIL) - نوع العقدة |
| isActive | boolean | No |  | Active status - حالة التفعيل |
| children | object | No |  | Child nodes - العقد الفرعية |
