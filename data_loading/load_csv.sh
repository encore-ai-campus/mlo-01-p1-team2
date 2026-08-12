#!/bin/bash

set -e

DB_NAME="projectTest"
TABLE_NAME="cars"
STAGING_TABLE="cars_staging"
CSV_PATH="/home/playdata/test/cars.csv"

if [ ! -f "$CSV_PATH" ]; then
  echo "CSV 파일이 없습니다: $CSV_PATH"
  exit 1
fi

echo "CSV 적재 시작: $CSV_PATH"

mysql "$DB_NAME" <<SQL

CREATE TABLE IF NOT EXISTS $STAGING_TABLE (
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

CREATE TABLE IF NOT EXISTS $TABLE_NAME (
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


TRUNCATE TABLE $STAGING_TABLE;

LOAD DATA LOCAL INFILE '$CSV_PATH'
INTO TABLE $STAGING_TABLE
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

INSERT INTO $TABLE_NAME (
    listing_number,
    title,
    description,
    brand_id,
    brand_name,
    brand_country,
    model_id,
    model_name,
    body_type,
    trim,
    model_year,
    first_registration,
    mileage_km,
    fuel_type,
    transmission,
    price,
    currency,
    color,
    displacement_cc,
    accident_count,
    owner_change_count,
    inspection_status,
    status,
    location_id,
    province,
    city,
    dealer_code,
    dealer_department,
    dealer_position,
    business_area_id,
    business_area_name,
    business_area_parent_id,
    business_area_parent_name,
    created_at,
    updated_at
)
SELECT
    listing_number,
    title,
    description,
    brand_id,
    brand_name,
    brand_country,
    model_id,
    model_name,
    body_type,
    trim,
    model_year,
    first_registration,
    mileage_km,
    fuel_type,
    transmission,
    price,
    currency,
    color,
    displacement_cc,
    accident_count,
    owner_change_count,
    inspection_status,
    status,
    location_id,
    province,
    city,
    dealer_code,
    dealer_department,
    dealer_position,
    business_area_id,
    business_area_name,
    business_area_parent_id,
    business_area_parent_name,
    created_at,
    updated_at
FROM $STAGING_TABLE
AS new
ON DUPLICATE KEY UPDATE
    listing_number = new.listing_number,
    title = new.title,
    description = new.description,
    brand_id = new.brand_id,
    brand_name = new.brand_name,
    brand_country = new.brand_country,
    model_id = new.model_id,
    model_name = new.model_id,
    body_type = new.body_type,
    trim = new.trim,
    model_year = new.model_year,
    first_registration = new.first_registration,
    mileage_km = new.mileage_km,
    fuel_type = new.fuel_type,
    transmission = new.transmission,
    price = new.price,
    currency = new.currency,
    color = new.color,
    displacement_cc = new.displacement_cc,
    accident_count = new.accident_count,
    owner_change_count = new.owner_change_count,
    inspection_status = new.inspection_status,
    status = new.status,
    location_id = new.location_id,
    province = new.province,
    city = new.city,
    dealer_code = new.dealer_code,
    dealer_department = new.dealer_department,
    dealer_position = new.dealer_position,
    business_area_id = new.business_area_id,
    business_area_name = new.business_area_name,
    business_area_parent_id = new.business_area_parent_id,
    business_area_parent_name = new.business_area_parent_name,
    created_at = new.created_at,
    updated_at = new.updated_at;

SELECT COUNT(*) AS total_rows
FROM $TABLE_NAME;

SQL

echo "적재 완료"
