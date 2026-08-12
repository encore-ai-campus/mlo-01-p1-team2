#!/bin/bash

set -e

DB_NAME="projectTest"
TABLE_NAME="cars"
CSV_PATH="/home/playdata/test/cars.csv"

if [ ! -f "$CSV_PATH" ]; then
  echo "CSV 파일이 없습니다: $CSV_PATH"
  exit 1
fi

echo "CSV 적재 시작: $CSV_PATH"

mysql \
  --local-infile=1 \
  -u projectTest \
  -p \
  projectTest <<SQL

LOAD DATA LOCAL INFILE '$CSV_PATH'
INTO TABLE $TABLE_NAME
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

SELECT COUNT(*) AS total_rows
FROM $TABLE_NAME;

SQL

echo "적재 완료"
