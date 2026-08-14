import ast
import csv
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

INPUT_FILE = BASE_DIR / "data" / "used_car.json"
OUTPUT_FILE = BASE_DIR / "data" / "used_car_flattened.csv"


# 변환 대상 datetime 컬럼
DATETIME_COLUMNS = {
    "createdAt",
    "updatedAt",
}

# CSV에 저장할 DB datetime 형식
DB_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# 한국 표준시 UTC+9
KST = timezone(timedelta(hours=9))


def parse_stringified_structure(value):
    """문자열로 저장된 dict/list를 실제 Python 구조로 복원합니다."""

    if not isinstance(value, str):
        return value

    text = value.strip()

    if not (
        (text.startswith("{") and text.endswith("}"))
        or
        (text.startswith("[") and text.endswith("]"))
    ):
        return value

    try:
        parsed = ast.literal_eval(text)

    except (ValueError, SyntaxError):
        return value

    return (
        parsed
        if isinstance(parsed, (dict, list))
        else value
    )


def normalize_nested_values(value):
    """중첩된 dict/list와 문자열 형태의 dict/list를 재귀적으로 정리합니다."""

    parsed = parse_stringified_structure(value)

    if parsed is not value:
        return normalize_nested_values(parsed)

    if isinstance(value, dict):
        return {
            key: normalize_nested_values(child)
            for key, child in value.items()
        }

    if isinstance(value, list):
        return [
            normalize_nested_values(child)
            for child in value
        ]

    return value


def convert_datetime_for_db(value):
    """
    ISO 8601 UTC 날짜를 한국시간 DB DATETIME 형식으로 변환합니다.

    예:
    2025-12-01T10:17:40.000Z
    →
    2025-12-01 19:17:40
    """

    if value is None:
        return ""

    if not isinstance(value, str):
        return value

    text = value.strip()

    if not text:
        return ""

    try:
        # Z는 UTC를 의미합니다.
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        parsed_datetime = datetime.fromisoformat(text)

        # 시간대가 없으면 UTC로 간주합니다.
        if parsed_datetime.tzinfo is None:
            parsed_datetime = parsed_datetime.replace(
                tzinfo=timezone.utc
            )

        # UTC를 한국시간으로 변환합니다.
        parsed_datetime = (
            parsed_datetime
            .astimezone(KST)
            .replace(tzinfo=None)
        )

        return parsed_datetime.strftime(
            DB_DATETIME_FORMAT
        )

    except ValueError:
        print(
            f"datetime 변환 실패 - 원본 값을 유지합니다: {value}"
        )
        return value


def preprocess_datetime_fields(row):
    """createdAt과 updatedAt을 한국시간으로 변환합니다."""

    processed_row = dict(row)

    for column_name in DATETIME_COLUMNS:
        if column_name in processed_row:
            processed_row[column_name] = (
                convert_datetime_for_db(
                    processed_row[column_name]
                )
            )

    return processed_row


def flatten_json(value, parent_key="", separator="_"):
    """중첩 JSON을 한 행의 평탄한 dictionary로 변환합니다."""

    flattened = {}

    if isinstance(value, dict):
        if not value and parent_key:
            flattened[parent_key] = ""

        for key, child in value.items():
            new_key = (
                f"{parent_key}{separator}{key}"
                if parent_key
                else str(key)
            )

            flattened.update(
                flatten_json(
                    child,
                    new_key,
                    separator,
                )
            )

    elif isinstance(value, list):
        if not value and parent_key:
            flattened[parent_key] = ""

        for index, child in enumerate(value):
            new_key = (
                f"{parent_key}{separator}{index}"
                if parent_key
                else str(index)
            )

            flattened.update(
                flatten_json(
                    child,
                    new_key,
                    separator,
                )
            )

    else:
        flattened[parent_key] = value

    return flattened


def remove_id_column(rows):
    """CSV 저장 전에 최상위 id 컬럼만 제거합니다."""

    return [
        {
            key: value
            for key, value in row.items()
            if key != "id"
        }
        for row in rows
    ]


def load_json_rows():
    """used_car.json을 읽어 CSV 변환용 행 목록으로 만듭니다."""

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        rows = data

    elif (
        isinstance(data, dict)
        and isinstance(data.get("data"), list)
    ):
        rows = data["data"]

    elif isinstance(data, dict):
        rows = [data]

    else:
        raise ValueError(
            "JSON은 list 또는 dictionary 형식이어야 합니다."
        )

    processed_rows = []

    for row in rows:
        if not isinstance(row, dict):
            continue

        # 중첩 구조 복원
        normalized_row = normalize_nested_values(row)

        # CSV 변환용 복사본에만 datetime 변환 적용
        processed_row = preprocess_datetime_fields(
            normalized_row
        )

        processed_rows.append(processed_row)

    return processed_rows


def write_csv(rows):
    """평탄화된 데이터를 CSV 파일로 저장합니다."""

    flattened_rows = [
        flatten_json(row)
        for row in rows
    ]

    # CSV에서만 최상위 id 컬럼 제거
    flattened_rows = remove_id_column(flattened_rows)

    if not flattened_rows:
        print("변환할 데이터가 없습니다.")
        return 0

    fieldnames = list(
        dict.fromkeys(
            key
            for row in flattened_rows
            for key in row
        )
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(flattened_rows)

    print(f"CSV 저장 완료: {OUTPUT_FILE}")
    print(f"저장된 행 수: {len(flattened_rows)}")

    return len(flattened_rows)


def convert_json_to_csv():
    """다른 모듈에서 호출하는 JSON → CSV 변환 함수입니다."""

    rows = load_json_rows()
    return write_csv(rows)


def main():
    """이 파일을 직접 실행할 때 CSV 변환을 시작합니다."""

    convert_json_to_csv()


if __name__ == "__main__":
    main()