import ast
import csv
import json

from pathlib import Path


# 현재 파이썬 파일이 있는 폴더
BASE_DIR = Path(__file__).resolve().parent

# 입력 JSON과 출력 파일 경로
DATA_DIR = BASE_DIR / "data"
INPUT_FILE = DATA_DIR / "used_car.json"

# wide 형식 CSV
WIDE_OUTPUT_FILE = DATA_DIR / "used_car_flattened.csv"

# wide를 long candidate로 변환한 CSV
LONG_OUTPUT_FILE = DATA_DIR / "used_car_long_candidate.csv"

# 검증 결과 파일
VALIDATION_OUTPUT_FILE = DATA_DIR / "used_car_validation.json"

# 기존 코드와의 호환을 위한 출력 파일 변수
OUTPUT_FILE = WIDE_OUTPUT_FILE

# long 형식에서 차량 식별자로 유지할 열
# title이나 createdAt도 식별 정보로 유지하려면 여기에 추가합니다.
ID_COLUMNS = (
    "id",
    "listingNumber",
)

# 값이 숫자여야 하는 주요 컬럼
NUMERIC_COLUMNS = {
    "id",
    "modelYear",
    "mileageKm",
    "price",
    "displacementCc",
    "accidentCount",
    "ownerChangeCount",
}


def parse_stringified_structure(value):
    """
    문자열로 저장된 dictionary/list를 실제 구조로 변환합니다.

    예:
    "{'id': 2, 'name': '기아'}"
    -> {"id": 2, "name": "기아"}

    API 데이터가 정상적인 dict/list라면 그대로 반환합니다.
    일반 문자열은 변환하지 않습니다.
    """
    if not isinstance(value, str):
        return value

    text = value.strip()

    if not text:
        return value

    is_dict_text = (
        text.startswith("{")
        and text.endswith("}")
    )
    is_list_text = (
        text.startswith("[")
        and text.endswith("]")
    )

    if not (is_dict_text or is_list_text):
        return value

    try:
        parsed_value = ast.literal_eval(text)
    except (
        ValueError,
        SyntaxError
    ):
        return value

    if isinstance(parsed_value, (dict, list)):
        return parsed_value

    return value


def normalize_nested_values(value):
    """
    문자열로 변환된 중첩 dictionary/list를 복원하고
    내부 값까지 재귀적으로 정리합니다.
    """
    parsed_value = parse_stringified_structure(value)

    if parsed_value is not value:
        return normalize_nested_values(parsed_value)

    if isinstance(value, dict):
        return {
            key: normalize_nested_values(child_value)
            for key, child_value in value.items()
        }

    if isinstance(value, list):
        return [
            normalize_nested_values(child_value)
            for child_value in value
        ]

    return value


def flatten_json(value, parent_key="", separator="_"):
    """
    중첩된 dictionary와 list를 wide 형식의 한 단계 dictionary로
    평탄화합니다.
    """
    flattened = {}

    if isinstance(value, dict):
        if not value and parent_key:
            flattened[parent_key] = ""

        for key, child_value in value.items():
            new_key = (
                f"{parent_key}{separator}{key}"
                if parent_key
                else str(key)
            )

            flattened.update(
                flatten_json(
                    child_value,
                    new_key,
                    separator
                )
            )

    elif isinstance(value, list):
        if not value and parent_key:
            flattened[parent_key] = ""

        for index, child_value in enumerate(value):
            new_key = (
                f"{parent_key}{separator}{index}"
                if parent_key
                else str(index)
            )

            flattened.update(
                flatten_json(
                    child_value,
                    new_key,
                    separator
                )
            )

    else:
        flattened[parent_key] = value

    return flattened


