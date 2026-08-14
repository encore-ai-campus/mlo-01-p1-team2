# EC2 Git 설치 및 저장소 Clone 스크립트

프로젝트 루트의 setup_git.sh를 사용해 EC2에 Git을 설치하고, GitHub 인증 정보를 등록한 뒤 저장소를 clone합니다.

## 동작 내용

스크립트는 다음 작업을 순서대로 수행합니다.

1. EC2 운영체제의 패키지 관리자(apt-get, dnf, yum)를 확인합니다.
2. Git을 설치합니다.
3. Git 사용자 이름과 이메일을 전역 설정합니다.
4. GitHub Personal Access Token(PAT)을 화면에 표시하지 않고 입력받습니다.
5. 입력한 토큰을 Git credential helper에 등록합니다.
6. 지정한 폴더가 이미 존재하지 않는지 확인합니다.
7. GitHub 저장소를 지정한 폴더에 clone합니다.

## 현재 설정값

| 항목 | 값 |
|---|---|
| GitHub 사용자명 | Ducks-Lee |
| Git 이메일 | ducks9372@gmail.com |
| 원격 저장소 | https://github.com/encore-ai-campus/mlo-01-p1-team2.git |
| 기본 저장 위치 | /home/ec2-user/mlo-01-p1-team2 |

현재 스크립트의 저장 위치가 /home/ec2-user/...로 고정되어 있으므로, Ubuntu 등 다른 사용자로 실행한다면 DEST_DIR을 수정해야 합니다.

```bash
DEST_DIR="$HOME/mlo-01-p1-team2"
```

## 실행 방법

EC2에 프로젝트 파일을 준비한 뒤 프로젝트 루트에서 실행합니다.

```bash
chmod 700 setup_git.sh
./setup_git.sh
```

실행 중 다음 입력을 요청합니다.

```text
GitHub Personal Access Token:
```

토큰 입력 내용은 터미널에 표시되지 않습니다.

## GitHub 토큰 준비

private 저장소를 clone하려면 저장소에 접근할 수 있는 GitHub PAT가 필요합니다.

Fine-grained token을 사용하는 경우 다음 권한을 부여합니다.

- 대상 저장소: mlo-01-p1-team2
- Repository permissions: Contents: Read-only

토큰은 스크립트 파일에 직접 작성하지 마세요. 토큰이 노출된 경우 해당 토큰을 폐기하고 새 토큰을 발급하는 것이 안전합니다.

## 실행 후 확인

Git 설정을 확인합니다.

```bash
git config --global --get user.name
git config --global --get user.email
```

clone 결과를 확인합니다.

```bash
cd /home/ec2-user/mlo-01-p1-team2
git status
git remote -v
```

정상적으로 완료되면 원격 저장소 주소가 표시됩니다.

```text
https://github.com/encore-ai-campus/mlo-01-p1-team2.git
```

## 주의사항

스크립트는 다음 설정을 사용합니다.

```bash
git config --global credential.helper store
```

이 방식은 GitHub 토큰을 EC2 사용자의 ~/.git-credentials 파일에 저장합니다. 파일에는 토큰이 평문으로 저장될 수 있으므로 공용 서버나 운영 환경에서는 주의해야 합니다.

토큰을 더 이상 저장할 필요가 없다면 다음 명령으로 삭제할 수 있습니다.

```bash
git config --global --unset credential.helper || true
rm -f ~/.git-credentials
```

운영 환경에서는 AWS Secrets Manager, AWS Systems Manager Parameter Store 또는 SSH Deploy Key 사용을 권장합니다.

## 문제 해결

### 대상 폴더가 이미 존재합니다가 출력되는 경우

스크립트는 기존 파일을 덮어쓰지 않고 중단합니다. 기존 저장소를 사용할 경우 해당 폴더로 이동합니다.

```bash
cd /home/ec2-user/mlo-01-p1-team2
git pull
```

다른 위치에 다시 clone하려면 스크립트의 DEST_DIR 값을 변경합니다.

### 인증 실패가 발생하는 경우

- PAT가 만료되지 않았는지 확인합니다.
- PAT가 대상 저장소에 접근할 수 있는지 확인합니다.
- Fine-grained token에 Contents: Read-only 권한이 있는지 확인합니다.
- GitHub 사용자명이 Ducks-Lee인지 확인합니다.

### sudo 또는 패키지 관리자 오류가 발생하는 경우

EC2 인스턴스의 운영체제와 현재 사용자의 권한을 확인합니다.

```bash
cat /etc/os-release
whoami
```

GitHub PAT 관련 문서: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens

