# 중고차 데이터 크롤링

차량 정보를 제공하는 API 서버에 요청을 보내 중고차 데이터를 수집하고, 수집한 결과를 JSON 파일로 저장하는 프로그램입니다.

이 프로그램은 처음 실행할 때는 차량 데이터를 처음부터 전체적으로 수집합니다. 전체 수집이 끝난 뒤 다시 실행하면, 이미 받은 데이터는 다시 받지 않고 새로운 데이터만 이어서 수집합니다.

## 1. 프로그램의 주요 기능

- 차량 데이터 전체 수집
- 전체 수집이 끝난 뒤 새로운 데이터만 증분 수집
- 중복된 `listingNumber` 데이터 제외
- API 응답에 포함된 HTML 태그 제거
- API 키 자동 발급
- API 키 만료 시 새 API 키 발급 후 재요청
- 호출 제한이 발생하면 일정 시간 기다린 뒤 재요청
- 네트워크 오류가 발생하면 기다린 뒤 같은 위치에서 재시도
- 현재 수집 위치를 상태 파일에 저장
- `data` 폴더가 없으면 자동 생성

## 2. 폴더 구조

모든 Python 모듈은 실행 파일과 같은 폴더에 둡니다.

```text
새 폴더/
├── used_car_clawling.py  # 프로그램을 시작하는 파일
├── used_car_api.py       # API 키 발급과 차량 API 요청
├── used_car_config.py    # 서버 주소, 파일 경로, 수집 설정
├── used_car_state.py     # 수집 상태 파일 읽기·저장
├── used_car_storage.py   # 차량 데이터 정리·중복 확인·JSON 저장
├── used_car_crawler.py   # 전체 수집·증분 수집 흐름
├── json_to_csv.py        # JSON 데이터를 CSV로 변환
└── data/
    ├── used_car.json     # 수집된 차량 데이터
    └── crawl_state.json  # 마지막 수집 위치와 완료 상태
```

## 3. 모듈별 역할

### `used_car_clawling.py`

프로그램을 실제로 실행하는 시작 파일입니다.

이 파일을 실행하면 `used_car_crawler.py`에 있는 `main()` 함수를 호출합니다.

```bash
python used_car_clawling.py
```

### `used_car_config.py`

프로그램에서 공통으로 사용하는 설정을 모아둔 파일입니다.

- API 서버 주소
- `data` 폴더 경로
- JSON 파일 경로
- 한 번에 요청할 데이터 수
- 재시도 대기 시간
- 차량 식별에 사용할 필드명

### `used_car_api.py`

API 서버와 통신하는 파일입니다.

차량 데이터를 요청하기 전에 공개 키 API에 요청해 API 키를 가져옵니다. 가져온 키는 `X-API-Key`라는 요청 헤더에 넣어 차량 API 요청에 사용합니다.

API 키가 만료되어 `403` 응답이 오면 새 키를 발급받고 같은 요청을 다시 시도합니다.

### `used_car_state.py`

수집 진행 상황을 `crawl_state.json`에 저장하고 읽는 파일입니다.

```json
{
  "last_id": "500",
  "initial_complete": true
}
```

- `last_id`: 마지막으로 요청한 차량의 ID
- `initial_complete`: 최초 전체 수집 완료 여부

이 파일 덕분에 프로그램을 다시 실행해도 수집 위치를 기억하고 이어서 작업할 수 있습니다.

### `used_car_storage.py`

API에서 받은 차량 데이터를 저장하는 파일입니다.

- 기존 `used_car.json` 읽기
- `listingNumber`를 이용한 중복 확인
- HTML 태그 제거
- 새로운 차량 데이터를 JSON으로 저장

### `used_car_crawler.py`

전체 수집과 증분 수집의 순서를 관리하는 파일입니다.

- `initial_crawl()`: 최초 전체 수집
- `incremental_crawl()`: 새로운 데이터 증분 수집
- `main()`: 어떤 수집 방식을 사용할지 결정

## 4. 실행 흐름

