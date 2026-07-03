# PUT /api/v1/org/branches/{id}/activate

**Activate Branch**

تفعيل فرع

Operation ID: `API-ORG-011`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: BRANCH_UPDATE (found on service:BranchService)

## Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

## Response `200` — OK

Shape: `BranchResponse`

| Field | Type | Required | Constraints | Description | Example |
|---|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |  |
| branchCode | string | No |  | System-generated business code (BR-[LE_CODE]-NNNNN) - الرمز الآلي | BR-LE-00001-00001 |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |  |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |  |
| legalEntityFk | integer (int64) | No |  | Parent Legal Entity ID - معرف الكيان القانوني الأب |  |
| legalEntityCode | string | No |  | Parent Legal Entity business code - رمز الكيان القانوني الأب |  |
| legalEntityNameEn | string | No |  | Parent Legal Entity English name - اسم الكيان القانوني الأب |  |
| branchTypeId | string | No |  | Branch type code (LOV-ORG-002) - نوع الفرع |  |
| isActive | boolean | No |  | Active status - حالة التفعيل |  |
| notes | string | No |  | Notes - ملاحظات |  |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |  |
| createdBy | string | No |  | Created by - أنشئ بواسطة |  |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |  |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |  |

**Response Example**

```json
{
  "branchCode": "BR-LE-00001-00001"
}
```
