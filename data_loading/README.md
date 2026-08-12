# load_csv.sh의 README

# CSV MySQL 적재 셸스크립트

## 목적

API 등에서 생성한 CSV 파일을 MySQL 테이블에 적재하기 위한 셸스크립트이다. MySQL의 `LOAD DATA LOCAL INFILE`을 사용해 CSV 데이터를 일괄 적재한다.

## 실행 흐름

```text
CSV 파일 확인 → MySQL 접속 → CSV 데이터 적재 → 적재 결과 확인
```

## 사용 방법

스크립트에 CSV 파일 경로를 첫 번째 인자로 전달한다.

```bash
./load_csv.sh test/cars.csv
```

## 전제조건

- 대상 MySQL 데이터베이스와 테이블이 미리 생성되어 있어야 한다.
- 실행 계정에 대상 테이블에 데이터를 적재할 권한이 있어야 한다.
- MySQL 클라이언트와 서버에서 `local_infile`이 활성화되어 있어야 한다.
- CSV 파일의 형식과 대상 테이블의 컬럼 구성이 사전에 정의되어 있어야 한다.

## 주의사항

- CSV 컬럼 순서가 대상 테이블의 컬럼 순서 또는 스크립트에 지정한 컬럼 순서와 일치해야 한다.
- CSV 첫 행이 헤더인 경우 `IGNORE 1 ROWS`로 헤더를 제외한다.
- 보안을 위해 MySQL 비밀번호를 셸스크립트에 직접 작성하지 않는다.
- 동일한 CSV를 다시 적재하면 Primary Key 또는 Unique Key 중복이 발생할 수 있으므로 재실행 전에 중복 여부를 확인한다.

## Troubleshooting

### Access denied

MySQL 계정 정보와 대상 데이터베이스를 확인하고, 해당 계정에 테이블 적재 권한이 있는지 확인한다.

### ERROR 3948

클라이언트 또는 서버에서 `local_infile`이 비활성화된 경우 발생할 수 있다. 양쪽 설정을 확인하고, 필요하면 클라이언트 실행 시 `--local-infile=1`을 사용한다.

### 예상보다 적은 행이 적재된 경우

CSV의 실제 행 수를 확인하고, MySQL이 반환한 경고를 확인한다.

```bash
wc -l test/cars.csv
```

```sql
SHOW WARNINGS;
```

헤더 포함 여부, CSV 컬럼 순서, 줄바꿈 형식, Primary Key 또는 Unique Key 중복도 함께 확인한다.
