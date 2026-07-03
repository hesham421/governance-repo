# PUT /api/v1/org/regions/{id}

**Update Region**

تحديث منطقة

Operation ID: `API-ORG-015`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: REGION_UPDATE (found on service:RegionService)

## Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

## Request Body

Schema: `RegionUpdateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| nameAr | string | No | maxLength: 200 | Arabic name - الاسم بالعربية | منطقة القاهرة الكبرى |
| nameEn | string | No | maxLength: 100 | English name - الاسم بالإنجليزية | Greater Cairo Region |
| notes | string | No | maxLength: 2000 | Notes - ملاحظات | Covers all Cairo branches |

**Request Example**

```json
{
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
