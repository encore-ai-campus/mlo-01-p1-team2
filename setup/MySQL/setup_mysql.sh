#!/usr/bin/env bash

sudo wget https://dev.mysql.com/get/mysql80-community-release-el9-1.noarch.rpm


sudo curl -fsSL \
  https://repo.mysql.com/RPM-GPG-KEY-mysql-2025 \
  -o /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql-2025


sudo rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-mysql-2025
sudo sed -i \
  's/RPM-GPG-KEY-mysql-[0-9]{4}/RPM-GPG-KEY-mysql-2025/g' \
  /etc/yum.repos.d/mysql-community*.repo


sudo dnf clean all
sudo rm -rf /var/cache/dnf
sudo dnf makecache

sudo dnf install mysql80-community-release-el9-1.noarch.rpm -y


sudo dnf install mysql-community-server -y


sudo systemctl enable --now mysqld


sudo grep 'temporary password' /var/log/mysqld.log


sql_escape() {
  local value="$1"
  value=${value//\\/\\\\}
  value=${value//\'/\'\'}
  printf '%s' "$value"
}


read -r -s -p '새 root 비밀번호: ' ROOT_PASSWORD
echo
read -r -s -p 'project_team2 비밀번호: ' PROJECT_TEAM2_PASSWORD
echo

ROOT_PASSWORD_SQL="$(sql_escape "$ROOT_PASSWORD")"
PROJECT_TEAM2_PASSWORD_SQL="$(sql_escape "$PROJECT_TEAM2_PASSWORD")"
trap 'unset CURRENT_ROOT_PASSWORD ROOT_PASSWORD PROJECT_TEAM2_PASSWORD ROOT_PASSWORD_SQL PROJECT_TEAM2_PASSWORD_SQL' EXIT

mysql --connect-expired-password -u root -p <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED BY '${ROOT_PASSWORD_SQL}';
CREATE USER IF NOT EXISTS 'project_team2'@'localhost' IDENTIFIED BY '${PROJECT_TEAM2_PASSWORD_SQL}';
ALTER USER 'project_team2'@'localhost' IDENTIFIED BY '${PROJECT_TEAM2_PASSWORD_SQL}';
GRANT ALL PRIVILEGES ON *.* TO 'project_team2'@'localhost' WITH GRANT OPTION;
SET GLOBAL local_infile = ON;
FLUSH PRIVILEGES;
exit
SQL
