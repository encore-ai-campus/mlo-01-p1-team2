import json

from bs4 import BeautifulSoup

from used_car_config import API_LISTING_NUMBER_FIELD, OUTPUT_FILE


# API 데이터에 포함된 HTML 태그를 제거하는 함수
def clean_value(value):
    if value is None:
        return ""

    return BeautifulSoup(
        str(value),
        "html.parser"
    ).get_text(" ", strip=True)


# 기존 JSON 데이터를 읽는 함수
def load_existing_data():
    if not OUTPUT_FILE.exists():
        return []

    try:
        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except (
        json.JSONDecodeError,
        OSError
    ):
        return []


# 새 데이터를 기존 데이터와 합쳐 JSON으로 저장하는 함수
def save_to_json(items):
    if not items:
        return 0

    existing_data = load_existing_data()

    existing_numbers = {
        str(item.get(API_LISTING_NUMBER_FIELD))
        for item in existing_data
        if item.get(API_LISTING_NUMBER_FIELD) is not None
    }

    new_items = []

    for item in items:
        listing_number = item.get(
            API_LISTING_NUMBER_FIELD
        )

        if not listing_number:
            print("listingNumber가 없어 건너뜁니다.")
            continue

        listing_number = str(listing_number)

        if listing_number in existing_numbers:
            continue

        cleaned_item = {
            key: clean_value(value)
            for key, value in item.items()
        }

        cleaned_item[
            API_LISTING_NUMBER_FIELD
        ] = listing_number

        new_items.append(cleaned_item)
        existing_numbers.add(listing_number)

    if not new_items:
        print("새로 저장할 데이터가 없습니다.")
        return 0

    existing_data.extend(new_items)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            existing_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    return len(new_items)
