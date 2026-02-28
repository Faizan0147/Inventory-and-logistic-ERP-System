-- =============================
-- PROCUREMENT
-- =============================

CREATE TABLE supplier (
    supplier_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    contact_info TEXT,
    address TEXT
);

CREATE TABLE supplier_bank_details (
    bank_detail_id UUID PRIMARY KEY,
    supplier_id UUID NOT NULL REFERENCES supplier(supplier_id) ON DELETE CASCADE,
    bank_name TEXT NOT NULL,
    account_number TEXT NOT NULL,
    routing_number TEXT
);

CREATE TABLE product (
    product_id UUID PRIMARY KEY,
    category_id UUID,
    name TEXT NOT NULL,
    sku TEXT UNIQUE NOT NULL,
    description TEXT,
    unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE product_supplier (
    product_id UUID REFERENCES product(product_id) ON DELETE CASCADE,
    supplier_id UUID REFERENCES supplier(supplier_id) ON DELETE CASCADE,
    cost_price NUMERIC(14,2) NOT NULL CHECK (cost_price >= 0),
    lead_time_days INT CHECK (lead_time_days >= 0),
    preferred BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (product_id, supplier_id)
);

CREATE TABLE warehouse (
    warehouse_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    capacity INT CHECK (capacity >= 0)
);

CREATE TABLE purchase_order (
    po_id UUID PRIMARY KEY,
    supplier_id UUID NOT NULL REFERENCES supplier(supplier_id),
    warehouse_id UUID NOT NULL REFERENCES warehouse(warehouse_id),
    order_date TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    total_amount NUMERIC(14,2) CHECK (total_amount >= 0)
);

CREATE TABLE purchase_order_item (
    po_id UUID REFERENCES purchase_order(po_id) ON DELETE CASCADE,
    product_id UUID REFERENCES product(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_cost NUMERIC(14,2) NOT NULL CHECK (unit_cost >= 0),
    PRIMARY KEY (po_id, product_id)
);

-- =============================
-- INVENTORY
-- =============================

CREATE TABLE category (
    category_id UUID PRIMARY KEY,
    parent_category_id UUID REFERENCES category(category_id),
    name TEXT NOT NULL,
    description TEXT
);

CREATE TABLE warehouse_zone (
    zone_id UUID PRIMARY KEY,
    warehouse_id UUID NOT NULL REFERENCES warehouse(warehouse_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    zone_type TEXT
);

CREATE TABLE stock (
    product_id UUID REFERENCES product(product_id),
    warehouse_id UUID REFERENCES warehouse(warehouse_id),
    zone_id UUID REFERENCES warehouse_zone(zone_id),
    quantity INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_level INT DEFAULT 0 CHECK (reorder_level >= 0),
    PRIMARY KEY (product_id, warehouse_id, zone_id)
);

CREATE TABLE inventory_transaction (
    transaction_id UUID PRIMARY KEY,
    product_id UUID NOT NULL REFERENCES product(product_id),
    warehouse_id UUID NOT NULL REFERENCES warehouse(warehouse_id),
    quantity_change INT NOT NULL,
    reference_type TEXT NOT NULL,
    reference_id UUID,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- SALES
-- =============================

CREATE TABLE customer (
    customer_id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT,
    address TEXT
);

CREATE TABLE sales_order (
    order_id UUID PRIMARY KEY,
    customer_id UUID NOT NULL REFERENCES customer(customer_id),
    warehouse_id UUID NOT NULL REFERENCES warehouse(warehouse_id),
    order_date TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    total_amount NUMERIC(14,2) CHECK (total_amount >= 0)
);

CREATE TABLE sales_order_item (
    order_id UUID REFERENCES sales_order(order_id) ON DELETE CASCADE,
    product_id UUID REFERENCES product(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(14,2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);

CREATE TABLE invoice (
    invoice_id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES sales_order(order_id),
    invoice_date TIMESTAMP NOT NULL,
    due_date TIMESTAMP,
    status TEXT NOT NULL,
    total_amount NUMERIC(14,2) CHECK (total_amount >= 0)
);

-- =============================
-- LOGISTICS
-- =============================

CREATE TABLE inbound_shipment (
    inbound_shipment_id UUID PRIMARY KEY,
    po_id UUID NOT NULL REFERENCES purchase_order(po_id),
    warehouse_id UUID NOT NULL REFERENCES warehouse(warehouse_id),
    ship_date TIMESTAMP,
    status TEXT NOT NULL
);

CREATE TABLE inbound_shipment_item (
    inbound_shipment_id UUID REFERENCES inbound_shipment(inbound_shipment_id) ON DELETE CASCADE,
    product_id UUID REFERENCES product(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (inbound_shipment_id, product_id)
);

CREATE TABLE outbound_shipment (
    outbound_shipment_id UUID PRIMARY KEY,
    order_id UUID NOT NULL REFERENCES sales_order(order_id),
    warehouse_id UUID NOT NULL REFERENCES warehouse(warehouse_id),
    ship_date TIMESTAMP,
    status TEXT NOT NULL,
    tracking_number TEXT
);

CREATE TABLE outbound_shipment_item (
    outbound_shipment_id UUID REFERENCES outbound_shipment(outbound_shipment_id) ON DELETE CASCADE,
    product_id UUID REFERENCES product(product_id),
    quantity INT NOT NULL CHECK (quantity > 0),
    PRIMARY KEY (outbound_shipment_id, product_id)
);

-- =============================
-- RETURNS
-- =============================

CREATE TABLE sales_return (
    sales_return_id UUID PRIMARY KEY,
    order_id UUID REFERENCES sales_order(order_id),
    customer_id UUID REFERENCES customer(customer_id),
    warehouse_id UUID REFERENCES warehouse(warehouse_id),
    return_date TIMESTAMP NOT NULL,
    reason TEXT,
    status TEXT
);

CREATE TABLE purchase_return (
    purchase_return_id UUID PRIMARY KEY,
    po_id UUID REFERENCES purchase_order(po_id),
    supplier_id UUID REFERENCES supplier(supplier_id),
    warehouse_id UUID REFERENCES warehouse(warehouse_id),
    return_date TIMESTAMP NOT NULL,
    reason TEXT,
    status TEXT
);

-- =============================
-- SECURITY
-- =============================

CREATE TABLE role (
    role_id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE permission (
    permission_id UUID PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE role_permission (
    role_id UUID REFERENCES role(role_id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permission(permission_id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE app_user (
    user_id UUID PRIMARY KEY,
    role_id UUID REFERENCES role(role_id),
    warehouse_id UUID REFERENCES warehouse(warehouse_id),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL
);

-- =============================
-- SYSTEM
-- =============================

CREATE TABLE notification (
    notification_id UUID PRIMARY KEY,
    recipient_user_id UUID REFERENCES app_user(user_id),
    title TEXT,
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE
);

CREATE TABLE audit_log (
    log_id UUID PRIMARY KEY,
    changed_by UUID REFERENCES app_user(user_id),
    entity_type TEXT,
    entity_id UUID,
    action TEXT,
    change_details JSONB,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);