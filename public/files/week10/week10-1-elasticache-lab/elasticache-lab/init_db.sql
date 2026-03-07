-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS labdb;
USE labdb;

-- 사용자 테이블
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT,
    city VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 상품 테이블
CREATE TABLE IF NOT EXISTS products (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2),
    stock INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 샘플 사용자 데이터 삽입
INSERT INTO users (name, email, age, city) VALUES
('김철수', 'kim@example.com', 28, 'Seoul'),
('이영희', 'lee@example.com', 32, 'Busan'),
('박민수', 'park@example.com', 25, 'Incheon'),
('정수진', 'jung@example.com', 30, 'Daegu'),
('최지훈', 'choi@example.com', 27, 'Gwangju'),
('강미영', 'kang@example.com', 29, 'Daejeon'),
('윤서준', 'yoon@example.com', 31, 'Ulsan'),
('임하은', 'lim@example.com', 26, 'Suwon'),
('한동현', 'han@example.com', 33, 'Changwon'),
('오지원', 'oh@example.com', 24, 'Goyang');

-- 샘플 상품 데이터 삽입
INSERT INTO products (name, category, price, stock) VALUES
('노트북 15인치', 'Electronics', 1200000, 50),
('무선 마우스', 'Electronics', 35000, 200),
('기계식 키보드', 'Electronics', 150000, 100),
('모니터 27인치', 'Electronics', 350000, 75),
('USB-C 허브', 'Electronics', 45000, 150),
('책상 스탠드', 'Furniture', 80000, 120),
('사무용 의자', 'Furniture', 250000, 60),
('책장', 'Furniture', 180000, 40),
('스탠딩 책상', 'Furniture', 450000, 30),
('노트북 거치대', 'Accessories', 25000, 180);

-- 추가 대량 데이터 (성능 테스트용)
INSERT INTO products (name, category, price, stock)
SELECT 
    CONCAT('상품-', n),
    CASE (n % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Furniture'
        WHEN 2 THEN 'Accessories'
        WHEN 3 THEN 'Books'
        ELSE 'Others'
    END,
    FLOOR(10000 + RAND() * 990000),
    FLOOR(RAND() * 500)
FROM (
    SELECT @row := @row + 1 AS n
    FROM (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t1,
         (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t2,
         (SELECT 0 UNION SELECT 1 UNION SELECT 2 UNION SELECT 3 UNION SELECT 4 UNION SELECT 5 UNION SELECT 6 UNION SELECT 7 UNION SELECT 8 UNION SELECT 9) t3,
         (SELECT @row := 10) t4
    LIMIT 990
) numbers;

-- 인덱스 생성
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);

-- 테이블 확인
SELECT 'Users table:' AS info, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Products table:', COUNT(*) FROM products;
