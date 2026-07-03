# PUT /api/v1/org/legal-entities/{id}/deactivate

**Deactivate Legal Entity**

إلغاء تفعيل كيان قانوني

Operation ID: `API-ORG-004`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: LEGAL_ENTITY_UPDATE (found on service:LegalEntityService)

## Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

## Response `200` — OK

Shape: `LegalEntityResponse`

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
