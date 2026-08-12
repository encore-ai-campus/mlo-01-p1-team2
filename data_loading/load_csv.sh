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
    price,
    mileage_km,
    status
)
SELECT
    listing_number,
    title,
    price,
    mileage_km,
    status
FROM $STAGING_TABLE
AS new
ON DUPLICATE KEY UPDATE
    listing_number = new.listing_number,
    title = new.title,
    price = new.price,
    mileage_km = new.mileage_km,
    status = new.status;

SELECT COUNT(*) AS total_rows
FROM $TABLE_NAME;

SQL

echo "적재 완료"
