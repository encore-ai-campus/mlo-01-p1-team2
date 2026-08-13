# Amazon Linux 2023 MongoDB 8.0 설치 가이드

이 문서는 **Amazon Linux 2023 x86_64** 서버에 MongoDB를 설치하고 서비스로 실행하는 과정을 정리한 문서입니다.

최종 권장 방식은 MongoDB 공식 `dnf/yum` 저장소를 등록한 뒤 `mongodb-org` 패키지를 설치하는 것입니다. `.tgz` 파일을 내려받아 직접 배치하는 수동 설치보다 의존성, systemd 서비스 등록, 업데이트를 관리하기 쉽습니다.

## 최종 결론

- OS 패키지를 업데이트합니다.
- MongoDB 8.0 공식 저장소를 등록합니다.
- `mongodb-org`를 설치합니다.
  - `mongod`
  - `mongosh`
  - `mongoimport`를 포함한 MongoDB 도구
- `systemctl enable --now mongod`로 즉시 시작하고 부팅 시 자동 시작을 설정합니다.
- 각 실행 파일과 MongoDB 서비스 상태를 확인합니다.

## 대상 환경과 전제 조건

- Amazon Linux 2023
- x86_64 아키텍처
- `sudo` 권한이 있는 사용자
- MongoDB 저장소에 연결할 수 있는 네트워크
- 패키지 설치와 OS 업데이트를 수행할 수 있는 디스크 여유 공간

이 문서의 저장소 URL은 `x86_64`용입니다. Graviton 등 ARM64 인스턴스에서는 동일한 URL을 사용하면 안 되므로 해당 아키텍처에 맞는 MongoDB 저장소 URL을 별도로 확인해야 합니다.

## 사용자가 제공한 최종 설치 스크립트

```bash
#!/bin/bash
set -e

# 1. OS 패키지 업데이트
sudo dnf update -y

# 2. MongoDB repository 등록
sudo tee /etc/yum.repos.d/mongodb-org-8.0.repo > /dev/null <<'EOF'
[mongodb-org-8.0]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2023/mongodb-org/8.0/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://pgp.mongodb.com/server-8.0.asc
EOF

# 3. MongoDB 전체 패키지 설치
# mongod, mongosh, mongoimport 등 포함
sudo dnf install -y mongodb-org

# 4. MongoDB 시작 + 부팅 시 자동 시작
sudo systemctl enable --now mongod

# 5. 확인
mongod --version
mongosh --version
```

## 실행 방법

예를 들어 파일명을 `install-mongodb.sh`로 저장합니다.

```bash
chmod +x install-mongodb.sh
./install-mongodb.sh
```

스크립트 내부에 필요한 명령마다 `sudo`가 들어 있으므로 실행할 때 `sudo ./install-mongodb.sh`로 감쌀 필요는 없습니다. 실행 사용자는 `sudo`를 사용할 수 있어야 합니다.

`set -e`가 설정되어 있어 어느 단계에서든 오류가 발생하면 이후 단계는 실행되지 않습니다. 오류 메시지를 기준으로 해당 단계부터 확인하면 됩니다.

## 예상 결과

정상 실행되면 다음과 같은 흐름의 출력이 표시됩니다. 실제 MongoDB와 `mongosh` 버전 번호는 설치 시점의 최신 패키지에 따라 달라질 수 있습니다.

```text
Complete!
Created symlink ... mongod.service ...
db version v8.0.x
mongosh 2.x.x
```

핵심은 다음 두 결과입니다.

- 패키지 설치가 `Complete!`로 끝남
- `mongod` 서비스가 enable 및 active 상태가 됨

## 설치 확인 명령

다음 명령으로 실행 파일, 패키지, 서비스, 실제 MongoDB 응답을 확인할 수 있습니다.

```bash
# 실행 파일 위치
command -v mongod
command -v mongosh
command -v mongoimport

# 버전 확인
mongod --version
mongosh --version
mongoimport --version

# 설치된 MongoDB RPM 확인
rpm -qa | grep -E '^mongodb(-org|-)'

# 서비스가 부팅 시 자동 시작으로 설정되었는지 확인
sudo systemctl is-enabled mongod

# 현재 실행 중인지 확인
sudo systemctl is-active mongod

# 상세 상태 확인
sudo systemctl status mongod --no-pager

# 로컬 MongoDB에 ping 요청
mongosh --eval 'db.runCommand({ ping: 1 })'
```

정상적인 ping 결과에는 다음과 같이 `ok: 1`이 포함됩니다.

```text
{ ok: 1 }
```

`systemctl is-enabled mongod`의 결과는 `enabled`, `systemctl is-active mongod`의 결과는 `active`여야 합니다.

## 왜 `.tgz` 수동 설치 대신 패키지 설치를 선택했는가

초기에는 MongoDB `.tgz` 파일을 직접 내려받아 압축을 풀고 배치하는 방식을 시도했지만, 다음과 같은 문제가 발생했습니다.

1. `/tmp` 용량 문제

   다운로드 또는 압축 해제 과정에서 `/tmp`의 여유 공간이 부족해질 수 있습니다. 패키지 설치 방식은 OS 패키지 관리 흐름 안에서 설치하므로 이러한 임시 파일과 설치 단계를 한곳에서 수동 관리할 필요가 줄어듭니다.

