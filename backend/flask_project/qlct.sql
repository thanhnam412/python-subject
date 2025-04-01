CREATE DATABASE QLCT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE QLCT;

-- Bảng người dùng
CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    reset_token VARCHAR(255),
    reset_token_expiry DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng danh mục chi tiêu
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INT,
    note TEXT,
    created_date DATE,
    UNIQUE (name, user_id),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng giao dịch
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    type ENUM('expense', 'income') NOT NULL,
    description TEXT,
    date DATE NOT NULL,
    created_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX (user_id),
    INDEX (category_id),
    INDEX (date)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng ngân sách
CREATE TABLE budgets (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    budget_limit DECIMAL(10,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng hóa đơn
CREATE TABLE bills (
    bill_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    bill_name VARCHAR(100) NOT NULL,
    due_date DATE NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    is_paid BOOLEAN NOT NULL DEFAULT FALSE,
    created_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng chi tiêu nhóm
CREATE TABLE shared_expenses (
    shared_expense_id INT AUTO_INCREMENT PRIMARY KEY,
    payer_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    participants VARCHAR(255) NOT NULL,
    date DATE NOT NULL,
    created_date DATE,
    FOREIGN KEY (payer_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng thông báo
CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng tài khoản ngân hàng
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    balance DECIMAL(10,2) NOT NULL,
    account_number VARCHAR(50),
    logo_url VARCHAR(255),
    created_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng mục tiêu tài chính
CREATE TABLE goals (
    goal_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    goal_amount DECIMAL(15,2) NOT NULL,
    current_amount DECIMAL(15,2) NOT NULL DEFAULT 0.00,
    goal_name VARCHAR(100) NOT NULL,
    target_date DATE NOT NULL,
    created_date DATE,
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bảng thống kê hàng tuần
CREATE TABLE weekly_stats (
    user_id INT,
    day DATE,
    total DECIMAL(10,2),
    PRIMARY KEY (user_id, day),
    FOREIGN KEY (user_id) REFERENCES user(user_id)
) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Dữ liệu mẫu
INSERT INTO user (username, password, email) VALUES ('testuser', 'pbkdf2:sha256:260000$...', 'test@example.com');

INSERT INTO categories (name, user_id, note, created_date) VALUES
    ('Nhà', 1, 'Chi phí nhà ở', '2023-05-01'),
    ('Đồ ăn', 1, 'Chi phí ăn uống', '2023-05-01'),
    ('Phương tiện', 1, 'Chi phí đi lại', '2023-05-01'),
    ('Giải trí', 1, 'Chi phí giải trí', '2023-05-01'),
    ('Mua sắm', 1, 'Chi phí mua sắm', '2023-05-01'),
    ('Khác', 1, 'Chi phí khác', '2023-05-01');

INSERT INTO transactions (user_id, category_id, amount, type, description, date, created_date) VALUES
    (1, 1, 50000.00, 'expense', 'Mua đồ ăn', '2025-03-24', '2025-03-24'),
    (1, 2, 100000.00, 'expense', 'Mua quần áo', '2025-03-24', '2025-03-24');

INSERT INTO budgets (user_id, category_id, budget_limit, start_date, end_date, created_date) VALUES
    (1, 1, 100000.00, '2023-05-01', '2023-05-31', '2023-05-01'),
    (1, 2, 50000.00, '2023-05-01', '2023-05-31', '2023-05-01');

INSERT INTO bills (user_id, bill_name, due_date, amount, is_paid, created_date) VALUES
    (1, 'FIGMA – MONTHLY', '2022-05-14', 150.00, FALSE, '2022-05-01'),
    (1, 'Adobe – Yearly', '2023-06-17', 559.00, FALSE, '2023-06-01');

INSERT INTO shared_expenses (payer_id, amount, description, participants, date, created_date) VALUES
    (1, 200.00, 'Group dinner', 'user1,user2,user3', '2023-05-01', '2023-05-01');

INSERT INTO notifications (user_id, message, created_at, is_read) VALUES
    (1, 'New bill FIGMA – MONTHLY due on 2022-05-14', '2022-05-01 12:00:00', FALSE),
    (1, 'New bill Adobe – Yearly due on 2023-06-17', '2023-06-01 12:00:00', FALSE);

INSERT INTO accounts (user_id, account_type, balance, account_number, logo_url, created_date) VALUES
    (1, 'Credit Card', 25000.00, '3388 4556 8860 8***', 'https://upload.wikimedia.org/wikipedia/commons/0/04/Mastercard-logo.png', '2023-05-01');

INSERT INTO goals (user_id, goal_amount, current_amount, goal_name, target_date, created_date) VALUES
    (1, 20000.00, 0.00, 'Save for vacation', '2023-12-31', '2023-05-01');

INSERT INTO weekly_stats (user_id, day, total) VALUES
    (1, '2023-05-17', 5000.00),
    (1, '2023-05-18', 2000.00);
