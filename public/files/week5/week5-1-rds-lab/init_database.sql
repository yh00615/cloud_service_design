-- 데이터베이스 선택
USE labdb;

-- 고객 테이블 생성
CREATE TABLE customers (
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 상품 테이블 생성
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(200) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 주문 테이블 생성
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- 샘플 고객 데이터 삽입
INSERT INTO customers (name, email, phone) VALUES
('김철수', 'kim@example.com', '010-1234-5678'),
('이영희', 'lee@example.com', '010-2345-6789'),
('박민수', 'park@example.com', '010-3456-7890');

-- 샘플 상품 데이터 삽입
INSERT INTO products (name, price, stock, category) VALUES
('노트북', 1200000, 10, 'Electronics'),
('마우스', 35000, 50, 'Electronics'),
('키보드', 89000, 30, 'Electronics'),
('모니터', 350000, 15, 'Electronics'),
('책상', 250000, 5, 'Furniture');

-- 샘플 주문 데이터 삽입
INSERT INTO orders (customer_id, total_amount, status) VALUES
(1, 1200000, 'DELIVERED'),
(2, 124000, 'SHIPPED'),
(1, 350000, 'PROCESSING'),
(3, 250000, 'PENDING');

-- 데이터 확인
SELECT * FROM customers;
SELECT * FROM products;
SELECT * FROM orders;

-- 고객별 주문 조회
SELECT 
    c.name,
    o.order_id,
    o.order_date,
    o.total_amount,
    o.status
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
ORDER BY c.customer_id, o.order_date DESC;
