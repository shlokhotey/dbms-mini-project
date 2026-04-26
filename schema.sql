-- ============================================
-- TABLE: Stores
-- ============================================
CREATE TABLE Stores (
    StoreID       SERIAL PRIMARY KEY,
    Location      VARCHAR(150) NOT NULL,
    ContactNumber VARCHAR(20)  NOT NULL,
    ManagerName   VARCHAR(100) NOT NULL
);

-- ============================================
-- TABLE: Products
-- ============================================
CREATE TABLE Products (
    ProductID  SERIAL PRIMARY KEY,
    Name       VARCHAR(100)   NOT NULL,
    Category   VARCHAR(60)    NOT NULL,
    UnitPrice  DECIMAL(10, 2) NOT NULL
);

-- ============================================
-- TABLE: Inventory
-- ============================================
CREATE TABLE Inventory (
    InventoryID   SERIAL PRIMARY KEY,
    StoreID       INTEGER NOT NULL,
    ProductID     INTEGER NOT NULL,
    StockQuantity INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT fk_store FOREIGN KEY (StoreID)
        REFERENCES Stores(StoreID) ON DELETE CASCADE,
    CONSTRAINT fk_product FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID) ON DELETE CASCADE,
    CONSTRAINT unique_store_product UNIQUE (StoreID, ProductID)
);

-- ============================================
-- TABLE: Sales
-- ============================================
CREATE TABLE Sales (
    SaleID       SERIAL PRIMARY KEY,
    StoreID      INTEGER        NOT NULL,
    ProductID    INTEGER        NOT NULL,
    SaleDate     TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    QuantitySold INTEGER        NOT NULL,
    TotalAmount  DECIMAL(10, 2) NOT NULL,
    CONSTRAINT fk_store_sales FOREIGN KEY (StoreID)
        REFERENCES Stores(StoreID) ON DELETE CASCADE,
    CONSTRAINT fk_product_sales FOREIGN KEY (ProductID)
        REFERENCES Products(ProductID) ON DELETE CASCADE
);

-- ============================================
-- SEED DATA (Same as yours, no changes needed)
-- ============================================

-- Stores
INSERT INTO Stores (Location, ContactNumber, ManagerName) VALUES
('Mumbai - Andheri West',   '022-26321001', 'Rajesh Sharma'),
('Delhi - Connaught Place', '011-23456789', 'Priya Mehta'),
('Bangalore - Koramangala', '080-41234567', 'Amit Patel'),
('Chennai - T. Nagar',      '044-28152030', 'Sneha Reddy'),
('Pune - FC Road',          '020-25678901', 'Vikram Singh');

-- Products
INSERT INTO Products (Name, Category, UnitPrice) VALUES
('Basmati Rice 5kg',       'Groceries',    450.00),
('Toor Dal 1kg',           'Groceries',    160.00),
('Amul Butter 500g',       'Dairy',        270.00),
('Parle-G Biscuits 800g',  'Snacks',        85.00),
('Surf Excel 2kg',         'Household',    380.00),
('Colgate MaxFresh 150g',  'Personal Care', 95.00),
('Maggi Noodles 12-pack',  'Snacks',       168.00),
('Tata Tea Gold 500g',     'Beverages',    265.00),
('Dettol Handwash 750ml',  'Personal Care',185.00),
('Vim Liquid 750ml',       'Household',    139.00);

-- Inventory (same as yours)
INSERT INTO Inventory (StoreID, ProductID, StockQuantity) VALUES
(1, 1, 120), (1, 2, 90),  (1, 3, 60),  (1, 4, 200),
(1, 5, 75),  (1, 6, 110), (1, 7, 150), (1, 8, 85),
(1, 9, 95),  (1, 10, 70),
(2, 1, 100), (2, 2, 80),  (2, 3, 50),  (2, 4, 180),
(2, 5, 65),  (2, 6, 100), (2, 7, 130), (2, 8, 90),
(2, 9, 80),  (2, 10, 60),
(3, 1, 90),  (3, 2, 70),  (3, 3, 45),  (3, 4, 160),
(3, 5, 55),  (3, 6, 85),  (3, 7, 120), (3, 8, 75),
(3, 9, 70),  (3, 10, 50),
(4, 1, 110), (4, 2, 85),  (4, 3, 55),  (4, 4, 190),
(4, 5, 70),  (4, 6, 95),  (4, 7, 140), (4, 8, 80),
(4, 9, 88),  (4, 10, 65),
(5, 1, 80),  (5, 2, 60),  (5, 3, 40),  (5, 4, 150),
(5, 5, 50),  (5, 6, 75),  (5, 7, 100), (5, 8, 65),
(5, 9, 60),  (5, 10, 45);

-- Sales
INSERT INTO Sales (StoreID, ProductID, SaleDate, QuantitySold, TotalAmount) VALUES
(1, 1, '2026-04-01 10:30:00', 5, 2250.00),
(1, 4, '2026-04-01 11:15:00', 10, 850.00),
(2, 3, '2026-04-01 14:00:00', 3, 810.00),
(3, 7, '2026-04-02 09:45:00', 8, 1344.00),
(4, 5, '2026-04-02 16:20:00', 4, 1520.00),
(5, 2, '2026-04-03 12:10:00', 6, 960.00),
(1, 6, '2026-04-03 13:30:00', 7, 665.00),
(2, 8, '2026-04-03 15:45:00', 5, 1325.00),
(3, 9, '2026-04-04 10:20:00', 4, 280.00),
(4, 10, '2026-04-04 11:50:00', 3, 417.00);