CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id TEXT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    contact_email VARCHAR(150),
    contact_phone VARCHAR(50),
    address TEXT,
    status VARCHAR(20) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),

    role VARCHAR(20) CHECK (role IN ('SUPERADMIN', 'SUPPLIER')) NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categories (
    category_id TEXT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL,
    description TEXT,
    parent_category_id TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (parent_category_id)
        REFERENCES categories(category_id),
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name VARCHAR(100),
    location TEXT,
    city VARCHAR(50),
    capacity INT,
    phone VARCHAR(20),
    manager_id TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (manager_id)
        REFERENCES users(user_id)
        ON DELETE SET NULL,
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    category_id TEXT,

    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    sku VARCHAR(100),
    price NUMERIC(10,2),
    cost_price NUMERIC(10,2),
    weight DECIMAL(10,3),
    status VARCHAR(20) DEFAULT 'Active',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inventory (
    inventory_id TEXT PRIMARY KEY,
    product_id TEXT NOT NULL,
    warehouse_id TEXT NOT NULL,

    quantity INT NOT NULL DEFAULT 0,
    reorder_level INT DEFAULT 0,
    last_restocked TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    warehouse_id TEXT,
    order_number VARCHAR(100) UNIQUE,
    order_date DATE,
    expected_delivery DATE,
    total_amount NUMERIC(12,2),
    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id TEXT PRIMARY KEY,
    po_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INT NOT NULL,
    price NUMERIC(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (po_id)
        REFERENCES purchase_orders(po_id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS invoices (
    invoice_id TEXT PRIMARY KEY,
    supplier_id TEXT NOT NULL,
    po_id TEXT,
    invoice_number VARCHAR(100) UNIQUE,
    invoice_date DATE,
    total_amount NUMERIC(12,2),
    status VARCHAR(50),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (supplier_id)
        REFERENCES suppliers(supplier_id)
        ON DELETE CASCADE,
    FOREIGN KEY (po_id)
        REFERENCES purchase_orders(po_id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS invoice_items (
    invoice_item_id TEXT PRIMARY KEY,
    invoice_id TEXT NOT NULL,
    product_id TEXT NOT NULL,
    quantity INT,
    price NUMERIC(10,2),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (invoice_id)
        REFERENCES invoices(invoice_id)
        ON DELETE CASCADE,
    FOREIGN KEY (product_id)
        REFERENCES products(product_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
	customer_type VARCHAR(20) CHECK (customer_type IN ('Individual', 'Business')) DEFAULT 'Business',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS shipments (
    shipment_id TEXT PRIMARY KEY,
    po_id TEXT NOT NULL,
    warehouse_id TEXT,
    carrier_name VARCHAR(100),
    tracking_number VARCHAR(100),
    shipment_date DATE,
    estimated_arrival DATE,
    actual_arrival DATE,
    status VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by TEXT,
    updated_by TEXT,

    deleted BOOLEAN NOT NULL DEFAULT FALSE,

    FOREIGN KEY (po_id)
        REFERENCES purchase_orders(po_id)
        ON DELETE CASCADE,
    FOREIGN KEY (warehouse_id)
        REFERENCES warehouses(warehouse_id)
        ON DELETE SET NULL,
    FOREIGN KEY (created_by)
        REFERENCES users(user_id),
    FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
);