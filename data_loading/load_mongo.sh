#!/bin/bash

set -e

DB_NAME="projectTest"
COLLECTION_NAME="faq"
FILE_PATH="/home/ec2-user/1st_project/crawling/car_faq/data/categorized_faqs.json"
IMPORT_PATH=/home/ec2-user/1st_project/crawling/car_faq/data/filtered_faqs.json

if [ -z "$FILE_PATH" ]; then
    echo "사용법: $0 <json_file>"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "파일이 존재하지 않습니다: $FILE_PATH"
    exit 1
fi


echo "JSON 변환 시작"
# jq '.faq_detail' "$FILE_PATH" > "$IMPORT_PATH"
jq '
  [
    to_entries[]
    | .key as $brand
    | .value["FAQ detail"][]
    | {
        source_id: .source_id,
        brand: $brand,
        question: .["-Q"],
        answer: .["-A"],
        source: .["-출처"]
      }
  ]
' "$FILE_PATH" > "$IMPORT_PATH"

echo "MongoDB 적재 시작"
echo "DB         : $DB_NAME"
echo "Collection : $COLLECTION_NAME"
echo "File       : $IMPORT_PATH"

mongoimport \
  --host localhost \
  --port 27017 \
  --db "$DB_NAME" \
  --collection "$COLLECTION_NAME" \
  --file "$IMPORT_PATH" \
  --jsonArray \
  --mode upsert \
  --upsertFields source_id

echo "MongoDB 적재 완료"