2. `curl-minimal`과 `libcurl-minimal` 충돌

   수동 다운로드와 의존성 처리 과정에서 Amazon Linux 기본 패키지인 `curl-minimal`/`libcurl-minimal` 계열 충돌이 발생했습니다. 시스템 패키지를 강제로 제거하거나 덮어쓰면 다른 OS 도구에 영향을 줄 수 있습니다. `dnf` 기반 설치는 저장소 메타데이터와 패키지 의존성을 함께 처리하므로 이 방식이 더 안정적입니다.

3. `mongod.service` 부재

   `.tgz`는 실행 파일을 제공할 뿐, 일반적으로 `mongod.service`, 기본 설정 파일, 서비스 사용자, 로그·데이터 디렉터리와 권한을 자동으로 구성하지 않습니다. 그래서 `systemctl enable --now mongod`를 실행해도 `mongod.service`를 찾지 못하는 문제가 생길 수 있습니다.

`mongodb-org` 패키지는 MongoDB 서버와 셸·도구를 패키지 의존성으로 설치하고 systemd 서비스 등록에 필요한 구성을 제공하므로, Amazon Linux 2023에서는 저장소 기반 설치가 재현성과 운영 편의성 면에서 적합합니다.

## 트러블슈팅

### 저장소 또는 패키지 메타데이터 오류

저장소 파일이 정확히 생성되었는지 확인합니다.

```bash
sudo cat /etc/yum.repos.d/mongodb-org-8.0.repo
sudo dnf repolist
sudo dnf clean all
sudo dnf makecache
```

저장소 URL에 접근할 수 있는지, 인스턴스의 DNS·인터넷 연결·보안 정책이 정상인지도 확인합니다. GPG 검증을 끄거나 서명 검증을 우회하는 방식은 사용하지 않는 것이 좋습니다.

### `mongod.service not found`

`.tgz` 수동 설치만 되어 있거나 패키지 설치가 중간에 실패한 경우에 발생할 수 있습니다. 패키지 설치를 완료한 뒤 서비스를 다시 등록합니다.

```bash
sudo dnf install -y mongodb-org
sudo systemctl daemon-reload
sudo systemctl enable --now mongod
sudo systemctl status mongod --no-pager
```

### 서비스가 시작되지 않음

서비스 로그와 MongoDB 로그를 먼저 확인합니다.

```bash
sudo journalctl -u mongod -n 100 --no-pager
sudo tail -n 100 /var/log/mongodb/mongod.log
```

설정 파일 문법, 데이터 디렉터리와 로그 디렉터리 권한, 이미 사용 중인 포트가 있는지 확인합니다.

```bash
sudo grep -nE 'bindIp|port' /etc/mongod.conf
sudo ss -lntp | grep 27017
```

### `curl-minimal`/`libcurl-minimal` 관련 충돌

기존 `.tgz` 설치 과정에서 남은 수동 패키지나 불완전한 의존성 상태가 있는지 확인합니다.

```bash
rpm -qa | grep -E '(^|-)curl|libcurl'
sudo dnf check
```

`curl-minimal`을 강제로 삭제하지 말고, 충돌 메시지 전체를 확인한 뒤 `dnf`가 제시하는 의존성 해결 방법을 우선 사용합니다. 필요하면 기존 수동 설치 흔적을 정리한 후 `sudo dnf install -y mongodb-org`를 다시 실행합니다.

### 명령을 찾을 수 없음

설치가 끝났는지와 PATH를 확인합니다.

```bash
rpm -qa | grep -E '^mongodb(-org|-)'
command -v mongod
command -v mongosh
command -v mongoimport
```

패키지 설치가 완료되지 않았다면 다음을 다시 실행합니다.

```bash
sudo dnf install -y mongodb-org
```

## 네트워크와 보안 주의사항

MongoDB는 기본적으로 로컬 호스트에서만 접근하도록 설정하는 것이 안전합니다. 일반적으로 `/etc/mongod.conf`의 `net.bindIp`는 `127.0.0.1`로 시작하고, 기본 포트는 `27017`입니다.

원격 접속이 꼭 필요한 경우에만 다음 원칙을 적용합니다.

- `bindIp: 0.0.0.0`을 무심코 사용하지 않습니다.
- MongoDB 서버에 실제로 할당된 사설 IP와 `127.0.0.1`처럼 필요한 주소만 bind합니다.
- AWS Security Group의 TCP 27017 인바운드는 애플리케이션 서버 또는 신뢰할 수 있는 사설 CIDR로 제한합니다.
- 인터넷 전체(`0.0.0.0/0`)에 27017을 공개하지 않습니다.
- 원격 공개 전 관리자 계정, 인증(`security.authorization`), 필요 시 TLS를 구성합니다.
- 설정을 변경한 뒤에만 서비스를 재시작합니다.

예를 들어 설정을 확인한 뒤에는 다음처럼 서비스를 재시작할 수 있습니다.

```bash
sudo systemctl restart mongod
sudo systemctl is-active mongod
```

## 운영 전 체크리스트

- [ ] Amazon Linux 2023의 아키텍처가 `x86_64`인지 확인
- [ ] 저장소 GPG 검증을 유지
- [ ] `mongod` 서비스가 `enabled`/`active`인지 확인
- [ ] `mongosh`와 `mongoimport` 버전 확인
- [ ] 데이터·로그 디렉터리의 디스크 사용량 모니터링
- [ ] 원격 접속이 필요하지 않다면 `bindIp`를 로컬호스트로 유지
- [ ] 원격 접속이 필요하다면 인증, TLS, Security Group 제한을 먼저 구성
- [ ] 백업과 복구 절차를 운영 환경에 맞게 별도로 검증
