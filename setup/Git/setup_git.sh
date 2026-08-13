#!/usr/bin/env bash
set -euo pipefail

# 고정값
GITHUB_USER="Ducks-Lee"
GIT_EMAIL="ducks9372@gmail.com"

# 수정할 부분
REPO_URL="https://github.com/encore-ai-campus/mlo-01-p1-team2.git"
DEST_DIR="/home/ec2-user/mlo-01-p1-team2"

# Git 설치
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update
    $SUDO apt-get install -y git
elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y git
elif command -v yum >/dev/null 2>&1; then
    $SUDO yum install -y git
else
    echo "지원하는 패키지 관리자를 찾지 못했습니다."
    exit 1
fi

# Git 커밋 정보 설정
git config --global user.name "$GITHUB_USER"
git config --global user.email "$GIT_EMAIL"

# 토큰 입력
read -rsp "GitHub Personal Access Token: " GITHUB_TOKEN
echo

# 토큰 저장
git config --global credential.helper store

printf 'protocol=https\nhost=github.com\nusername=%s\npassword=%s\n\n' \
    "$GITHUB_USER" "$GITHUB_TOKEN" | git credential approve

# clone 대상 폴더 확인
if [ -e "$DEST_DIR" ]; then
    echo "대상 폴더가 이미 존재합니다: $DEST_DIR"
    exit 1
fi

# 저장소 clone
git clone "$REPO_URL" "$DEST_DIR"

unset GITHUB_TOKEN

echo "Git 설치, 사용자 설정, 토큰 등록, clone이 완료되었습니다."