# CSV → MySQL 적재 셸스크립트

API 등에서 수집한 CSV 파일을 MySQL 테이블에 적재하는 셸스크립트 안내서다. 대량 데이터를 빠르게 적재하기 위해 `LOAD DATA LOCAL INFILE`을 사용한다.

## 실행 흐름

```text
CSV 파일
  → 셸스크립트 실행
  → MySQL 클라이언트 접속
  → LOAD DATA LOCAL INFILE 실행
  → 적재 결과 확인
```

## 사용 방법

```bash
chmod +x load_csv.sh
./load_csv.sh ./data/cars.csv
```

스크립트의 첫 번째 인자로 적재할 CSV 파일 경로를 전달한다.

예시 스크립트:

```bash
#!/usr/bin/env bash

set -euo pipefail

DB_NAME="projectTest"
TABLE_NAME="cars"
CSV_PATH="${1:-}"

if [[ -z "$CSV_PATH" || ! -f "$CSV_PATH" ]]; then
    echo "CSV 파일이 존재하지 않습니다: $CSV_PATH"
    exit 1
fi

mysql --local-infile=1 "$DB_NAME" <<SQL
LOAD DATA LOCAL INFILE '$CSV_PATH'
INTO TABLE $TABLE_NAME
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
SQL
```

실제 프로젝트에서는 CSV 컬럼 순서에 맞춰 `INTO TABLE` 뒤에 대상 컬럼 목록을 명시하는 것을 권장한다.

```sql
LOAD DATA LOCAL INFILE '/path/to/cars.csv'
INTO TABLE cars
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(maker, model, model_year, price);
```

## 전제조건

- 대상 데이터베이스와 테이블이 미리 생성되어 있어야 한다.
- MySQL 계정에 대상 테이블에 데이터를 적재할 권한이 있어야 한다.
- MySQL 서버의 `local_infile` 기능이 활성화되어 있어야 한다.
- MySQL 클라이언트에서 `LOCAL INFILE` 사용이 허용되어 있어야 한다.
- CSV의 컬럼 순서, 구분자, 인코딩이 적재 대상과 일치해야 한다.

서버 설정 확인:

```sql
SHOW GLOBAL VARIABLES LIKE 'local_infile';
```

필요한 경우 관리자 권한으로 일시 활성화한다.

```sql
SET GLOBAL local_infile = ON;
```

재시작 후에도 유지해야 한다면 MySQL 서버 설정의 `[mysqld]` 섹션에 다음을 추가한다.

```ini
[mysqld]
local_infile=1
```

## MySQL 인증정보 관리

비밀번호를 셸스크립트나 명령줄에 직접 작성하지 않는다. MySQL 클라이언트 설정 파일을 사용하면 인증정보를 스크립트와 분리할 수 있다.

### `~/.my.cnf` 자동 참조

MySQL 클라이언트는 사용자 홈 디렉터리의 `~/.my.cnf`를 자동으로 읽는다.

```ini
[client]
host=127.0.0.1
port=3306
user=projectTest
password=실제비밀번호
local-infile=1
```

인증정보가 들어 있으므로 파일 권한을 현재 사용자만 읽을 수 있도록 제한한다.

```bash
chmod 600 ~/.my.cnf
```

설정 파일을 정상적으로 읽고 있는지 확인한다.

```bash
mysql --print-defaults
```

설정이 적용되면 출력 결과에 `--user=...`, `--host=...`, `--local-infile=1` 등의 옵션이 표시된다. 이후 스크립트에서는 사용자명과 비밀번호를 직접 지정하지 않고 다음처럼 실행할 수 있다.

```bash
mysql projectTest
```

스크립트의 `mysql --local-infile=1 "$DB_NAME"` 호출도 기본적으로 `~/.my.cnf`의 `[client]` 설정을 함께 사용한다.

### 임의의 설정 파일을 명시하는 방법

프로젝트별로 설정 파일을 나누거나 `~/.my.cnf`가 아닌 파일을 사용하려면 `--defaults-extra-file`로 경로를 명시한다.

예를 들어 `/path/to/mysql.cnf`의 내용이 다음과 같다고 하자.

