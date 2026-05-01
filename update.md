# Nested FK Data — Change Tracker

## Summary
All `Read` DTOs that reference foreign keys now return nested summary objects
instead of bare IDs. Repositories were updated to use `LEFT JOIN` queries and
a `_build()` helper to assemble the nested response. The pattern used is:

- **INSERT / UPDATE** → write only the FK id column (no change to write path)
- **SELECT (get / list)** → `LEFT JOIN` the referenced table, build nested object
- Nested object is `None` when the FK is `NULL` or the referenced row is soft-deleted

---

## Status Legend
- ✅ Done
- ⏳ Pending
- ➖ Not applicable (no FK to nest)

---

## APIs

### 1. Category — `app/dto/category.py` · `app/repositories/category_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `parent_category_id` | `categories.category_id` | `parent_category: ParentCategory` | ✅ Already done (pre-existing) |

**Nested model:**
```python
class ParentCategory(BaseModel):
    category_id: str
    category_name: str
    description: Optional[str]
```

---

### 2. Product — `app/dto/product.py` · `app/repositories/product_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `supplier_id` | `suppliers` | `supplier: SupplierSummary` | ✅ Done |
| `category_id` | `categories` | `category: CategorySummary` | ✅ Done |

**Nested models:**
```python
class SupplierSummary(BaseModel):
    supplier_id: str
    supplier_name: str
    contact_email: Optional[str]
    contact_phone: Optional[str]

class CategorySummary(BaseModel):
    category_id: str
    category_name: str
    description: Optional[str]
```

**Repo change:** `_SELECT` uses `LEFT JOIN suppliers` + `LEFT JOIN categories`.
`create_product` and `update_product` now `RETURNING product_id` then call `get_product()`.

---

### 3. Inventory — `app/dto/inventory.py` · `app/repositories/inventory_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `product_id` | `products` | `product: ProductSummary` | ✅ Done |
| `warehouse_id` | `warehouses` | `warehouse: WarehouseSummary` | ✅ Done |

**Nested models:**
```python
class ProductSummary(BaseModel):
    product_id: str
    product_name: str
    sku: str
    price: Optional[Decimal]

class WarehouseSummary(BaseModel):
    warehouse_id: str
    warehouse_name: str
    location: Optional[str]
    city: Optional[str]
```

**Repo change:** `_SELECT` uses `LEFT JOIN products` + `LEFT JOIN warehouses`.

---

### 4. Purchase Order — `app/dto/purchase_order.py` · `app/repositories/purchase_order_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `supplier_id` | `suppliers` | `supplier: SupplierSummary` | ✅ Done |
| `warehouse_id` | `warehouses` | `warehouse: WarehouseSummary` | ✅ Done |

**Nested models:** same `SupplierSummary` / `WarehouseSummary` shapes as above.

**Repo change:** `_SELECT` uses `LEFT JOIN suppliers` + `LEFT JOIN warehouses`.

---

### 5. Purchase Order Item (POI) — `app/dto/poi.py` · `app/repositories/poi_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `po_id` | `purchase_orders` | `purchase_order: PurchaseOrderSummary` | ✅ Done |
| `product_id` | `products` | `product: ProductSummary` | ✅ Done |

**Nested models:**
```python
class PurchaseOrderSummary(BaseModel):
    po_id: str
    order_number: Optional[str]
    order_date: Optional[date]
    status: Optional[str]

class ProductSummary(BaseModel):
    product_id: str
    product_name: str
    sku: str
    price: Optional[Decimal]
```

**Repo change:** `_SELECT` uses `LEFT JOIN purchase_orders` + `LEFT JOIN products`.

---

### 6. Invoice — `app/dto/invoice.py` · `app/repositories/invoice_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `supplier_id` | `suppliers` | `supplier: SupplierSummary` | ✅ Done |
| `po_id` | `purchase_orders` | `purchase_order: PurchaseOrderSummary` | ✅ Done |

**Nested models:** same `SupplierSummary` / `PurchaseOrderSummary` shapes as above.

**Repo change:** `_SELECT` uses `LEFT JOIN suppliers` + `LEFT JOIN purchase_orders`.

---

### 7. Invoice Item — `app/dto/invoice_item.py` · `app/repositories/invoice_item_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `invoice_id` | `invoices` | `invoice: InvoiceSummary` | ✅ Done |
| `product_id` | `products` | `product: ProductSummary` | ✅ Done |

**Nested models:**
```python
class InvoiceSummary(BaseModel):
    invoice_id: str
    invoice_number: Optional[str]
    invoice_date: Optional[date]
    total_amount: Optional[Decimal]
    status: Optional[str]
```

**Repo change:** `_SELECT` uses `LEFT JOIN invoices` + `LEFT JOIN products`.

---

### 8. Shipment — `app/dto/shipments.py` · `app/repositories/shipments_repo.py`
| Field | References | Nested As | Status |
|---|---|---|---|
| `po_id` | `purchase_orders` | `purchase_order: PurchaseOrderSummary` | ✅ Done |
| `warehouse_id` | `warehouses` | `warehouse: WarehouseSummary` | ✅ Done |

**`PurchaseOrderSummary` for shipments also includes `supplier_id`** so the frontend
can identify the supplier without an extra call.

**Repo change:** `_SELECT` uses `LEFT JOIN purchase_orders` + `LEFT JOIN warehouses`.

---

## No Changes Needed
| Entity | Reason |
|---|---|
| Supplier | No FK references to other domain entities |
| Warehouse | No FK references to other domain entities |
| Customer | No FK references to other domain entities |
| User | No FK references to other domain entities |

---

## Implementation Notes
- All `_build()` helpers guard against `None` — if the JOIN returns no match
  (FK is NULL or referenced row is soft-deleted), the nested field is `None`.
- Write paths (INSERT/UPDATE) are unchanged — they still accept and store only the FK id.
- `create_*` and `update_*` now do `RETURNING <pk>` then call `get_*()` to return
  the fully-joined response, adding one extra round-trip per write (acceptable trade-off).
