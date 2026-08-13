# MySQL 설치 셸 스크립트 실행 가이드

이 문서는 로컬 컴퓨터에서 EC2로 `setup_mysql.sh`를 전송하고, EC2에서 MySQL을 설치하는 방법을 설명합니다.

## 1. 로컬에서 EC2로 설치 스크립트 전송

로컬 PowerShell에서 프로젝트 폴더로 이동한 뒤 `scp -i` 명령을 실행합니다. 아래 값은 실제 환경에 맞게 바꿉니다.

```powershell
cd C:\workspace\1st_project

scp -i "C:\path\to\my-key.pem" .\setup_mysql.sh ec2-user@<EC2_PUBLIC_IP>:/home/ec2-user/
```

- `C:\path\to\my-key.pem`: EC2 생성 때 내려받은 키페어 파일 경로
- `<EC2_PUBLIC_IP>`: MySQL을 설치할 EC2의 퍼블릭 IPv4 주소
- `ec2-user`: Amazon Linux EC2의 기본 사용자입니다. 다른 AMI를 사용한다면 해당 사용자명으로 바꿉니다.

전송이 완료되면 다음과 비슷한 메시지가 표시됩니다.

```text
setup_mysql.sh                         100%  ...   ...
```

## 2. SSH로 EC2 접속

```powershell
ssh -i "C:\path\to\my-key.pem" ec2-user@<EC2_PUBLIC_IP>
```

EC2에서 파일이 전송되었는지 확인합니다.

```bash
ls -l /home/ec2-user/setup_mysql.sh
```

## 3. 설치 스크립트 실행

스크립트가 있는 위치에서 다음 명령을 실행합니다.

```bash
cd /home/ec2-user
sudo bash setup_mysql.sh
```

스크립트는 다음 작업을 순서대로 수행합니다.

1. MySQL Community 저장소와 GPG 키를 설정합니다.
2. MySQL Community Server를 설치합니다.
3. `mysqld` 서비스를 켜고 시작합니다.
4. `/var/log/mysqld.log`에서 최초 임시 root 비밀번호를 출력합니다.
5. 새 root 비밀번호와 `project_team2` 비밀번호를 입력받습니다.
6. 임시 root 비밀번호로 MySQL에 접속해 root 비밀번호 변경, 계정 생성, 권한 부여, `local_infile` 활성화, 권한 반영을 실행합니다.

## 4. 실행 중 비밀번호 입력 순서

현재 `setup_mysql.sh`의 입력 순서는 다음과 같습니다.

### 새 root 비밀번호

앞으로 사용할 MySQL root 비밀번호를 입력합니다.

### `project_team2` 비밀번호

새로 생성할 `project_team2` 계정의 비밀번호를 입력합니다.

### `Enter password:`

SQL 블록이 시작되면 다음과 같은 입력창이 다시 나타납니다.

```text
Enter password:
```

이때는 `/var/log/mysqld.log`에 출력된 **임시 root 비밀번호**를 입력합니다. 새 root 비밀번호나 `project_team2` 비밀번호를 입력하면 안 됩니다.

임시 비밀번호를 다시 확인하려면 다음 명령을 사용합니다.

```bash
sudo grep 'temporary password' /var/log/mysqld.log | tail -n 1
```

임시 비밀번호는 최초 설치 직후 root 계정에 한 번 사용되는 비밀번호입니다. SQL의 다음 문장이 성공하면 root 비밀번호는 입력한 새 비밀번호로 변경됩니다.

```sql
ALTER USER 'root'@'localhost' IDENTIFIED BY '새 root 비밀번호';
```

## 5. MySQL 기본 비밀번호 정책

MySQL 8.0의 기본 비밀번호 정책은 일반적으로 `MEDIUM`입니다. 따라서 root와 `project_team2`에 입력하는 새 비밀번호는 다음 조건을 만족해야 합니다.

- 8자 이상
- 영문 대문자 1개 이상
- 영문 소문자 1개 이상
- 숫자 1개 이상
- 특수문자 1개 이상
- 사용자명과 같거나 사용자명을 그대로 포함하는 비밀번호는 피합니다.

예를 들어 아래와 같은 형식입니다. 실제 사용 시에는 예시와 다른 비밀번호를 사용합니다.

```text
MyRoot!2026
ProjectTeam2!2026
```

조건을 만족하지 않는 비밀번호를 입력하면 다음 오류가 발생합니다.

```text
ERROR 1819 (HY000): Your password does not satisfy the current policy requirements
```

이 오류는 임시 비밀번호가 틀렸다는 뜻이 아니라, 새로 설정하려는 비밀번호가 MySQL 정책에 맞지 않는다는 뜻입니다. 대문자·소문자·숫자·특수문자를 포함한 8자 이상의 비밀번호로 다시 실행합니다.

현재 정책을 확인하려면 root 비밀번호 변경이 끝난 뒤 다음 명령을 실행합니다.

```bash
sudo mysql -u root -p -e "SHOW VARIABLES LIKE 'validate_password%';"
```

