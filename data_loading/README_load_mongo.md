# load_mongo.sh

원본 JSON의 `records` 배열만 MongoDB에 적재하고, `source_id`를 기준으로 upsert합니다.

## 준비사항

- `jq` 설치
- MongoDB Database Tools의 `mongoimport` 설치
- MongoDB 접속 정보
- 원본 파일이 다음 구조의 유효한 JSON이어야 합니다.

```json
{
  "collected_at": "...",
  "source_url": "...",
  "records": [
    { "source_id": "...", "question": "...", "answer": "..." }
  ]
}
```

## 사용 방법

인증정보는 스크립트에 직접 넣지 말고 환경변수로 전달합니다.

```bash
export MONGO_URI='mongodb://127.0.0.1:27017/faq_db'
export MONGO_COLLECTION='faqs'

chmod +x load_mongo.sh
./load_mongo.sh faq_all.txt faq_records.json
```

인자를 생략하면 `faq_all.txt`를 읽고 `faq_records.json`을 생성합니다.

## 동작

먼저 원본 전체가 아니라 `records` 배열만 별도 파일로 추출합니다.

```bash
jq '.records' "$FILE_PATH" > "$IMPORT_PATH"
```

추출 결과는 최상위 배열이므로 `--jsonArray`를 사용합니다. `source_id`가 같으면 기존 문서를 갱신하고, 없으면 새 문서를 추가합니다.

```bash
mongoimport \
  --uri "$MONGO_URI" \
  --collection "$MONGO_COLLECTION" \
  --jsonArray \
  --mode upsert \
  --upsertFields source_id \
  --file "$IMPORT_PATH"
```

`source_id` 중복 방지를 위해 unique index를 권장합니다.

```javascript
db.faqs.createIndex({ source_id: 1 }, { unique: true })
```

## 예시 `load_mongo.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

FILE_PATH="${1:-faq_all.txt}"
IMPORT_PATH="${2:-faq_records.json}"
MONGO_URI="${MONGO_URI:?MONGO_URI 환경변수를 설정하세요.}"
MONGO_COLLECTION="${MONGO_COLLECTION:-faqs}"

command -v jq >/dev/null || { echo "jq가 필요합니다." >&2; exit 1; }
command -v mongoimport >/dev/null || { echo "mongoimport가 필요합니다." >&2; exit 1; }

if [[ ! -f "$FILE_PATH" ]]; then
  echo "원본 파일을 찾을 수 없습니다: $FILE_PATH" >&2
  exit 1
fi

jq '.records' "$FILE_PATH" > "$IMPORT_PATH"

mongoimport \
  --uri "$MONGO_URI" \
  --collection "$MONGO_COLLECTION" \
  --jsonArray \
  --mode upsert \
  --upsertFields source_id \
  --file "$IMPORT_PATH"
```

문제 발생 시 `jq`, `mongoimport` 설치 여부와 `MONGO_URI`, 원본 파일 경로를 확인하세요. 최상위 `collected_at`, `source_url`은 이 스크립트에서 별도로 저장하지 않습니다.
