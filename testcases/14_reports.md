# Reports API Test Cases
**Base URL:** `/api/v1/reports`
**Status:** ⏳ Pending
**Note:** Filters are intentionally out of scope for this phase.

---

## 1. Users Report

```
GET /api/v1/reports/users
Expected: 200 — { summary, rows[] }
```

```
GET /api/v1/reports/users/summary
Expected: 200 — users KPIs only
```

```
GET /api/v1/reports/users/export/csv
Expected: 200
Headers include: Content-Disposition: attachment; filename="users-report-YYYY-MM.csv"
CSV columns: User ID, Name, Email, Role, Status, Created At
```

---

## 2. Categories Report

```
GET /api/v1/reports/categories
Expected: 200 — total/parent/child/products_per_category + rows
```

```
GET /api/v1/reports/categories/export/csv
Expected: 200
Filename pattern: categories-report-YYYY-MM.csv
CSV columns: Category ID, Category Name, Parent Category, Product Count, Created At
```

---

## 3. Products Report

```
GET /api/v1/reports/products
Expected: 200 — product KPIs + rows
```

```
GET /api/v1/reports/products/export/csv
Expected: 200
Filename pattern: products-report-YYYY-MM.csv
CSV columns: Product ID, Product Name, SKU, Supplier, Category, Price, Cost Price, Status, Created At
```

---

## 4. Inventory Report

```
GET /api/v1/reports/inventory
Expected: 200 — inventory KPIs + rows
```

```
GET /api/v1/reports/inventory/export/csv
Expected: 200
Filename pattern: inventory-report-YYYY-MM.csv
CSV columns: Product, Warehouse, Quantity, Reorder Level, Last Restocked, Updated At
```

---

## 5. Purchase Orders Report

```
GET /api/v1/reports/purchase-orders
Expected: 200 — order status KPIs + rows
```

```
GET /api/v1/reports/purchase-orders/export/csv
Expected: 200
Filename pattern: purchase-orders-report-YYYY-MM.csv
CSV columns: PO Number, Supplier, Warehouse, Order Date, Expected Delivery, Total Amount, Status
```

---

## 6. Purchase Order Items Report

```
GET /api/v1/reports/purchase-order-items
Expected: 200 — most ordered / quantity ordered / supplier volume + rows
```

```
GET /api/v1/reports/purchase-order-items/export/csv
Expected: 200
Filename pattern: purchase-order-items-report-YYYY-MM.csv
CSV columns: PO Item ID, PO Number, Product, Quantity, Price, Total
```

---

## 7. Invoices Report

```
GET /api/v1/reports/invoices
Expected: 200 — revenue and invoice status KPIs + rows
```

```
GET /api/v1/reports/invoices/export/csv
Expected: 200
Filename pattern: invoices-report-YYYY-MM.csv
CSV columns: Invoice Number, Supplier, PO Number, Invoice Date, Total Amount, Status
```

---

## 8. Invoice Items Report

```
GET /api/v1/reports/invoice-items
Expected: 200 — best selling / product revenue / quantity sold + rows
```

```
GET /api/v1/reports/invoice-items/export/csv
Expected: 200
Filename pattern: invoice-items-report-YYYY-MM.csv
CSV columns: Invoice Item ID, Invoice Number, Product, Quantity, Price, Total
```

---

## 9. Shipments Report

```
GET /api/v1/reports/shipments
Expected: 200 — active/delivered/delayed/carrier performance + rows
```

```
GET /api/v1/reports/shipments/export/csv
Expected: 200
Filename pattern: shipments-report-YYYY-MM.csv
CSV columns: Shipment ID, Tracking Number, Carrier, Shipment Date, Estimated Arrival, Status
```

---

## 10. Common Validation Checklist

```
All /export/csv endpoints:
- preserve column order
- export filtered rows only (future when filters are added)
- return UTF-8 CSV
- quote comma-containing fields safely
- support empty-state exports (header-only CSV)
```

```
No-data behavior:
- /reports/{module} returns 200 with empty rows and zeroed summary values
- /reports/{module}/export/csv returns 200 with only header row
```
