# 중고차 데이터 수집 및 변환 프로그램

중고차 정보를 제공하는 API 서버에 요청을 보내 차량 데이터를 수집하고, 수집 결과를 JSON 파일과 분석용 CSV 파일로 저장하는 프로그램입니다.

프로그램을 처음 실행하면 아직 완료되지 않은 전체 수집을 이어서 진행합니다. 전체 수집이 완료된 뒤 다시 실행하면 마지막으로 수집한 ID 이후의 데이터를 최대 500건까지 증분 수집합니다.

현재 프로그램은 API에서 데이터를 받아 JSON과 CSV 파일로 저장하는 단계까지 구현되어 있습니다. MySQL 또는 RDS와 같은 데이터베이스에 직접 적재하는 기능은 포함되어 있지 않으며, 생성된 CSV 파일을 이용해 별도 적재 작업을 진행해야 합니다.

## 1. 주요 기능

- API 서버의 공개 키 엔드포인트에서 API 키를 자동으로 발급받습니다.
- 발급받은 API 키를 `X-API-Key` 요청 헤더에 넣어 차량 데이터를 요청합니다.
- 커서 기반 API에 `after_id`와 `limit`을 전달해 페이지 단위로 데이터를 수집합니다.
- 최초 실행 시 전체 데이터를 수집하고, 중단되면 마지막 저장 위치부터 이어서 수집합니다.
- 전체 수집 완료 후에는 새로운 데이터만 최대 500건까지 증분 수집합니다.
- `listingNumber`를 기준으로 중복 데이터를 확인합니다.
- API 응답 값에 포함된 HTML 태그를 제거한 뒤 JSON에 저장합니다.
- API 키가 만료되면 새 키를 발급받아 같은 요청을 다시 시도합니다.
- 호출 제한이 발생하면 일정 시간 기다린 뒤 재요청합니다.
- 서버 오류나 네트워크 오류가 발생하면 현재 위치를 유지한 채 5분 후 재시도합니다.
- 페이지마다 `crawl_state.json`에 마지막 수집 위치를 저장합니다.
- 수집이 끝나거나 새로운 데이터가 저장되면 JSON 전체를 다시 읽어 CSV를 생성합니다.
- CSV 변환 과정에서 중첩 JSON을 평탄화합니다.
- `createdAt`, `updatedAt` 값을 한국 시간의 DB `DATETIME` 형식으로 변환합니다.
- CSV 파일에서는 최상위 `id` 컬럼을 제거합니다.
- 원본 JSON의 `id` 값은 그대로 유지됩니다.

## 2. 폴더 구조

모든 Python 모듈은 `used_car_clawling.py`와 같은 폴더에 두어야 합니다.

```text
used_car/
├── used_car_clawling.py   # 프로그램 실행 파일
├── used_car_api.py        # API 키 발급 및 차량 API 요청
├── used_car_config.py     # 서버 주소와 공통 설정
├── used_car_crawler.py    # 전체 수집·증분 수집 흐름
├── used_car_state.py      # 수집 상태 읽기·저장
├── used_car_storage.py    # 데이터 정리·중복 확인·JSON 저장
├── json_to_csv.py         # JSON 평탄화 및 CSV 변환
└── data/
    ├── used_car.json
    ├── crawl_state.json
    └── used_car_flattened.csv
```

각 파일의 역할은 다음과 같습니다.

- `used_car.json`: API에서 수집한 원본 데이터입니다.
- `crawl_state.json`: 마지막 수집 위치와 전체 수집 완료 여부를 저장합니다.
- `used_car_flattened.csv`: JSON을 평탄화한 분석용 CSV 파일입니다.

`data` 폴더는 `used_car_config.py`가 실행될 때 없으면 자동으로 생성됩니다.

## 3. 모듈별 역할

### `used_car_clawling.py`

프로그램을 시작하는 실행 파일입니다.

이 파일을 직접 실행했을 때만 `used_car_crawler.py`의 `main()` 함수를 호출합니다.

```bash
python used_car_clawling.py
```

파일명은 기존 프로젝트에서 사용하던 `clawling` 표기를 유지하고 있습니다.

### `used_car_config.py`

여러 모듈에서 공통으로 사용하는 설정을 관리합니다.

