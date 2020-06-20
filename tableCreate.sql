-- DROP TABLE IF EXISTS user_master;
-- CREATE TABLE user_master (
--     user_id INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
--     email VARCHAR(30) UNIQUE,
--     user_name VARCHAR(50) NOT NULL,
--     mobile VARCHAR(15),
--     date_created DEFAULT CURRENT_DATE,
--     time_created DEFAULT CURRENT_TIME,
--     password VARCHAR(255)
-- );

-- DROP TABLE IF EXISTS product_master;
-- CREATE TABLE product_master (
--     product_code INTEGER UNIQUE PRIMARY KEY AUTOINCREMENT,
--     product_description VARCHAR(40) NOT NULL,
--     price REAL,
--     stock INTEGER,
--     image BLOB
-- );

DROP TABLE IF EXISTS order_header;
CREATE TABLE order_header (
    order_no INTEGER PRIMARY KEY AUTOINCREMENT,
    order_date DATE,
    addr_1 VARCHAR(40),
    addr_2 VARCHAR(40),
    user_id INTEGER,
    date_created DEFAULT CURRENT_DATE,
    time_created DEFAULT CURRENT_TIME,
    FOREIGN KEY (user_id)
        REFERENCES user_master (user_id)
);

DROP TABLE IF EXISTS order_detail;
CREATE TABLE order_detail (
    order_no INTEGER,
    product_code VARCHAR(30),
    product_description VARCHAR(40) NOT NULL,
    price REAL,
    order_qty INT,
    user_id INTEGER,
    date_created DEFAULT CURRENT_DATE,
    time_created DEFAULT CURRENT_TIME,
    PRIMARY KEY (order_no, product_code, time_created),
    FOREIGN KEY (order_no) REFERENCES order_header (order_no),
    FOREIGN KEY (product_code) REFERENCES product_master (product_code)
);

DROP TABLE IF EXISTS basket;
CREATE TABLE basket (
    order_no INTEGER,
    product_code VARCHAR(30),
    product_description VARCHAR(40) NOT NULL,
    price REAL,
    order_qty INT,
    user_id INTEGER,
    date_created DEFAULT CURRENT_DATE,
    time_created DEFAULT CURRENT_TIME,
    PRIMARY KEY (product_code, time_created),
    FOREIGN KEY (product_code) REFERENCES product_master (product_code)
);