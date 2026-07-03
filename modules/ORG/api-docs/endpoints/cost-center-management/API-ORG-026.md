# POST /api/v1/org/cost-centers

**Create Cost Center**

إنشاء مركز تكلفة جديد

Operation ID: `API-ORG-026`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: COST_CENTER_CREATE (found on service:CostCenterService)

## Request Body

Schema: `CostCenterCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| branchFk | integer (int64) | Yes |  | Parent Branch ID - معرف الفرع الأب | 1 |
| nameAr | string | Yes | maxLength: 200 | Arabic name - الاسم بالعربية | مركز تكلفة الإنتاج |
| nameEn | string | Yes | maxLength: 100 | English name - الاسم بالإنجليزية | Production Cost Center |
| parentCostCenterFk | integer (int64) | No |  | Parent Cost Center ID — null for a root node - معرف مركز التكلفة الأب |  |
| nodeTypeId | string | Yes | maxLength: 50 | Node type (LOV-ORG-004: SUMMARY, DETAIL) - نوع العقدة. Immutable after save. | DETAIL |
| costCenterTypeId | string | Yes | maxLength: 50 | Cost center type (LOV-ORG-005: DIRECT, INDIRECT, SHARED) - نوع مركز التكلفة | DIRECT |
| notes | string | No | maxLength: 2000 | Notes - ملاحظات | Main production line |

**Request Example**

```json
{
  "branchFk": 1,
  "nameAr": "مركز تكلفة الإنتاج",
  "nameEn": "Production Cost Center",
  "nodeTypeId": "DETAIL",
  "costCenterTypeId": "DIRECT",
  "notes": "Main production line"
}
```

## Response `200` — OK

Shape: `CostCenterResponse`

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
