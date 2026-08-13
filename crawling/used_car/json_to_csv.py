import ast
import csv
import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "used_car.json"
OUTPUT_FILE = BASE_DIR / "data" / "used_car_flattened.csv"


def parse_stringified_structure(value):
    """문자열로 저장된 dict/list를 실제 Python 구조로 복원합니다."""
    if not isinstance(value, str):
        return value

    text = value.strip()
    if not ((text.startswith("{") and text.endswith("}")) or
            (text.startswith("[") and text.endswith("]"))):
        return value

    try:
        parsed = ast.literal_eval(text)
    except (ValueError, SyntaxError):
        return value

    return parsed if isinstance(parsed, (dict, list)) else value


def normalize_nested_values(value):
    """중첩된 dict/list와 문자열 형태의 dict/list를 재귀적으로 정리합니다."""
    parsed = parse_stringified_structure(value)

    if parsed is not value:
        return normalize_nested_values(parsed)
    if isinstance(value, dict):
        return {key: normalize_nested_values(child) for key, child in value.items()}
    if isinstance(value, list):
        return [normalize_nested_values(child) for child in value]
    return value


def flatten_json(value, parent_key="", separator="_"):
    """중첩 JSON을 한 행의 평탄한 dictionary로 변환합니다."""
    flattened = {}

    if isinstance(value, dict):
        if not value and parent_key:
            flattened[parent_key] = ""
        for key, child in value.items():
            new_key = f"{parent_key}{separator}{key}" if parent_key else str(key)
            flattened.update(flatten_json(child, new_key, separator))
    elif isinstance(value, list):
        if not value and parent_key:
            flattened[parent_key] = ""
        for index, child in enumerate(value):
            new_key = f"{parent_key}{separator}{index}" if parent_key else str(index)
            flattened.update(flatten_json(child, new_key, separator))
    else:
        flattened[parent_key] = value

    return flattened


def load_json_rows():
    with INPUT_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and isinstance(data.get("data"), list):
        rows = data["data"]
    elif isinstance(data, dict):
        rows = [data]
    else:
        raise ValueError("JSON은 list 또는 dictionary 형식이어야 합니다.")

    return [normalize_nested_values(row) for row in rows]


def write_csv(rows):
    flattened_rows = [flatten_json(row) for row in rows]
    if not flattened_rows:
        print("변환할 데이터가 없습니다.")
        return

    fieldnames = list(dict.fromkeys(
        key for row in flattened_rows for key in row
    ))
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flattened_rows)

    print(f"CSV 저장 완료: {OUTPUT_FILE}")
    print(f"저장된 행 수: {len(flattened_rows)}")


if __name__ == "__main__":
    write_csv(load_json_rows())