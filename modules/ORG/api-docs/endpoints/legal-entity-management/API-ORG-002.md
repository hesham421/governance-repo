# POST /api/v1/org/legal-entities/search

**Search Legal Entities**

بحث في الكيانات القانونية

Operation ID: `API-ORG-002`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: LEGAL_ENTITY_VIEW (found on service:LegalEntityService)

## Request Body

Schema: `LegalEntitySearchRequest` (application/json)

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| filters | array<ContractFilter> | No |  |  |
| sorts | array<ContractSort> | No |  |  |
| page | integer (int32) | No |  |  |
| size | integer (int32) | No |  |  |

## Response `200` — OK

Shape: `paginated list of LegalEntityResponse (see Pagination Envelope in index.md)`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |  |
| legalEntityCode | string | No |  | System-generated business code (LE-NNNNN) - الرمز الآلي | LE-00001 |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |  |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |  |
| entityTypeId | string | No |  | Entity type code (LOV-ORG-001) - نوع الكيان |  |
| isActive | boolean | No |  | Active status - حالة التفعيل |  |
| notes | string | No |  | Notes - ملاحظات |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

```json
{
  "legalEntityCode": "LE-00001"
}
```
