# GET /api/v1/org/location-sites/{id}

**Get Location Site by ID**

جلب موقع عمل بالمعرف

Operation ID: `API-ORG-044`

**Authentication**

Required (Bearer Authentication).

**Required permission(s)**: LOCATION_SITE_VIEW (found on service:LocationSiteService)

## Path Parameters

| Name | Type | Required | Description |
|---|---|---|---|
| id | integer | Yes |  |

## Response `200` — OK

Shape: `LocationSiteResponse`

| Field | Type | Required | Constraints | Description |
|---|---|---|---|---|
| id | integer (int64) | No |  | Unique identifier - المعرف الفريد |
| locationSiteCode | string | No |  | System-generated business code (LS-[BR_CODE]-NNNNN) - الرمز الآلي |
| nameAr | string | No |  | Arabic name - الاسم بالعربية |
| nameEn | string | No |  | English name - الاسم بالإنجليزية |
| branchFk | integer (int64) | No |  | Parent Branch ID - معرف الفرع الأب |
| branchCode | string | No |  | Parent Branch business code - رمز الفرع الأب |
| branchNameEn | string | No |  | Parent Branch English name - اسم الفرع الأب |
| siteTypeId | string | No |  | Site type code (LOV-ORG-006) - نوع الموقع |
| isActive | boolean | No |  | Active status - حالة التفعيل |
| notes | string | No |  | Notes - ملاحظات |
| createdAt | string (date-time) | No |  | Created timestamp - تاريخ الإنشاء |
| createdBy | string | No |  | Created by - أنشئ بواسطة |
| updatedAt | string (date-time) | No |  | Updated timestamp - تاريخ التحديث |
| updatedBy | string | No |  | Updated by - حُدّث بواسطة |