| 설정 | 현재 값 | 설명 |
|---|---:|---|
| `BASE_URL` | `http://43.203.233.157` | API 서버 기본 주소 |
| `PAGE_LIMIT` | `500` | API 한 번의 요청에 포함할 최대 데이터 수 |
| `INCREMENTAL_MAX_ITEMS` | `500` | 증분 수집 최대 데이터 수 |
| `SERVER_RETRY_SECONDS` | `300` | 서버·네트워크 오류 후 재시도 대기 시간 |
| `API_LISTING_NUMBER_FIELD` | `listingNumber` | 차량 중복 확인에 사용하는 필드 |

API 서버 주소나 수집 건수를 변경하려면 이 파일의 설정값을 수정하시면 됩니다.

### `used_car_api.py`

API 서버와 통신하는 모듈입니다.

#### `get_api_headers()`

- `/api/v1/public-key`에 요청합니다.
- 응답에서 현재 API 키를 가져옵니다.
- `X-API-Key`가 포함된 요청 헤더를 반환합니다.
- API 키 발급 요청이 실패하면 5분 후 다시 요청합니다.

#### `request_page(after_id)`

- `/api/v1/cars/cursor`에 차량 데이터를 요청합니다.
- `after_id`와 `limit`을 요청 파라미터로 전달합니다.
- `429` 응답이면 `Retry-After` 값을 기준으로 기다린 뒤 재요청합니다.
- `Retry-After` 값이 없으면 10초 후 재요청합니다.
- `403` 응답이면 API 키를 새로 발급받아 같은 요청을 다시 시도합니다.
- 서버 오류나 네트워크 오류가 발생하면 현재 위치에서 5분 후 재시도합니다.

### `used_car_state.py`

수집 상태를 `data/crawl_state.json`에 저장하고 읽습니다.

주요 함수는 다음과 같습니다.

- `get_state()`: 상태 파일을 읽습니다.
- `get_last_id()`: 마지막으로 저장된 차량 ID를 반환합니다.
- `is_initial_complete()`: 최초 전체 수집 완료 여부를 반환합니다.
- `save_state(last_id, initial_complete=False)`: 현재 위치와 완료 여부를 저장합니다.

상태 파일 예시는 다음과 같습니다.

```json
{
  "last_id": "500",
  "initial_complete": false
}
```

- `last_id`: 마지막으로 처리한 차량의 API ID입니다.
- `initial_complete`: 최초 전체 수집이 끝났는지를 나타냅니다.

### `used_car_storage.py`

API에서 받은 차량 데이터를 JSON 파일에 저장합니다.

주요 기능은 다음과 같습니다.

- 기존 `used_car.json` 읽기
- `listingNumber` 기준 중복 확인
- HTML 태그 제거
- 새로운 차량 데이터만 JSON에 추가
- JSON 파일 저장

새롭게 저장할 데이터가 없으면 기존 JSON 파일을 다시 저장하지 않고 `0`을 반환합니다.

### `used_car_crawler.py`

전체 수집과 증분 수집의 실행 순서를 관리합니다.

#### `initial_crawl()`

최초 전체 수집을 담당합니다.

- 상태 파일의 `last_id`부터 수집을 시작합니다.
- 한 페이지를 처리할 때마다 현재 위치를 상태 파일에 저장합니다.
- 응답의 `links.next`가 있으면 다음 페이지를 요청합니다.
- 전체 수집이 정상적으로 끝나면 `initial_complete`를 `true`로 저장합니다.
- 수집 완료 후 `convert_json_to_csv()`를 호출합니다.

#### `incremental_crawl()`

전체 수집 완료 후 새로운 데이터를 수집합니다.

- `last_id` 이후의 데이터를 요청합니다.
- 최대 500건까지 데이터를 처리합니다.
- 새로운 데이터가 저장된 경우에만 JSON 전체를 CSV로 다시 변환합니다.
- 마지막 수집 ID를 상태 파일에 저장합니다.

#### `main()`

수집 상태에 따라 실행할 수집 방식을 결정합니다.

- `initial_complete`가 `false`이면 전체 수집을 실행합니다.
- `initial_complete`가 `true`이면 증분 수집을 실행합니다.

### `json_to_csv.py`

`used_car.json`을 읽어 `used_car_flattened.csv`로 변환합니다.