def load_json_data():
    """used_car.json을 읽어 차량 행 목록으로 변환합니다."""
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"입력 파일을 찾을 수 없습니다: {INPUT_FILE}"
        )

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    if isinstance(data, list):
        rows = data

    elif isinstance(data, dict):
        if isinstance(data.get("data"), list):
            rows = data["data"]
        else:
            rows = [data]

    else:
        raise ValueError(
            "JSON 데이터는 list 또는 dictionary 형식이어야 합니다."
        )

    return [
        normalize_nested_values(row)
        for row in rows
    ]


def get_fieldnames(rows):
    """행 목록에서 전체 컬럼명을 중복 없이 수집합니다."""
    fieldnames = []

    for row in rows:
        for key in row.keys():
            key = str(key)

            if key not in fieldnames:
                fieldnames.append(key)

    return fieldnames


def write_csv(rows, output_file, fieldnames):
    """지정된 행과 컬럼으로 CSV 파일을 새로 작성합니다."""
    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        writer.writeheader()
        writer.writerows(rows)


def save_flattened_csv(rows):
    """
    JSON을 중첩 구조가 없는 wide CSV로 저장합니다.

    반환값:
    wide 형식으로 평탄화된 행 목록
    """
    flattened_rows = [
        flatten_json(row)
        for row in rows
    ]

    if not flattened_rows:
        print("저장할 데이터가 없습니다.")
        return []

    fieldnames = get_fieldnames(flattened_rows)

    write_csv(
        flattened_rows,
        WIDE_OUTPUT_FILE,
        fieldnames
    )

    print("JSON 평탄화 및 wide CSV 저장 완료")
    print(f"wide 데이터: {len(flattened_rows)}건")
    print(f"저장 위치: {WIDE_OUTPUT_FILE}")

    return flattened_rows


def convert_wide_to_long(flattened_rows):
    """
    wide 행을 long candidate 형식으로 변환합니다.

    식별자 컬럼은 그대로 유지하고,
    나머지 컬럼은 measure_name과 measure_value 행으로 펼칩니다.
    """
    if not flattened_rows:
        return []

    fieldnames = get_fieldnames(flattened_rows)
    measure_columns = [
        field
        for field in fieldnames
        if field not in ID_COLUMNS
    ]

    long_rows = []

    for row in flattened_rows:
        identifiers = {
            column: row.get(column, "")
            for column in ID_COLUMNS
        }

        for measure_name in measure_columns:
            long_rows.append(
                {
                    **identifiers,
                    "measure_name": measure_name,
                    "measure_value": row.get(
                        measure_name,
                        ""
                    )
                }
            )

    return long_rows


def save_long_csv(long_rows):
    """long candidate 데이터를 CSV로 저장합니다."""
    if not long_rows:
        print("저장할 long 데이터가 없습니다.")
        return

    fieldnames = [
        *ID_COLUMNS,
        "measure_name",
        "measure_value"
    ]

    write_csv(
        long_rows,
        LONG_OUTPUT_FILE,
        fieldnames
    )

    print("wide → long candidate 변환 완료")
    print(f"long 데이터: {len(long_rows)}건")
    print(f"저장 위치: {LONG_OUTPUT_FILE}")


def validate_wide_rows(flattened_rows):
    """wide 데이터의 필수값, 중복, 숫자 컬럼을 검증합니다."""
    errors = []
    warnings = []
    fieldnames = get_fieldnames(flattened_rows)

    for required_column in ID_COLUMNS:
        if required_column not in fieldnames:
            errors.append(
                f"필수 컬럼이 없습니다: {required_column}"
            )

    listing_numbers = set()

    for row_number, row in enumerate(
        flattened_rows,
        start=1
    ):
        for required_column in ID_COLUMNS:
            value = row.get(required_column, "")

            if value is None or str(value).strip() == "":
                errors.append(
                    f"{row_number}행의 "
                    f"{required_column} 값이 비어 있습니다."
                )

        listing_number = str(
            row.get("listingNumber", "")
        ).strip()

        if listing_number:
            if listing_number in listing_numbers:
                errors.append(
                    f"listingNumber 중복: {listing_number}"
                )

            listing_numbers.add(listing_number)

        for column in NUMERIC_COLUMNS:
            if column not in row:
                continue

            value = row.get(column, "")

            if value is None or str(value).strip() == "":
                continue

            try:
                float(str(value).replace(",", ""))
            except ValueError:
                errors.append(
                    f"{row_number}행의 {column} 값이 "
                    f"숫자가 아닙니다: {value}"
                )

    if not flattened_rows:
        warnings.append("wide 데이터가 비어 있습니다.")

    return {
        "errors": errors,
        "warnings": warnings
    }


