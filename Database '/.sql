title Digital ERP System (Enterprise Version)

// ================= PROCUREMENT =================

supplier [icon: truck, color: blue] {
  SupplierID string pk
  Name string
  ContactInfo string
  Address string
}

supplier_bank_details [icon: credit-card, color: blue] {
  BankDetailID string pk
  SupplierID string fk
  BankName string
  AccountNumber string
  RoutingNumber string
}

product_supplier [icon: link, color: blue] {
  ProductID string fk
  SupplierID string fk
  CostPrice decimal
  LeadTimeDays int
  Preferred boolean
}

purchase_order [icon: clipboard, color: blue] {
  POID string pk
  SupplierID string fk
  WarehouseID string fk
  OrderDate timestamp
  Status string
  TotalAmount decimal
}

purchase_order_item [icon: list, color: blue] {
  POItemID string pk
  POID string fk
  ProductID string fk
  Quantity int
  UnitCost decimal
}

goods_receipt [icon: download, color: blue] {
  GRNID string pk
  POID string fk
  WarehouseID string fk
  ReceiptDate timestamp
  Status string
}

goods_receipt_item [icon: list, color: blue] {
  GRNItemID string pk
  GRNID string fk
  ProductID string fk
  ReceivedQty int
}

// ================= INVENTORY =================

category [icon: folder, color: green] {
  CategoryID string pk
  ParentCategoryID string fk
  Name string
  Description string
}

product [icon: box, color: green] {
  ProductID string pk
  CategoryID string fk
  Name string
  SKU string
  Description string
  UnitPrice decimal
}

stock [icon: package, color: green] {
  ProductID string fk
  WarehouseID string fk
  ZoneID string fk
  Quantity int
  ReorderLevel int
}

inventory_transaction [icon: repeat, color: green] {
  TransactionID string pk
  ProductID string fk
  WarehouseID string fk
  QuantityChange int
  ReferenceType string
  ReferenceID string
  TransactionDate timestamp
}

// ================= WAREHOUSE =================

warehouse [icon: home, color: orange] {
  WarehouseID string pk
  Name string
  Location string
  Capacity int
}

warehouse_zone [icon: grid, color: orange] {
  ZoneID string pk
  WarehouseID string fk
  Name string
  ZoneType string
}

// ================= SALES =================

customer [icon: user, color: purple] {
  CustomerID string pk
  Name string
  Email string
  Phone string
  Address string
}

sales_order [icon: shopping-cart, color: purple] {
  OrderID string pk
  CustomerID string fk
  WarehouseID string fk
  OrderDate timestamp
  Status string
  TotalAmount decimal
}

sales_order_item [icon: list, color: purple] {
  OrderItemID string pk
  OrderID string fk
  ProductID string fk
  Quantity int
  UnitPrice decimal
}

invoice [icon: file-text, color: purple] {
  InvoiceID string pk
  OrderID string fk
  InvoiceDate timestamp
  DueDate timestamp
  Status string
  TotalAmount decimal
}

// ================= LOGISTICS =================

inbound_shipment [icon: download, color: yellow] {
  InboundShipmentID string pk
  POID string fk
  WarehouseID string fk
  ShipDate timestamp
  Status string
}

outbound_shipment [icon: send, color: yellow] {
  OutboundShipmentID string pk
  OrderID string fk
  WarehouseID string fk
  ShipDate timestamp
  Status string
  TrackingNumber string
}

shipment_item [icon: list, color: yellow] {
  ShipmentItemID string pk
  ProductID string fk
  Quantity int
}

// ================= RETURNS =================

sales_return [icon: rotate-ccw, color: red] {
  SalesReturnID string pk
  OrderID string fk
  CustomerID string fk
  WarehouseID string fk
  ReturnDate timestamp
  Reason string
  Status string
}

purchase_return [icon: rotate-ccw, color: red] {
  PurchaseReturnID string pk
  POID string fk
  SupplierID string fk
  WarehouseID string fk
  ReturnDate timestamp
  Reason string
  Status string
}

// ================= FINANCE =================

currency [icon: dollar-sign, color: gray] {
  CurrencyID string pk
  Code string
  Name string
  Symbol string
}