자세한 정책은 [MySQL 비밀번호 검증 정책 문서](https://dev.mysql.com/doc/mysql-security-excerpt/8.0/en/validate-password-options-variables.html)를 참고합니다.

## 6. 설치 결과 확인

MySQL 클라이언트와 서비스를 확인합니다.

```bash
mysql --version
sudo systemctl is-active mysqld
```

root 계정 접속을 확인합니다.

```bash
mysql -u root -p -e "SELECT VERSION();"
```

`project_team2` 계정 접속을 확인합니다.

```bash
mysql -u project_team2 -p -e "SELECT CURRENT_USER();"
```

출력에 다음과 비슷한 값이 나오면 정상입니다.

```text
project_team2@localhost
```

root 권한과 `local_infile` 설정도 확인할 수 있습니다.

```bash
sudo mysql -u root -p -e "SHOW GRANTS FOR 'project_team2'@'localhost';"
sudo mysql -u root -p -e "SHOW VARIABLES LIKE 'local_infile';"
```

`local_infile`의 값이 `ON`이면 현재 실행 중인 MySQL 서버에서 활성화된 상태입니다.

## 7. 설치 후 주의사항

- `project_team2`는 현재 스크립트에서 `'project_team2'@'localhost'`로 생성되므로 EC2 내부에서 접속할 때 사용하는 계정입니다.
- `project_team2`에는 `*.*` 대상의 전체 권한과 `WITH GRANT OPTION`이 부여됩니다. root와 같은 수준의 권한이므로 비밀번호를 다른 사람과 공유하지 않습니다.
- `SET GLOBAL local_infile = ON`은 현재 실행 중인 MySQL 서버에 적용됩니다. 서버 재시작 후에도 유지해야 한다면 별도의 MySQL 설정 파일에 영구 설정을 추가해야 합니다.
- 설치가 성공한 뒤에는 이 스크립트를 그대로 다시 실행하지 않습니다. 이미 root 비밀번호가 새 비밀번호로 바뀌었기 때문에 로그에 남은 임시 비밀번호로 재실행하면 `ERROR 1045`가 발생할 수 있습니다. 재실행 대신 위의 확인 명령을 사용합니다.

## 8. `.my.cnf` 설정

`setup_mysql.sh`는 `'project_team2'@'localhost'` 계정을 생성하고, `create_tables.sh`는 이 계정으로 MySQL에 접속합니다. 비밀번호를 명령어에 직접 입력하지 않으려면 EC2 사용자 홈 디렉터리에 `.my.cnf`를 둡니다.

```ini
[client]
host=localhost
port=3306
user=project_team2
password=<PROJECT_TEAM2_PASSWORD>
local-infile=1
```

`<PROJECT_TEAM2_PASSWORD>`는 `setup_mysql.sh` 실행 중 입력한 실제 비밀번호로 바꿉니다. `.my.cnf`는 현재 작업 폴더에 있다는 이유만으로 자동으로 읽히지 않으므로, 다음처럼 기본 위치에 배치하고 권한을 제한합니다.

```bash
cd /home/ec2-user
chmod 600 .my.cnf
mv .my.cnf ~/.my.cnf
chmod 600 ~/.my.cnf
```

로컬에서 두 파일을 함께 전송할 수도 있습니다.

```powershell
scp -i "C:\path\to\my-key.pem" .\create_tables.sh .\.my.cnf ec2-user@<EC2_PUBLIC_IP>:/home/ec2-user/
```

`.my.cnf`에는 비밀번호가 들어 있으므로 Git에 커밋하거나 다른 사용자와 공유하지 않습니다. 파일을 Windows에서 만든 경우 EC2에서 줄바꿈도 Linux 형식으로 변환합니다.

```bash
sed -i 's/\r$//' .my.cnf
```

### `.my.cnf`를 스크립트와 같은 폴더에 둘 때

`.my.cnf`를 홈 디렉터리가 아닌 스크립트 폴더에 보관하려면 `create_tables.sh`의 `mysql <<SQL` 부분을 다음처럼 바꿉니다.

```bash
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

mysql --defaults-extra-file="$SCRIPT_DIR/.my.cnf" <<SQL
```

`--defaults-extra-file`을 사용하면 현재 작업 폴더와 관계없이 해당 파일을 명시적으로 읽습니다.

## 9. `create_tables.sh` 실행

EC2에서 다음 순서로 실행합니다.

```bash
cd /home/ec2-user
sed -i 's/\r$//' create_tables.sh
chmod 700 create_tables.sh
./create_tables.sh
```

현재 스크립트는 `DB_NAME="car_data"`를 기준으로 다음 작업을 수행합니다.

1. `car_data` 데이터베이스를 없으면 생성합니다.
2. 자동차 원천 데이터와 등록대수 데이터에 필요한 테이블을 생성합니다.
3. `SHOW TABLES`로 생성 결과를 출력합니다.

이 스크립트에서 `project_team2`는 데이터베이스 이름이 아니라 MySQL 접속 계정입니다. 데이터베이스 이름을 바꾸려면 `create_tables.sh`의 `DB_NAME` 값을 수정합니다.

`~/.my.cnf`를 설정한 뒤에는 `sudo` 없이 실행하는 것이 중요합니다. `sudo bash create_tables.sh`로 실행하면 홈 디렉터리가 `/root`로 바뀌어 `/home/ec2-user/.my.cnf`를 읽지 못할 수 있습니다. 이 경우 MySQL은 기본 사용자 `root`로 비밀번호 없이 접속을 시도하여 다음 오류가 발생할 수 있습니다.

```text
ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: NO)
```

`$'\r': command not found`가 나오면 Windows 줄바꿈(CRLF)이 남아 있는 것이므로 `create_tables.sh`에 다음 명령을 다시 실행합니다.

```bash
sed -i 's/\r$//' create_tables.sh
```