```text
used_car_clawling.py 실행
        ↓
main() 실행
        ↓
crawl_state.json 확인
        ↓
최초 전체 수집이 끝났는지 확인
        ├── 끝나지 않음 → initial_crawl()
        └── 끝남       → incremental_crawl()
        ↓
API 키 발급
        ↓
차량 데이터 요청
        ↓
중복 확인 및 데이터 정리
        ↓
used_car.json 저장
        ↓
현재 위치를 crawl_state.json에 저장
```

## 5. 최초 실행

처음 실행할 때 `crawl_state.json`이 없으면 최초 전체 수집으로 시작합니다.

전체 수집 과정은 다음과 같습니다.

1. API 키를 발급받습니다.
2. 차량 데이터를 요청합니다.
3. 받은 데이터를 `used_car.json`에 저장합니다.
4. 현재 페이지의 마지막 차량 ID를 `crawl_state.json`에 저장합니다.
5. 다음 페이지가 있으면 같은 과정을 반복합니다.
6. 전체 수집이 끝나면 `initial_complete`를 `true`로 저장합니다.

## 6. 다시 실행할 때

최초 전체 수집이 끝난 뒤 프로그램을 다시 실행하면 `crawl_state.json`의 `last_id`를 확인합니다.

그다음 해당 ID 이후의 새로운 차량 데이터를 요청합니다. 이미 `used_car.json`에 있는 `listingNumber`는 중복으로 판단해 저장하지 않습니다.

## 7. 설치 방법

Python이 설치되어 있어야 합니다. 필요한 외부 패키지는 다음과 같습니다.

```bash
pip install requests beautifulsoup4
```

## 8. 실행 방법

모듈 파일들이 모두 같은 폴더에 있는지 확인한 뒤 실행합니다.

```bash
python used_car_clawling.py
```

실행이 끝나면 수집된 데이터는 다음 위치에서 확인할 수 있습니다.

```text
data/used_car.json
```

현재 수집 위치와 전체 수집 완료 여부는 다음 파일에서 확인할 수 있습니다.

```text
data/crawl_state.json
```

## 9. 참고 사항

- `data` 폴더는 프로그램 실행 시 없으면 자동으로 생성됩니다.
- `used_car.json`은 기존 데이터에 새로운 차량 데이터를 추가하는 방식으로 저장됩니다.
- `crawl_state.json`을 삭제하면 프로그램이 마지막 위치를 기억하지 못하므로 다시 전체 수집을 시작할 수 있습니다.
- API 서버에 연결할 수 있어야 프로그램이 정상적으로 데이터를 수집할 수 있습니다.
- 현재 실행 파일 이름은 기존 이름을 유지한 `used_car_clawling.py`입니다.

## 10. JSON 데이터를 CSV로 변환하기

`json_to_csv.py`는 크롤링 결과로 만들어진 `used_car.json`을 읽어 CSV 파일로 변환합니다.

### 입력 파일

```text
data/used_car.json
```

### 출력 파일

```text
data/used_car_flattened.csv
```

### 변환 내용

- JSON 파일을 읽습니다.
- 중첩된 dictionary와 list 구조를 CSV 열로 펼칩니다.
- 부모 키와 자식 키를 `_`로 연결합니다.
- list의 항목에는 순서 번호를 붙입니다.
- 모든 차량 데이터의 열 이름을 모아 CSV의 첫 번째 줄에 작성합니다.

예를 들어 다음과 같은 JSON은:

```json
{
  "id": 1,
  "car": {
    "brand": "현대",
    "options": ["썬루프", "네비"]
  }
}
```

다음과 같은 CSV 열로 변환됩니다.

```text
id,car_brand,car_options_0,car_options_1
1,현대,썬루프,네비
```

### 실행 방법

`json_to_csv.py`와 `data/used_car.json`이 준비되어 있는지 확인한 뒤 실행합니다.

```bash
python json_to_csv.py
```

실행이 끝나면 다음 위치에 CSV 파일이 생성됩니다.

```text
data/used_car_flattened.csv
```

기존 JSON 파일은 수정하지 않습니다. 같은 이름의 CSV 파일이 이미 있으면 새 변환 결과로 덮어씁니다.
