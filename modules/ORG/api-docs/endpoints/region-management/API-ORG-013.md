# POST /api/v1/org/regions

**Create Region**

إنشاء منطقة جديدة

Operation ID: `API-ORG-013`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: REGION_CREATE (found on service:RegionService)

## Request Body

Schema: `RegionCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| legalEntityFk | integer (int64) | Yes |  | Parent Legal Entity ID - معرف الكيان القانوني الأب | 1 |
| regionTypeIdFk | integer (int64) | Yes |  | Region Type ID - معرف نوع المنطقة | 1 |
| nameAr | string | Yes | maxLength: 200 | Arabic name - الاسم بالعربية | منطقة القاهرة الكبرى |
| nameEn | string | Yes | maxLength: 100 | English name - الاسم بالإنجليزية | Greater Cairo Region |
| notes | string | No | maxLength: 2000 | Notes - ملاحظات | Covers all Cairo branches |

**Request Example**

```json
{
  "legalEntityFk": 1,
  "regionTypeIdFk": 1,
  "nameAr": "منطقة القاهرة الكبرى",
  "nameEn": "Greater Cairo Region",
  "notes": "Covers all Cairo branches"
}
```

## Response `200` — OK

Shape: `RegionResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |  |
| regionCode | string | No |  | System-generated business code (RG-[LE_CODE]-NNNNN) - الرمز الآلي | RG-LE-00001-00001 |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |  |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |  |
| legalEntityFk | integer (int64) | No |  | Parent Legal Entity ID - معرف الكيان القانوني الأب |  |
| legalEntityCode | string | No |  | Parent Legal Entity business code - رمز الكيان القانوني الأب |  |
| regionTypeIdFk | integer (int64) | No |  | Region Type ID - معرف نوع المنطقة |  |
| regionTypeNameEn | string | No |  | Region Type English name - اسم نوع المنطقة |  |
| isActive | boolean | No |  | Active status - حالة التفعيل |  |
| notes | string | No |  | Notes - ملاحظات |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

```json
{
  "regionCode": "RG-LE-00001-00001"
}
```
