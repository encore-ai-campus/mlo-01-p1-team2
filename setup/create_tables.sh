#!/bin/bash

set -e

DB_NAME="projectTest"

echo "테이블 생성 시작"

mysql "$DB_NAME" <<SQL

CREATE TABLE IF NOT EXISTS cars (
    listing_number VARCHAR(50) NOT NULL UNIQUE PRIMARY KEY,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    brand_id INT,
    brand_name VARCHAR(100),
    brand_country VARCHAR(50),

    model_id INT,
    model_name VARCHAR(100),
    body_type VARCHAR(50),

    trim VARCHAR(100),
    model_year INT,
    first_registration DATE,
    mileage_km INT,

    fuel_type VARCHAR(50),
    transmission VARCHAR(50),

    price BIGINT,
    currency VARCHAR(10),
    color VARCHAR(50),

    displacement_cc INT,
    accident_count INT,
    owner_change_count INT,

    inspection_status VARCHAR(50),
    status VARCHAR(50),

    location_id INT,
    province VARCHAR(50),
    city VARCHAR(50),

    dealer_code VARCHAR(100),
    dealer_department VARCHAR(100),
    dealer_position VARCHAR(100),

    business_area_id VARCHAR(50),
    business_area_name VARCHAR(100),

    business_area_parent_id VARCHAR(50),
    business_area_parent_name VARCHAR(100),

    created_at DATETIME,
    updated_at DATETIME
);

CREATE TABLE IF NOT EXISTS staging_cars (
    listing_number VARCHAR(50) NOT NULL UNIQUE PRIMARY KEY,

    title VARCHAR(255) NOT NULL,
    description TEXT,

    brand_id INT,
    brand_name VARCHAR(100),
    brand_country VARCHAR(50),

    model_id INT,
    model_name VARCHAR(100),
    body_type VARCHAR(50),

    trim VARCHAR(100),
    model_year INT,
    first_registration DATE,
    mileage_km INT,

    fuel_type VARCHAR(50),
    transmission VARCHAR(50),

    price BIGINT,
    currency VARCHAR(10),
    color VARCHAR(50),

    displacement_cc INT,
    accident_count INT,
    owner_change_count INT,

    inspection_status VARCHAR(50),
    status VARCHAR(50),

    location_id INT,
    province VARCHAR(50),
    city VARCHAR(50),

    dealer_code VARCHAR(100),
    dealer_department VARCHAR(100),
    dealer_position VARCHAR(100),

    business_area_id VARCHAR(50),
    business_area_name VARCHAR(100),

    business_area_parent_id VARCHAR(50),
    business_area_parent_name VARCHAR(100),

    created_at DATETIME,
    updated_at DATETIME
);

SHOW TABLES;

SQL

echo "테이블 생성 완료"
