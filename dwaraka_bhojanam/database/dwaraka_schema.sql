USE [DwarakaBhojanam]
GO
-- Create MenuItems table (if not already created)
CREATE TABLE MenuItems (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    description NVARCHAR(255),
    price DECIMAL(10,2),
    image NVARCHAR(255)
);

-- Create Users table
CREATE TABLE Users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100),
    email NVARCHAR(100) UNIQUE,
    password NVARCHAR(100)
);

-- Create Cart table
CREATE TABLE Cart (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_email NVARCHAR(100),
    item_id INT,
    quantity INT,
    FOREIGN KEY (item_id) REFERENCES MenuItems(id)
);

-- Create Orders table
CREATE TABLE Orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    user_email NVARCHAR(100),
    order_time DATETIME DEFAULT GETDATE(),
    total DECIMAL(10,2)
);

-- Create OrderItems table
CREATE TABLE OrderItems (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT,
    item_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES Orders(id),
    FOREIGN KEY (item_id) REFERENCES MenuItems(id)
);