주요 기능은 다음과 같습니다.

- 문자열로 저장된 dictionary와 list를 Python 구조로 복원합니다.
- 중첩된 dictionary와 list를 평탄화합니다.
- 부모 키와 자식 키를 `_`로 연결합니다.
- `createdAt`, `updatedAt`을 한국 시간으로 변환합니다.
- CSV 저장 시 최상위 `id` 컬럼을 제거합니다.
- 기존 JSON 파일은 수정하지 않습니다.
- 기존 CSV 파일이 있으면 새 변환 결과로 덮어씁니다.

## 4. 전체 실행 흐름

```text
used_car_clawling.py 실행
        ↓
used_car_crawler.main()
        ↓
crawl_state.json 확인
        ↓
initial_complete 확인
        ├── false → initial_crawl()
        └── true  → incremental_crawl()
        ↓
API 키 자동 발급
        ↓
차량 데이터 요청
        ↓
HTML 태그 제거
        ↓
listingNumber 중복 확인
        ↓
used_car.json 저장
        ↓
crawl_state.json 갱신
        ↓
JSON 전체를 CSV로 변환
```

초회 전체 수집에서는 API 응답의 `links.next`가 존재하는 동안 다음 페이지를 계속 요청합니다.

증분 수집에서는 마지막으로 저장한 `last_id` 이후의 데이터를 최대 500건까지 요청합니다.

## 5. 최초 실행

처음 실행할 때 `crawl_state.json`이 없으면 다음 기본 상태를 사용합니다.

```json
{
  "last_id": "",
  "initial_complete": false
}
```

이후 `initial_crawl()`이 API의 첫 페이지부터 데이터를 수집합니다.

각 페이지를 처리할 때 다음 순서로 동작합니다.

1. API 키를 발급받습니다.
2. 차량 데이터 한 페이지를 요청합니다.
3. HTML 태그를 제거합니다.
4. `listingNumber`를 기준으로 중복을 확인합니다.
5. 새로운 데이터를 `used_car.json`에 저장합니다.
6. 페이지의 마지막 차량 ID를 `crawl_state.json`에 저장합니다.
7. 다음 페이지가 있으면 같은 과정을 반복합니다.
8. 모든 페이지의 수집이 끝나면 `initial_complete`를 `true`로 저장합니다.
9. `used_car.json` 전체를 CSV로 변환합니다.

## 6. 수집 중단 후 재실행

수집 도중 프로그램이 종료되거나 서버 오류가 발생해도 정상적으로 저장된 마지막 페이지의 ID는 `crawl_state.json`에 남습니다.

프로그램을 다시 실행하면 `initial_complete`가 `false`인 동안 이전 `last_id`부터 전체 수집을 이어서 진행합니다.

예를 들어 상태 파일이 다음과 같다면:

```json
{
  "last_id": "30000",
  "initial_complete": false
}
```

다시 실행했을 때 `after_id=30000`부터 수집을 재개합니다.

API 요청 중 서버 오류가 발생하면 `request_page()`가 현재 위치를 유지하면서 5분마다 재시도합니다. 따라서 이미 저장된 데이터를 처음부터 다시 요청하지 않습니다.

## 7. 전체 수집 완료 후 재실행

전체 수집이 정상적으로 완료되면 상태 파일은 다음과 같이 저장됩니다.

```json
{
  "last_id": "105932",
  "initial_complete": true
}
```

이 상태에서 프로그램을 다시 실행하면 `incremental_crawl()`이 실행됩니다.

증분 수집에서는 `last_id` 이후의 새로운 데이터만 요청하고, 기존 `listingNumber`와 중복되는 데이터는 저장하지 않습니다.

## 8. 설치 방법

Python이 설치되어 있어야 합니다.

필요한 외부 패키지는 다음과 같습니다.

```bash
python -m pip install requests beautifulsoup4
```

다음 모듈은 Python 표준 라이브러리이므로 별도 설치가 필요하지 않습니다.

- `csv`
- `json`
- `ast`
- `datetime`
- `pathlib`
- `time`

## 9. 실행 방법

프로젝트 폴더로 이동한 뒤 다음 명령을 실행합니다.

```bash
python used_car_clawling.py
```