def validate_long_rows(long_rows):
    """long candidate의 필수 컬럼과 중복 구조를 검증합니다."""
    errors = []
    warnings = []

    required_columns = [
        *ID_COLUMNS,
        "measure_name",
        "measure_value"
    ]

    if long_rows:
        fieldnames = get_fieldnames(long_rows)

        for required_column in required_columns:
            if required_column not in fieldnames:
                errors.append(
                    f"long 필수 컬럼이 없습니다: "
                    f"{required_column}"
                )

    long_keys = set()

    for row_number, row in enumerate(
        long_rows,
        start=1
    ):
        for required_column in required_columns:
            value = row.get(required_column, "")

            if value is None or str(value).strip() == "":
                errors.append(
                    f"long {row_number}행의 "
                    f"{required_column} 값이 비어 있습니다."
                )

        listing_number = str(
            row.get("listingNumber", "")
        ).strip()
        measure_name = str(
            row.get("measure_name", "")
        ).strip()

        if listing_number and measure_name:
            long_key = (
                listing_number,
                measure_name
            )

            if long_key in long_keys:
                errors.append(
                    "long 데이터 중복: "
                    f"{listing_number} / {measure_name}"
                )

            long_keys.add(long_key)

    if not long_rows:
        warnings.append("long candidate가 비어 있습니다.")

    return {
        "errors": errors,
        "warnings": warnings
    }


def validate_data(flattened_rows, long_rows):
    """wide와 long 데이터의 검증 결과를 하나로 만듭니다."""
    wide_result = validate_wide_rows(flattened_rows)
    long_result = validate_long_rows(long_rows)

    errors = [
        *wide_result["errors"],
        *long_result["errors"]
    ]

    warnings = [
        *wide_result["warnings"],
        *long_result["warnings"]
    ]

    return {
        "valid": len(errors) == 0,
        "wide_row_count": len(flattened_rows),
        "long_row_count": len(long_rows),
        "errors": errors,
        "warnings": warnings
    }


def save_validation_report(report):
    """검증 결과를 JSON 파일로 저장합니다."""
    with open(
        VALIDATION_OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=2
        )


def convert_json_to_csv():
    """
    JSON 파싱부터 wide 저장, long 변환, 검증까지
    전체 변환 과정을 실행합니다.
    """
    rows = load_json_data()

    # 1. JSON을 wide 형식으로 평탄화하고 저장
    flattened_rows = save_flattened_csv(rows)

    # 2. wide 형식을 long candidate로 변환하고 저장
    long_rows = convert_wide_to_long(flattened_rows)
    save_long_csv(long_rows)

    # 3. wide와 long 데이터 검증
    validation_report = validate_data(
        flattened_rows,
        long_rows
    )
    save_validation_report(validation_report)

    print()
    print("검증 결과:", "성공" if validation_report["valid"] else "실패")
    print(f"검증 결과 저장 위치: {VALIDATION_OUTPUT_FILE}")

    if validation_report["errors"]:
        print("검증 오류:")

        for error in validation_report["errors"]:
            print(f"- {error}")

    return validation_report


def main():
    """이 파일을 직접 실행했을 때 전체 변환을 실행합니다."""
    convert_json_to_csv()


if __name__ == "__main__":
    main()
