#!/bin/bash

set -e

DB_NAME="car_data"
TABLE_NAME="car_registration_long"
STAGING_TABLE="staging_car_registration_long"
DATA_DIR="/home/ec2-user/data/car_resistration"
CSV_PATTERN="car_registration_long_*.csv"

found_csv=0

while IFS= read -r -d '' CSV_PATH; do
  found_csv=1

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
    stat_month,
    region_level,
    sido_name,
    sigungu_name,
    vehicle_type,
    use_type,
    registration_count,
    unit,
    source_measure_key,
    source_form_id,
    source_row_no,
    is_aggregate
)
SELECT
    stat_month,
    region_level,
    sido_name,
    sigungu_name,
    vehicle_type,
    use_type,
    registration_count,
    unit,
    source_measure_key,
    source_form_id,
    source_row_no,
    is_aggregate
FROM $STAGING_TABLE AS new
ON DUPLICATE KEY UPDATE
    vehicle_type = new.vehicle_type,
    use_type = new.use_type,
    registration_count = new.registration_count,
    unit = new.unit,
    source_row_no = new.source_row_no,
    is_aggregate = new.is_aggregate;

SELECT COUNT(*) AS total_rows
FROM $TABLE_NAME;

SQL

  rm -- "$CSV_PATH"
  echo "적재 완료 및 CSV 삭제: $CSV_PATH"
done < <(
  find "$DATA_DIR" \
    -maxdepth 1 \
    -type f \
    -name "$CSV_PATTERN" \
    -print0
)

if [ "$found_csv" -eq 0 ]; then
  echo "대상 CSV 파일이 없습니다: $DATA_DIR/$CSV_PATTERN"
  exit 1
fi

echo "모든 CSV 적재 완료"
