-- Xóa cơ sở dữ liệu nếu tồn tại
DROP DATABASE IF EXISTS QLCT;

-- Tạo cơ sở dữ liệu mới
CREATE DATABASE QLCT;
USE QLCT;

-- Đặt bộ mã hóa cho cơ sở dữ liệu
ALTER DATABASE QLCT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng user 
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng categories
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE, -- Đổi category_name thành name để khớp với models.py
    user_id INT,
    note TEXT, -- Thêm cột note
    created_date DATE, -- Thêm cột created_date
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng transactions
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    type ENUM('expense', 'income') NOT NULL, -- Đổi transaction_type thành type để khớp với models.py
    description TEXT,
    date DATE NOT NULL, -- Đổi transaction_date thành date để khớp với models.py
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_user_id (user_id),
    INDEX idx_category_id (category_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng budgets (thêm từ models.py)
CREATE TABLE budgets (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_limit DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng bills
CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bill_name VARCHAR(100) NOT NULL,
    due_date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL, 
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng shared_expenses 
CREATE TABLE shared_expenses (
    shared_expense_id INT AUTO_INCREMENT PRIMARY KEY,
    payer_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    participants VARCHAR(255) NOT NULL,
    FOREIGN KEY (payer_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng notifications 
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng accounts
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(10, 2) NOT NULL,
    account_number VARCHAR(50),
    logo_url VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng goals
CREATE TABLE goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    goal_amount DECIMAL(15, 2) NOT NULL,
    current_amount DECIMAL(15, 2) NOT NULL DEFAULT 0.00,
    goal_name VARCHAR(100) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Tạo bảng weekly_stats
CREATE TABLE weekly_stats (
    user_id INT,
    day DATE,
    total DECIMAL(10, 2),
    PRIMARY KEY (user_id, day), 
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
