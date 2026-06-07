-- 家庭记账数据库初始化脚本
-- 创建数据库
CREATE DATABASE IF NOT EXISTS family_account 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE family_account;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    avatar VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(100),
    family_id BIGINT,
    role ENUM('owner', 'admin', 'member') DEFAULT 'member',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_family (family_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 家庭表
CREATE TABLE IF NOT EXISTS families (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    owner_id BIGINT NOT NULL,
    invite_code VARCHAR(20) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 账户表
CREATE TABLE IF NOT EXISTS accounts (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    name VARCHAR(50) NOT NULL,
    type ENUM('cash', 'bank', 'alipay', 'wechat', 'credit_card', 'investment') NOT NULL,
    balance DECIMAL(12,2) DEFAULT 0,
    icon VARCHAR(50),
    color VARCHAR(20),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 分类表
CREATE TABLE IF NOT EXISTS categories (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT,
    name VARCHAR(50) NOT NULL,
    type ENUM('income', 'expense', 'investment') NOT NULL,
    parent_id BIGINT,
    icon VARCHAR(50),
    color VARCHAR(20),
    sort_order INT DEFAULT 0,
    is_fixed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id),
    INDEX idx_type (type),
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 记账记录表
CREATE TABLE IF NOT EXISTS records (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    family_id BIGINT,
    account_id BIGINT NOT NULL,
    category_id BIGINT NOT NULL,
    type ENUM('income', 'expense', 'investment') NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    record_date DATE NOT NULL,
    remark VARCHAR(255),
    is_fixed BOOLEAN DEFAULT FALSE,
    fixed_cycle ENUM('daily', 'weekly', 'monthly', 'yearly'),
    reimbursement_status ENUM('none', 'pending', 'done') DEFAULT 'none',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_user_date (user_id, record_date),
    INDEX idx_family_date (family_id, record_date),
    INDEX idx_type_date (type, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 预算表
CREATE TABLE IF NOT EXISTS budgets (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    family_id BIGINT,
    category_id BIGINT,
    amount DECIMAL(12,2) NOT NULL,
    month INT NOT NULL,
    spent DECIMAL(12,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id),
    INDEX idx_user_month (user_id, month)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 投资记录表
CREATE TABLE IF NOT EXISTS investments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    account_id BIGINT NOT NULL,
    type ENUM('stock', 'fund', 'bond', 'deposit', 'other') NOT NULL,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20),
    buy_price DECIMAL(12,4),
    current_price DECIMAL(12,4),
    quantity DECIMAL(12,4),
    amount DECIMAL(12,2) NOT NULL,
    profit DECIMAL(12,2) DEFAULT 0,
    buy_date VARCHAR(10) NOT NULL,
    sell_date VARCHAR(10),
    status VARCHAR(20) DEFAULT 'holding',
    remark VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_type (user_id, type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 保险表
CREATE TABLE IF NOT EXISTS insurances (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    family_id BIGINT,
    name VARCHAR(100) NOT NULL,
    type ENUM('life', 'health', 'accident', 'car', 'property', 'other') NOT NULL,
    sub_type VARCHAR(50),
    company VARCHAR(100),
    policy_no VARCHAR(50),
    insured_amount DECIMAL(12,2),
    premium DECIMAL(12,2) NOT NULL,
    payment_cycle VARCHAR(20) DEFAULT 'yearly',
    start_date VARCHAR(10) NOT NULL,
    end_date VARCHAR(10) NOT NULL,
    beneficiary VARCHAR(50),
    reminder_days INT DEFAULT 3,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (family_id) REFERENCES families(id),
    INDEX idx_user (user_id),
    INDEX idx_end_date (end_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 插入预设分类（支出）
INSERT INTO categories (name, type, icon, sort_order) VALUES
('日常支出', 'expense', '🍚', 1),
('交通费', 'expense', '🚗', 2),
('孩子教育', 'expense', '📚', 3),
('保险支出', 'expense', '🛡️', 4),
('投资理财', 'expense', '📊', 5),
('差旅报销', 'expense', '✈️', 6);

-- 插入预设分类（收入）
INSERT INTO categories (name, type, icon, sort_order) VALUES
('工资收入', 'income', '💰', 1),
('额外收入', 'income', '💵', 2),
('公司福利', 'income', '🎁', 3);

-- 插入预设分类（投资）
INSERT INTO categories (name, type, icon, sort_order) VALUES
('股票', 'investment', '📈', 1),
('基金', 'investment', '📉', 2),
('理财', 'investment', '🏦', 3);
