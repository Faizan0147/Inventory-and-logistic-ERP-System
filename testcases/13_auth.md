# Auth API Test Cases
**Base URL:** `/api/v1/auth`
**Status:** ⏳ Pending

---

## 1. REGISTER REQUEST (POST `/register`)

**1.1 Valid Registration Request**
```json
POST /api/v1/auth/register
Body:
{
  "name": "Jane Smith",
  "email": "jane.smith@company.com",
  "phone": "+971501234567",
  "company_name": "Smith Supplies LLC",
  "message": "Requesting access to manage our inventory"
}
Expected: 201 Created — Registration request object
```

**1.2 Minimum Required Fields**
```json
{
  "name": "Bob Jones",
  "email": "bob@example.com"
}
Expected: 201 Created
```

**1.3 Missing name**
```json
{
  "email": "test@test.com"
}
Expected: 422 — {"detail": "name is required"}
```

**1.4 Missing email**
```json
{
  "name": "Test User"
}
Expected: 422 — {"detail": "email is required"}
```

**1.5 Invalid email format**
```json
{
  "name": "Test User",
  "email": "not-an-email"
}
Expected: 422
```

---

## 2. LOGIN (POST `/login`)

**2.1 Valid Login**
```json
POST /api/v1/auth/login
Body:
{
  "email": "user@example.com",
  "password": "CorrectPassword123"
}
Expected: 200 — {"access_token": "...", "token_type": "bearer", "user": {...}}
```

**2.2 Wrong Password**
```json
{
  "email": "user@example.com",
  "password": "WrongPassword"
}
Expected: 401 Unauthorized
```

**2.3 Non-existent Email**
```json
{
  "email": "nonexistent@example.com",
  "password": "SomePassword"
}
Expected: 401 Unauthorized
```

**2.4 Missing email**
```json
{
  "password": "SomePassword"
}
Expected: 422 — {"detail": "email is required"}
```

**2.5 Missing password**
```json
{
  "email": "user@example.com"
}
Expected: 422 — {"detail": "password is required"}
```

**2.6 Inactive User Login**
```json
{
  "email": "inactive_user@example.com",
  "password": "CorrectPassword"
}
Expected: 403 Forbidden
```

---

## 3. LOGOUT (POST `/logout`)

**3.1 Valid Logout**
```
POST /api/v1/auth/logout
Headers: Authorization: Bearer <token>
Expected: 200 — {"message": "Logged out successfully"}
```

**3.2 No Token**
```
POST /api/v1/auth/logout
No Authorization header
Expected: 401 Unauthorized
```

---

## 4. TOKEN VALIDATION

**4.1 Valid Token on Protected Route**
```
GET /api/v1/suppliers
Headers: Authorization: Bearer <valid_token>
Expected: 200
```

**4.2 Expired Token**
```
GET /api/v1/suppliers
Headers: Authorization: Bearer <expired_token>
Expected: 401 Unauthorized
```

**4.3 Invalid Token**
```
GET /api/v1/suppliers
Headers: Authorization: Bearer invalid.token.here
Expected: 401 Unauthorized
```

**4.4 No Token on Protected Route**
```
GET /api/v1/suppliers
No Authorization header
Expected: 401 Unauthorized
```