실행이 끝나면 다음 파일을 확인하실 수 있습니다.

```text
data/used_car.json
data/crawl_state.json
data/used_car_flattened.csv
```

CSV만 다시 생성하려면 다음 명령을 실행하시면 됩니다.

```bash
python json_to_csv.py
```

이 명령은 기존 JSON을 변경하지 않고, JSON 전체를 기준으로 CSV 파일을 새로 작성합니다.

## 10. JSON을 CSV로 변환하는 예시

다음과 같은 JSON이 있다고 가정합니다.

```json
{
  "id": 1,
  "listingNumber": "UC-0001",
  "brand": {
    "name": "현대"
  },
  "options": [
    "썬루프",
    "내비게이션"
  ],
  "createdAt": "2025-12-01T10:17:40.000Z"
}
```

CSV로 변환하면 다음과 같은 형태가 됩니다.

```text
listingNumber,brand_name,options_0,options_1,createdAt
UC-0001,현대,썬루프,내비게이션,2025-12-01 19:17:40
```

`createdAt`의 원본 값은 UTC 기준입니다.

```text
2025-12-01T10:17:40.000Z
```

CSV에는 한국 시간으로 변환되어 저장됩니다.

```text
2025-12-01 19:17:40
```

원본 JSON의 `id` 값은 유지되지만 CSV에서는 최상위 `id` 컬럼이 제거됩니다.

## 11. 처음부터 다시 수집하는 방법

현재 위치부터 이어서 수집하려면 `data` 폴더의 파일을 그대로 두고 프로그램을 다시 실행하시면 됩니다.

처음부터 새로 수집하려면 기존 데이터를 보관할 필요가 없는지 먼저 확인하셔야 합니다.

새로 시작하려면 다음 파일을 백업하거나 삭제하셔야 합니다.

```text
data/used_car.json
data/crawl_state.json
```

`crawl_state.json`만 삭제하고 `used_car.json`을 남겨두면 API 수집은 처음부터 시작하더라도 기존 `listingNumber`가 중복으로 판단되어 저장되지 않을 수 있습니다.

## 12. 데이터베이스 적재 시 참고 사항

현재 Python 코드에는 MySQL 또는 RDS에 직접 연결하는 기능이 포함되어 있지 않습니다.

현재 생성되는 CSV는 데이터베이스 적재에 사용할 수 있는 평탄화 파일입니다.

```text
data/used_car_flattened.csv
```

DB 적재 시에는 별도의 적재 스크립트나 DB 도구에서 해당 CSV 파일을 사용하시면 됩니다.

CSV의 다음 컬럼은 한국 시간 기준 `YYYY-MM-DD HH:MM:SS` 형식입니다.

```text
createdAt
updatedAt
```

최상위 `id` 컬럼은 CSV에서 제거되어 있으므로, 원본 `id`가 필요하시면 `used_car.json`을 사용하시거나 `json_to_csv.py`의 `remove_id_column()` 동작을 변경하셔야 합니다.

## 13. 주의 사항

- API 서버 주소가 변경되면 `used_car_config.py`의 `BASE_URL`을 수정하셔야 합니다.
- API 키는 코드에 직접 입력하지 않고 서버의 공개 키 API에서 자동으로 발급받습니다.
- `PAGE_LIMIT`은 현재 500으로 설정되어 있습니다.
- 서버가 허용하는 최대 요청 건수에 맞춰 `PAGE_LIMIT`을 설정하셔야 합니다.
- `429` 응답이 발생하면 `Retry-After` 헤더가 있으면 해당 시간만큼 기다립니다.
- `Retry-After` 헤더가 없으면 10초 후 재요청합니다.
- 서버 연결 오류나 네트워크 오류가 발생하면 300초, 즉 5분 후 같은 위치에서 재시도합니다.
- `used_car.json`은 수집 데이터 전체를 저장하므로 데이터가 많아지면 파일 용량이 커질 수 있습니다.
- 대용량 JSON·CSV 파일은 GitHub에 커밋하기 전에 파일 크기를 확인하셔야 합니다.
- GitHub에 올리지 않을 대용량 결과 파일은 `.gitignore`에 추가하시는 것이 좋습니다.
- 현재 실행 파일 이름은 기존 이름을 유지한 `used_car_clawling.py`입니다.