```ini
[client]
host=127.0.0.1
port=3306
user=projectTest
password=실제비밀번호
local-infile=1
```

다음과 같이 실행한다. `--defaults-extra-file`은 `mysql` 명령 뒤의 첫 번째 옵션으로 지정한다.

```bash
mysql --defaults-extra-file=/path/to/mysql.cnf projectTest
```

셸스크립트에서 사용하는 경우:

```bash
CONFIG_FILE="/path/to/mysql.cnf"

mysql \
  --defaults-extra-file="$CONFIG_FILE" \
  "$DB_NAME" <<SQL
LOAD DATA LOCAL INFILE '$CSV_PATH'
INTO TABLE $TABLE_NAME
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
SQL
```

설정 적용 여부는 다음처럼 확인할 수 있다.

```bash
mysql --defaults-extra-file=/path/to/mysql.cnf --print-defaults
```

`.my.cnf`와 별도 `mysql.cnf` 파일에는 비밀번호가 포함될 수 있으므로 Git에 커밋하지 않는다. 저장소에 보관해야 하는 경우 `.gitignore`에 프로젝트별 경로를 추가한다.

```gitignore
.my.cnf
mysql.cnf
config/mysql.cnf
```

이미 비밀번호가 Git에 커밋된 경우에는 파일을 삭제하는 것만으로 충분하지 않으므로 해당 MySQL 비밀번호를 변경한다.

## 주의사항

- `LOAD DATA LOCAL INFILE`은 MySQL 클라이언트가 실행되는 환경의 파일을 읽는다. 서버 호스트의 파일 경로와 혼동하지 않는다.
- CSV에 헤더가 있으면 `IGNORE 1 ROWS`를 사용한다. 헤더가 없는 파일에는 제거하거나 조정한다.
- CSV 구분자, 따옴표, 줄바꿈, 문자 인코딩을 실제 파일 형식에 맞게 설정한다.
- 스크립트를 재실행하면 기본키 또는 유니크 키 중복 오류가 발생할 수 있다. 재실행 정책과 중복 처리 방식을 먼저 정한다.
- `LOCAL INFILE`은 파일을 읽는 클라이언트와 서버 양쪽에서 허용되어야 한다.
- 운영 환경에서는 최소 권한의 전용 계정을 사용하고, 설정 파일의 접근 권한을 제한한다.

## Troubleshooting

### `Loading local data is disabled` 오류

다음 항목을 확인한다.

1. 서버에서 `SHOW GLOBAL VARIABLES LIKE 'local_infile';` 결과가 `ON`인지 확인한다.
2. 클라이언트 실행 시 `--local-infile=1`을 지정했는지 확인한다.
3. `~/.my.cnf` 또는 별도 cnf의 `[client]` 섹션에 `local-infile=1`이 있는지 확인한다.
4. 해당 계정에 대상 테이블 적재 권한이 있는지 확인한다.

### `Access denied` 오류

- 사용자명, 비밀번호, 호스트, 포트가 올바른지 확인한다.
- `mysql --print-defaults` 또는 `mysql --defaults-extra-file=/path/to/mysql.cnf --print-defaults`로 실제 적용 옵션을 확인한다.
- `~/.my.cnf` 또는 별도 cnf의 권한이 `600`인지 확인한다.

### CSV 파일을 찾을 수 없음

- 스크립트에 전달한 경로와 파일 존재 여부를 확인한다.
- `LOCAL INFILE`은 MySQL 클라이언트 프로세스가 실행되는 시스템에서 파일을 읽는다는 점을 확인한다.

### 컬럼 수 또는 데이터 형식 오류

- CSV 헤더를 제외했는지(`IGNORE 1 ROWS`) 확인한다.
- CSV 컬럼 순서와 `LOAD DATA`의 컬럼 목록이 일치하는지 확인한다.
- 구분자, 따옴표, 줄바꿈, 문자 인코딩 설정을 확인한다.

### 중복 키 오류

- 대상 테이블의 기본키·유니크 키와 CSV 데이터를 확인한다.
- 재실행 전에 기존 적재 데이터를 정리하거나, 중복 데이터를 별도로 처리하는 정책을 적용한다.