exchange_rate [icon: trending-up, color: gray] {
  FromCurrency string fk
  ToCurrency string fk
  EffectiveDate timestamp
  Rate decimal
}

bill [icon: file, color: gray] {
  BillID string pk
  POID string fk
  SupplierID string fk
  BillDate timestamp
  DueDate timestamp
  TotalAmount decimal
  Status string
}

payment [icon: credit-card, color: gray] {
  PaymentID string pk
  InvoiceID string fk
  BillID string fk
  Amount decimal
  PaymentMethod string
  PaymentDate timestamp
}

// ===== Accounting Foundation =====

chart_of_accounts [icon: book, color: gray] {
  AccountID string pk
  AccountName string
  AccountType string
}

journal_entry [icon: edit, color: gray] {
  JournalEntryID string pk
  EntryDate timestamp
  ReferenceType string
  ReferenceID string
}

journal_entry_line [icon: list, color: gray] {
  LineID string pk
  JournalEntryID string fk
  AccountID string fk
  Debit decimal
  Credit decimal
}

// ================= SECURITY =================

role [icon: shield, color: black] {
  RoleID string pk
  Name string
}

permission [icon: key, color: black] {
  PermissionID string pk
  Name string
}

role_permission [icon: link, color: black] {
  RoleID string fk
  PermissionID string fk
}

user [icon: user, color: black] {
  UserID string pk
  RoleID string fk
  WarehouseID string fk
  Username string
  Email string
  PasswordHash string
}

// ================= SYSTEM =================

notification [icon: bell, color: white] {
  NotificationID string pk
  RecipientUserID string fk
  Title string
  Message string
  IsRead boolean
}
 
audit_log [icon: file-text, color: white] {
  LogID string pk
  ChangedBy string fk
  EntityType string
  EntityID string
  Action string
  ChangeDetails string
}


// ================= RELATIONSHIPS =================

// Procurement
supplier_bank_details.SupplierID > supplier.SupplierID
product_supplier.ProductID > product.ProductID
product_supplier.SupplierID > supplier.SupplierID
purchase_order.SupplierID > supplier.SupplierID
purchase_order.WarehouseID > warehouse.WarehouseID
purchase_order_item.POID > purchase_order.POID
purchase_order_item.ProductID > product.ProductID
goods_receipt.POID > purchase_order.POID
goods_receipt_item.GRNID > goods_receipt.GRNID
goods_receipt_item.ProductID > product.ProductID

// Inventory
category.ParentCategoryID > category.CategoryID
product.CategoryID > category.CategoryID
stock.ProductID > product.ProductID
stock.WarehouseID > warehouse.WarehouseID
stock.ZoneID > warehouse_zone.ZoneID
inventory_transaction.ProductID > product.ProductID
inventory_transaction.WarehouseID > warehouse.WarehouseID

// Sales
sales_order.CustomerID > customer.CustomerID
sales_order.WarehouseID > warehouse.WarehouseID
sales_order_item.OrderID > sales_order.OrderID
sales_order_item.ProductID > product.ProductID
invoice.OrderID > sales_order.OrderID

// Logistics
inbound_shipment.POID > purchase_order.POID
inbound_shipment.WarehouseID > warehouse.WarehouseID
outbound_shipment.OrderID > sales_order.OrderID
outbound_shipment.WarehouseID > warehouse.WarehouseID

// Returns
sales_return.OrderID > sales_order.OrderID
sales_return.CustomerID > customer.CustomerID
purchase_return.POID > purchase_order.POID
purchase_return.SupplierID > supplier.SupplierID

// Finance
exchange_rate.FromCurrency > currency.CurrencyID
exchange_rate.ToCurrency > currency.CurrencyID
bill.POID > purchase_order.POID
bill.SupplierID > supplier.SupplierID
payment.InvoiceID > invoice.InvoiceID
payment.BillID > bill.BillID
journal_entry_line.JournalEntryID > journal_entry.JournalEntryID
journal_entry_line.AccountID > chart_of_accounts.AccountID

// Security
role_permission.RoleID > role.RoleID
role_permission.PermissionID > permission.PermissionID
user.RoleID > role.RoleID
user.WarehouseID > warehouse.WarehouseID

// System
notification.RecipientUserID > user.UserID
audit_log.ChangedBy > user.UserID