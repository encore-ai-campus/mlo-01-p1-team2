#!/bin/bash

set -e

DB_NAME="car_data"

echo "DB 및 테이블 생성 시작"

mysql <<SQL

CREATE DATABASE IF NOT EXISTS $DB_NAME;
USE $DB_NAME;
CREATE TABLE IF NOT EXISTS used_cars (
    `id` INT NOT NULL,
    `listingNumber` VARCHAR(50) NOT NULL PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `brand_id` INT,
    `brand_name` VARCHAR(100),
    `brand_slug` VARCHAR(100),
    `brand_country` VARCHAR(50),
    `model_id` INT,
    `model_name` VARCHAR(100),
    `model_slug` VARCHAR(100),
    `model_bodyType` VARCHAR(50),
    `trim` VARCHAR(100),
    `modelYear` INT,
    `firstRegistration` DATE,
    `mileageKm` INT,
    `fuelType` VARCHAR(50),
    `transmission` VARCHAR(50),
    `price` BIGINT,
    `currency` VARCHAR(10),
    `color` VARCHAR(50),
    `displacementCc` INT,
    `accidentCount` INT,
    `ownerChangeCount` INT,
    `inspectionStatus` VARCHAR(50),
    `status` VARCHAR(50),
    `location_id` INT,
    `location_province` VARCHAR(50),
    `location_city` VARCHAR(50),
    `location_slug` VARCHAR(100),
    `dealer_code` VARCHAR(100),
    `dealer_displayName` VARCHAR(100),
    `dealer_department` VARCHAR(100),
    `dealer_position` VARCHAR(100),
    `businessArea_id` VARCHAR(50),
    `businessArea_name` VARCHAR(100),
    `businessArea_parent_id` VARCHAR(50),
    `businessArea_parent_name` VARCHAR(100),
    `createdAt` DATETIME,
    `updatedAt` DATETIME
);

CREATE TABLE IF NOT EXISTS staging_used_cars (
    `id` INT NOT NULL,
    `listingNumber` VARCHAR(50) NOT NULL PRIMARY KEY,
    `title` VARCHAR(255) NOT NULL,
    `description` TEXT,
    `brand_id` INT,
    `brand_name` VARCHAR(100),
    `brand_slug` VARCHAR(100),
    `brand_country` VARCHAR(50),
    `model_id` INT,
    `model_name` VARCHAR(100),
    `model_slug` VARCHAR(100),
    `model_bodyType` VARCHAR(50),
    `trim` VARCHAR(100),
    `modelYear` INT,
    `firstRegistration` DATE,
    `mileageKm` INT,
    `fuelType` VARCHAR(50),
    `transmission` VARCHAR(50),
    `price` BIGINT,
    `currency` VARCHAR(10),
    `color` VARCHAR(50),
    `displacementCc` INT,
    `accidentCount` INT,
    `ownerChangeCount` INT,
    `inspectionStatus` VARCHAR(50),
    `status` VARCHAR(50),
    `location_id` INT,
    `location_province` VARCHAR(50),
    `location_city` VARCHAR(50),
    `location_slug` VARCHAR(100),
    `dealer_code` VARCHAR(100),
    `dealer_displayName` VARCHAR(100),
    `dealer_department` VARCHAR(100),
    `dealer_position` VARCHAR(100),
    `businessArea_id` VARCHAR(50),
    `businessArea_name` VARCHAR(100),
    `businessArea_parent_id` VARCHAR(50),
    `businessArea_parent_name` VARCHAR(100),
    `createdAt` DATETIME,
    `updatedAt` DATETIME
);

CREATE TABLE car_registration_long (
    stat_month CHAR(6) NOT NULL,
    region_level VARCHAR(10) NOT NULL,
    sido_name VARCHAR(20) NOT NULL,
    sigungu_name VARCHAR(50) NOT NULL DEFAULT '',

    vehicle_type VARCHAR(20) NOT NULL,
    use_type VARCHAR(20) NOT NULL,
    registration_count INT UNSIGNED NOT NULL,
    unit VARCHAR(10) NOT NULL,

    source_measure_key VARCHAR(50) NOT NULL,
    source_form_id INT UNSIGNED NOT NULL,
    source_row_no INT UNSIGNED NULL,
    is_aggregate TINYINT(1) NOT NULL,

    PRIMARY KEY (
        source_form_id,
        stat_month,
        region_level,
        sido_name,
        sigungu_name,
        source_measure_key
    )
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;

CREATE TABLE staging_car_registration_long (
    stat_month CHAR(6) NOT NULL,
    region_level VARCHAR(10) NOT NULL,
    sido_name VARCHAR(20) NOT NULL,
    sigungu_name VARCHAR(50) NOT NULL DEFAULT '',

    vehicle_type VARCHAR(20) NOT NULL,
    use_type VARCHAR(20) NOT NULL,
    registration_count INT UNSIGNED NOT NULL,
    unit VARCHAR(10) NOT NULL,

    source_measure_key VARCHAR(50) NOT NULL,
    source_form_id INT UNSIGNED NOT NULL,
    source_row_no INT UNSIGNED NULL,
    is_aggregate TINYINT(1) NOT NULL,

    PRIMARY KEY (
        source_form_id,
        stat_month,
        region_level,
        sido_name,
        sigungu_name,
        source_measure_key
    )
)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_unicode_ci;


SHOW TABLES;

SQL

echo "테이블 생성 완료"
