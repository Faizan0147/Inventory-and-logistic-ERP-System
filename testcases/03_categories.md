# Categories API Test Cases
**Base URL:** `/api/v1/categories`
**Status:** ✅ Tested

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Category**
```json
{
  "category_name": "Electronics",
  "description": "Electronic devices and accessories"
}
Expected: 201 Created
```

**1.2 Category with Parent**
```json
{
  "category_name": "Laptops",
  "description": "Portable computers",
  "parent_category_id": "<category_id from 1.1>"
}
Expected: 201 Created
```

**1.3 Minimum Required Fields**
```json
{
  "category_name": "Furniture"
}
Expected: 201 Created
```

**1.4 Missing category_name**
```json
{
  "description": "Some description"
}
Expected: 422 — {"detail": "category_name is required"}
```

**1.5 Invalid parent_category_id**
```json
{
  "category_name": "Sub Category",
  "parent_category_id": "non-existent-id"
}
Expected: 409 — {"detail": "Invalid parent_category_id."}
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/categories
Expected: 200 — Array of category objects
```

**2.2 Pagination**
```
GET /api/v1/categories?offset=0&limit=5
Expected: 200 — Max 5 categories
```

---

## 3. GET Single (GET `/{category_id}`)

**3.1 Valid ID**
```
GET /api/v1/categories/{category_id}
Expected: 200 — Category object
```

**3.2 Invalid ID**
```
GET /api/v1/categories/non-existent-id
Expected: 404 — {"detail": "Category not found"}
```

---

## 4. UPDATE (PUT `/{category_id}`)

**4.1 Valid Update**
```json
{
  "category_name": "Electronics & Gadgets",
  "description": "Updated description"
}
Expected: 200 — Updated category object
```

**4.2 Assign Parent**
```json
{ "parent_category_id": "<valid_parent_id>" }
Expected: 200
```

**4.3 Non-existent Category**
```
PUT /api/v1/categories/non-existent-id
Expected: 404 — {"detail": "Category not found"}
```

---

## 5. DELETE (DELETE `/{category_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/categories/{category_id}
Expected: 200 — {"message": "Category deleted successfully"}
```

**5.2 Non-existent Category**
```
DELETE /api/v1/categories/non-existent-id
Expected: 404 — {"detail": "Category not found"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/categories/{category_id}  → 200
2. GET    /api/v1/categories/{category_id}  → 404
```
