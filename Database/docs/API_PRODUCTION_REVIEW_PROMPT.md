# API Production Readiness Review Prompt

## Purpose

This document defines how to review every API route and backend component to ensure the system is production-grade, secure, scalable, and maintainable.

This review must prevent:

* application crashes
* unauthorized access
* data corruption
* security leaks
* performance bottlenecks
* untraceable runtime failures

The system must support:

* RBAC (ADMIN, SUPPLIER)
* JWT Authentication
* Secure API handling
* Database integrity
* Large dataset performance

All checks listed below are mandatory.

---

# Part 1 — API Route Validation

Review every API route.

Check:

* Route exists and is reachable
* HTTP method is correct (GET, POST, PUT, DELETE)
* Route naming is consistent
* Route does not expose internal logic

Validate:

Every route must:

* validate input
* authenticate user
* authorize role
* handle errors
* log failures

Reject:

* unprotected routes
* direct database access without middleware

---

# Part 2 — Error Handling and Crash Prevention

Every route must include:

* try-catch block
* structured error response
* internal error logging

Check:

All async operations must be wrapped.

Example requirement:

* No unhandled promise
* No silent failure

Error responses must include:

* error message
* error code
* timestamp
* request reference id

Application must never crash due to:

* database failure
* invalid input
* null reference
* missing resource

---

# Part 3 — Error Logging System

Verify:

Centralized logging system exists.

Logging must capture:

* API errors
* database failures
* authentication failures
* permission violations

Logs must include:

* route name
* user id
* supplier id
* timestamp
* error stack

Verify logs are written to:

* file
* or logging service

Reject:

console-only logging in production.

---

# Part 4 — Authentication System Review

Verify register and login flows.

Check:

Registration:

* password hashing exists
* strong hashing algorithm used
* duplicate email prevention
* input validation enforced

Login:

* password verification correct
* JWT generated securely
* expiration time configured
* refresh strategy exists (if implemented)

JWT Handling:

Verify:

* token encryption
* token validation middleware
* token expiration check
* signature validation

Session Storage:

Verify:

Stored:

* user_id
* role
* supplier_id (if applicable)

Reject:

* storing sensitive data in token payload unnecessarily

---

# Part 5 — Role Management Validation

Roles supported:

* ADMIN
* SUPPLIER

Verify:

* role assigned during registration
* role stored securely
* role checked before every request

Reject:

role checks only done on frontend.

Must exist:

Server-side role validation.

---

# Part 6 — RBAC Enforcement

Verify:

All queries enforce role-based filtering.

SUPPLIER users must:

Only access:

* their own supplier data
* their own products
* their own purchase orders
* their own invoices
* their own shipments

Check:

Missing supplier filter in:

* SELECT
* UPDATE
* DELETE
* Aggregation queries

Reject:

global queries without role filter.

---

# Part 7 — Environment Variable Handling

Check:

Sensitive configuration stored in environment variables.

Required:

* DB connection string
* JWT secret
* API keys
* Encryption keys

Verify:

No secrets stored in:

* source code
* repository files

Check:

.env abstraction exists.

Reject:

hardcoded credentials.

---

# Part 8 — Route Structure and Middleware

Verify:

Routes follow layered structure:

Controller → Service → Repository → Database

Reject:

Database logic inside route handlers.

Middleware must include:

* authentication middleware
* RBAC middleware
* request validation middleware

---

# Part 9 — Database Transaction Safety

Verify:

Critical operations use transactions.

Examples:

* purchase order creation
* invoice creation
* shipment updates
* inventory updates

Check:

Rollback exists on failure.

Reject:

partial writes allowed.

---

# Part 10 — Query Optimization

Review all database queries.

Check:

* indexes used
* joins optimized
* no unnecessary SELECT *

Reject:

full table scans in production queries.

Verify:

Queries support:

* filtering
* pagination
* sorting

Mandatory:

Pagination for large datasets.

---

# Part 11 — Input Validation

Verify:

All API inputs validated.

Check:

* required fields
* data types
* string length
* number ranges
* date formats

Reject:

raw input passed to database.

Use:

Schema validation system.

---

# Part 12 — Output Validation

Verify:

API responses:

* consistent format
* predictable structure

Reject:

random or inconsistent response shape.

---

# Part 13 — Rate Limiting and Abuse Protection

Verify:

Rate limiting exists.

Required protection against:

* brute force login attempts
* excessive API usage
* automated attacks

Reject:

unlimited request handling.

---

# Part 14 — Security Hardening

Verify:

System includes:

* CORS protection
* Helmet or security headers
* SQL injection protection
* XSS protection
* CSRF protection (if session-based)

Reject:

raw SQL with unsanitized inputs.

---

# Part 15 — API Timeout Handling

Verify:

Timeout configured for:

* external APIs
* database calls

Reject:

infinite waiting requests.

---

# Part 16 — Documentation and Code Comments

Verify:

Every service includes:

* function description
* parameter explanation
* return structure

Check:

Important variables documented.

Reject:

complex logic without explanation.

---

# Part 17 — Conversational Query Safety

System supports:

Natural language → SQL queries.

Verify:

Generated SQL passes through:

Security validation layer.

Required:

RBAC enforcement before execution.

Reject:

Direct execution of generated SQL.

---

# Part 18 — Background Job Safety

If background jobs exist:

Verify:

* retry logic
* failure logging
* job timeout

Reject:

silent job failure.

---

# Part 19 — Caching Strategy Review

Check:

Caching exists for:

* frequent queries
* analytics queries

Verify:

Cache invalidation rules defined.

Reject:

permanent stale cache.

---

# Part 20 — Monitoring and Observability

Verify:

System tracks:

* API latency
* error rate
* request volume

Logs must support:

Root cause investigation.

---

# Part 21 — Scalability Readiness

Verify:

System supports:

* horizontal scaling
* connection pooling
* load balancing readiness

Reject:

single-point dependency.

---

# Part 22 — Test Coverage

Verify:

Unit tests exist for:

* services
* controllers

Integration tests exist for:

* API flows
* authentication

Reject:

untested authentication logic.

---

# Part 23 — Response Time Performance

Check:

Average response time:

Must remain under:

500ms for standard queries.

Flag:

Slow queries.

---

# Part 24 — Required Output Report

Agent must generate:

## Files Reviewed

List all files.

---

## Issues Found

Grouped by:

* Security
* Performance
* Stability
* Maintainability

---

## Fixes Applied

List all modifications.

---

## Remaining Risks

List unresolved issues.

---

## Production Readiness Score

Rate system:

1–10 scale.

---

# Final Rule

No API route should:

* crash
* expose unauthorized data
* run without validation
* execute without role check

Every failure must be handled.

Every request must be secured.
