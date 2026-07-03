# POST /api/v1/org/profit-centers

**Create Profit Center**

إنشاء مركز ربح جديد

Operation ID: `API-ORG-033`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: PROFIT_CENTER_CREATE (found on service:ProfitCenterService)

## Request Body

Schema: `ProfitCenterCreateRequest` (application/json)

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| legalEntityFk | integer (int64) | Yes |  | Parent Legal Entity ID - معرف الكيان القانوني الأب | 1 |
| nameAr | string | Yes | maxLength: 200 | Arabic name - الاسم بالعربية | مركز ربح التجزئة |
| nameEn | string | Yes | maxLength: 100 | English name - الاسم بالإنجليزية | Retail Profit Center |
| notes | string | No | maxLength: 2000 | Notes - ملاحظات | Covers retail division |

**Request Example**

```json
{
  "legalEntityFk": 1,
  "nameAr": "مركز ربح التجزئة",
  "nameEn": "Retail Profit Center",
  "notes": "Covers retail division"
}
```

## Response `200` — OK

Shape: `ProfitCenterResponse`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |
| profitCenterCode | string | No |  | System-generated business code (PC-[LE_CODE]-NNNNN) - الرمز الآلي |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |
| legalEntityFk | integer (int64) | No |  | Parent Legal Entity ID - معرف الكيان القانوني الأب |
| legalEntityCode | string | No |  | Parent Legal Entity business code - رمز الكيان القانوني الأب |
| legalEntityNameEn | string | No |  | Parent Legal Entity English name - اسم الكيان القانوني الأب |
| isActive | boolean | No |  | Active status - حالة التفعيل |
| notes | string | No |  | Notes - ملاحظات |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |
| createdBy | string | No |  | Created by - أنشئ بواسطة |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |
