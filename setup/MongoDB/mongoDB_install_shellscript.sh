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