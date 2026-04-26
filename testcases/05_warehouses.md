# Warehouses API Test Cases
**Base URL:** `/api/v1/warehouses`
**Status:** 🔄 In Progress

---

## 1. CREATE (POST `/`)

**1.1 Full Valid Warehouse**
```json
{
  "warehouse_name": "Main Warehouse Dubai",
  "location": "Industrial Area, Zone 5",
  "city": "Dubai",
  "capacity": 5000,
  "phone": "+971501234567",
  "is_active": true
}
Expected: 201 Created
```

**1.2 Minimum Required Fields**
```json
{
  "warehouse_name": "Secondary Warehouse"
}
Expected: 201 Created
```

**1.3 Missing warehouse_name**
```json
{
  "city": "Abu Dhabi",
  "capacity": 1000
}
Expected: 422 — {"detail": "warehouse_name is required"}
```

---

## 2. LIST (GET `/`)

**2.1 List All**
```
GET /api/v1/warehouses
Expected: 200 — Array of warehouse objects
```

**2.2 Pagination**
```
GET /api/v1/warehouses?offset=0&limit=2
Expected: 200 — Max 2 warehouses
```

---

## 3. GET Single (GET `/{warehouse_id}`)

**3.1 Valid ID**
```
GET /api/v1/warehouses/{warehouse_id}
Expected: 200 — Full warehouse object with timestamps
```

**3.2 Invalid ID**
```
GET /api/v1/warehouses/non-existent-id
Expected: 404 — {"detail": "Warehouse not found"}
```

---

## 4. UPDATE (PUT `/{warehouse_id}`)

**4.1 Update Multiple Fields**
```json
{
  "warehouse_name": "Main Warehouse Dubai - Updated",
  "capacity": 8000,
  "city": "Sharjah",
  "is_active": false
}
Expected: 200 — Updated warehouse object
```

**4.2 Update Single Field**
```json
{ "phone": "+971509999999" }
Expected: 200
```

**4.3 Non-existent Warehouse**
```
PUT /api/v1/warehouses/non-existent-id
Expected: 404 — {"detail": "Warehouse not found or access denied"}
```

---

## 5. DELETE (DELETE `/{warehouse_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/warehouses/{warehouse_id}
Expected: 200 — {"message": "Warehouse deleted successfully"}
```

**5.2 Non-existent Warehouse**
```
DELETE /api/v1/warehouses/non-existent-id
Expected: 404 — {"detail": "Warehouse not found"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/warehouses/{warehouse_id}  → 200
2. GET    /api/v1/warehouses/{warehouse_id}  → 404
```
