#!/bin/bash

set -e

DB_NAME="car_data"
TABLE_NAME="used_cars"
STAGING_TABLE="staging_used_cars"
CSV_PATH="/home/ec2-user/data/used_cars/used_car_flattened.csv"

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
    id,
    listingNumber,
    title,
    description,
    brand_id,
    brand_name,
    brand_slug,
    brand_country,
    model_id,
    model_name,
    model_slug,
    model_bodyType,
    trim,
    modelYear,
    firstRegistration,
    mileageKm,
    fuelType,
    transmission,
    price,
    currency,
    color,
    displacementCc,
    accidentCount,
    ownerChangeCount,
    inspectionStatus,
    status,
    location_id,
    location_province,
    location_city,
    location_slug,
    dealer_code,
    dealer_displayName,
    dealer_department,
    dealer_position,
    businessArea_id,
    businessArea_name,
    businessArea_parent_id,
    businessArea_parent_name,
    createdAt,
    updatedAt
)
SELECT
    id,
    listingNumber,
    title,
    description,
    brand_id,
    brand_name,
    brand_slug,
    brand_country,
    model_id,
    model_name,
    model_slug,
    model_bodyType,
    trim,
    modelYear,
    firstRegistration,
    mileageKm,
    fuelType,
    transmission,
    price,
    currency,
    color,
    displacementCc,
    accidentCount,
    ownerChangeCount,
    inspectionStatus,
    status,
    location_id,
    location_province,
    location_city,
    location_slug,
    dealer_code,
    dealer_displayName,
    dealer_department,
    dealer_position,
    businessArea_id,
    businessArea_name,
    businessArea_parent_id,
    businessArea_parent_name,
    createdAt,
    updatedAt
FROM $STAGING_TABLE AS new
ON DUPLICATE KEY UPDATE
    id = new.id,
    title = new.title,
    description = new.description,
    brand_id = new.brand_id,
    brand_name = new.brand_name,
    brand_slug = new.brand_slug,
    brand_country = new.brand_country,
    model_id = new.model_id,
    model_name = new.model_name,
    model_slug = new.model_slug,
    model_bodyType = new.model_bodyType,
    trim = new.trim,
    modelYear = new.modelYear,
    firstRegistration = new.firstRegistration,
    mileageKm = new.mileageKm,
    fuelType = new.fuelType,
    transmission = new.transmission,
    price = new.price,
    currency = new.currency,
    color = new.color,
    displacementCc = new.displacementCc,
    accidentCount = new.accidentCount,
    ownerChangeCount = new.ownerChangeCount,
    inspectionStatus = new.inspectionStatus,
    status = new.status,
    location_id = new.location_id,
    location_province = new.location_province,
    location_city = new.location_city,
    location_slug = new.location_slug,
    dealer_code = new.dealer_code,
    dealer_displayName = new.dealer_displayName,
    dealer_department = new.dealer_department,
    dealer_position = new.dealer_position,
    businessArea_id = new.businessArea_id,
    businessArea_name = new.businessArea_name,
    businessArea_parent_id = new.businessArea_parent_id,
    businessArea_parent_name = new.businessArea_parent_name,
    createdAt = new.createdAt,
    updatedAt = new.updatedAt;

SELECT COUNT(*) AS total_rows
FROM $TABLE_NAME;

SQL

rm -- "$CSV_PATH"

echo "적재 완료 및 CSV 삭제: $CSV_PATH"
