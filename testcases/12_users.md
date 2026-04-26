# Users API Test Cases
**Base URL:** `/api/v1/users`
**Status:** ⏳ Pending
**Note:** Create, List, Get require SUPERADMIN role

---

## 1. CREATE (POST `/`)

**1.1 Full Valid User**
```json
POST /api/v1/users
Headers: Authorization: Bearer <superadmin_token>
Body:
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123",
  "phone_number": "+971501234567",
  "role": "SUPPLIER"
}
Expected: 201 Created
```

**1.2 SUPERADMIN Role**
```json
{
  "name": "Admin User",
  "email": "admin@example.com",
  "password": "AdminPass123",
  "role": "SUPERADMIN"
}
Expected: 201 Created
```

**1.3 Duplicate Email**
```json
{
  "name": "Another User",
  "email": "john.doe@example.com",
  "password": "Pass123",
  "role": "SUPPLIER"
}
Expected: 409 — duplicate email error
```

**1.4 Missing name**
```json
{
  "email": "test@test.com",
  "password": "Pass123"
}
Expected: 422 — {"detail": "name is required"}
```

**1.5 Missing email**
```json
{
  "name": "Test User",
  "password": "Pass123"
}
Expected: 422 — {"detail": "email is required"}
```

**1.6 Missing password**
```json
{
  "name": "Test User",
  "email": "test2@test.com"
}
Expected: 422 — {"detail": "password is required"}
```

**1.7 Invalid role**
```json
{
  "name": "Test",
  "email": "test3@test.com",
  "password": "Pass123",
  "role": "MANAGER"
}
Expected: 409 (DB check constraint — allowed: SUPERADMIN, SUPPLIER)
```

**1.8 Non-SUPERADMIN trying to create user**
```
Headers: Authorization: Bearer <supplier_token>
Expected: 403 Forbidden
```

---

## 2. LIST (GET `/`)

**2.1 List All (SUPERADMIN)**
```
GET /api/v1/users
Headers: Authorization: Bearer <superadmin_token>
Expected: 200 — Array of user objects
```

**2.2 Non-SUPERADMIN Access**
```
Headers: Authorization: Bearer <supplier_token>
Expected: 403 Forbidden
```

**2.3 Pagination**
```
GET /api/v1/users?offset=0&limit=5
Expected: 200 — Max 5 users
```

---

## 3. GET Single (GET `/{user_id}`)

**3.1 Valid ID (SUPERADMIN)**
```
GET /api/v1/users/{user_id}
Headers: Authorization: Bearer <superadmin_token>
Expected: 200 — User object
```

**3.2 Invalid ID**
```
GET /api/v1/users/non-existent-id
Expected: 404 — {"detail": "User not found"}
```

---

## 4. UPDATE (PUT `/{user_id}`)

**4.1 Update Name and Phone**
```json
{
  "name": "John Doe Updated",
  "phone_number": "+971509999999"
}
Expected: 200 — Updated user object
```

**4.2 Deactivate User**
```json
{ "is_active": false }
Expected: 200
```

**4.3 Non-existent User**
```
PUT /api/v1/users/non-existent-id
Expected: 404 — {"detail": "User not found or access denied"}
```

---

## 5. DELETE (DELETE `/{user_id}`)

**5.1 Valid Delete**
```
DELETE /api/v1/users/{user_id}
Expected: 200 — {"message": "User deleted successfully"}
```

**5.2 Non-existent User**
```
DELETE /api/v1/users/non-existent-id
Expected: 404 — {"detail": "User not found or access denied"}
```

**5.3 Soft Delete Verification**
```
1. DELETE /api/v1/users/{user_id}  → 200
2. GET    /api/v1/users/{user_id}  → 404
```
