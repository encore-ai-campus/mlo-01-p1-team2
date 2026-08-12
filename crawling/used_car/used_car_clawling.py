import csv
import json
import time
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


BASE_URL = "http://192.168.0.51:4000"

BASE_DIR = Path(__file__).resolve().parent

# CSV와 상태 파일을 같은 data 폴더에 저장
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = DATA_DIR / "used_car.csv"
STATE_FILE = DATA_DIR / "crawl_state.json"

PAGE_LIMIT = 500
INCREMENTAL_MAX_ITEMS = 500
SERVER_RETRY_SECONDS = 300

API_LISTING_NUMBER_FIELD = "listingNumber"
CSV_LISTING_NUMBER_FIELD = "listingNumber"


def get_api_headers():
    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/public-key",
                headers={
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0"
                },
                timeout=20
            )

            response.raise_for_status()

            key_info = response.json()
            api_key = key_info["data"]["current"]["api_key"]

            return {
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0",
                "X-API-Key": api_key
            }

        except RequestException as error:
            print()
            print("API 키 서버에 연결할 수 없습니다.")
            print(f"오류 내용: {error}")
            print("5분 후 다시 시도합니다.")
            print()

            time.sleep(SERVER_RETRY_SECONDS)


def clean_value(value):
    if value is None:
        return ""

    return BeautifulSoup(
        str(value),
        "html.parser"
    ).get_text(" ", strip=True)


def get_state():
    if not STATE_FILE.exists():
        return {
            "last_id": "",
            "initial_complete": False
        }

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        state = json.load(file)

    return {
        "last_id": str(state.get("last_id", "")),
        "initial_complete": bool(
            state.get("initial_complete", False)
        )
    }


def get_last_id():
    return get_state()["last_id"]


def is_initial_complete():
    return get_state()["initial_complete"]


def save_state(last_id, initial_complete=False):
    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            {
                "last_id": str(last_id),
                "initial_complete": initial_complete
            },
            file,
            ensure_ascii=False,
            indent=2
        )


def get_existing_listing_numbers():
    existing_numbers = set()

    if not OUTPUT_FILE.exists():
        return existing_numbers

    with open(
        OUTPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            listing_number = row.get(
                CSV_LISTING_NUMBER_FIELD
            )

            if listing_number:
                existing_numbers.add(
                    str(listing_number)
                )

    return existing_numbers


def get_existing_fieldnames():
    if not OUTPUT_FILE.exists():
        return None

    with open(
        OUTPUT_FILE,
        "r",
        newline="",
        encoding="utf-8-sig"
    ) as file:
        reader = csv.DictReader(file)
        return reader.fieldnames


def request_page(after_id):
    while True:
        try:
            headers = get_api_headers()

            response = requests.get(
                f"{BASE_URL}/api/v1/cars/cursor",
                params={
                    "after_id": after_id,
                    "limit": PAGE_LIMIT
                },
                headers=headers,
                timeout=20
            )

            print("요청 주소:", response.url)
            print("상태 코드:", response.status_code)

            if response.status_code == 429:
                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after and retry_after.isdigit():
                    wait_seconds = int(retry_after) + 1
                else:
                    wait_seconds = 10

                print(
                    f"호출 제한입니다. "
                    f"{wait_seconds}초 후 재시도합니다."
                )

                time.sleep(wait_seconds)
                continue

            if response.status_code == 403:
                print("API 키가 만료되었습니다.")
                print("새 API 키로 다시 요청합니다.")

                headers = get_api_headers()

                response = requests.get(
                    f"{BASE_URL}/api/v1/cars/cursor",
                    params={
                        "after_id": after_id,
                        "limit": PAGE_LIMIT
                    },
                    headers=headers,
                    timeout=20
                )

            response.raise_for_status()

            payload = response.json()
            data = payload.get("data", [])

            if (
                data
                and API_LISTING_NUMBER_FIELD not in data[0]
            ):
                print("현재 API 응답 필드:")
                print(data[0].keys())

                raise KeyError(
                    "API 응답에 listingNumber 필드가 없습니다."
                )

            return payload

        except RequestException as error:
            print()
            print("서버가 다운되었거나 네트워크가 끊겼습니다.")
            print(f"오류 내용: {error}")
            print("현재 위치에서 5분 후 다시 시도합니다.")
            print()

            time.sleep(SERVER_RETRY_SECONDS)


def save_to_csv(items, file_mode):
    if not items:
        return 0

    existing_numbers = (
        get_existing_listing_numbers()
    )

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
            CSV_LISTING_NUMBER_FIELD
        ] = listing_number

        new_items.append(cleaned_item)
        existing_numbers.add(listing_number)

    if not new_items:
        print("새로 저장할 데이터가 없습니다.")
        return 0

    if file_mode == "w":
        fieldnames = sorted({
            key
            for item in new_items
            for key in item.keys()
        })
    else:
        fieldnames = get_existing_fieldnames()

        if not fieldnames:
            fieldnames = sorted({
                key
                for item in new_items
                for key in item.keys()
            })

    file_exists = OUTPUT_FILE.exists()

    with open(
        OUTPUT_FILE,
        file_mode,
        newline="",
        encoding="utf-8-sig"
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore"
        )

        if file_mode == "w" or not file_exists:
            writer.writeheader()

        writer.writerows(new_items)

    return len(new_items)


def initial_crawl():
    page_count = 0
    after_id = get_last_id()

    file_mode = "a" if OUTPUT_FILE.exists() else "w"

    while True:
        payload = request_page(after_id)

        page_data = payload.get(
            "data",
            []
        )

        if not page_data:
            print("더 이상 데이터가 없습니다.")
            break

        saved_count = save_to_csv(
            page_data,
            file_mode
        )

        file_mode = "a"
        page_count += 1

        after_id = str(
            page_data[-1]["id"]
        )

        # 매 페이지마다 data 폴더 안에 상태 저장
        save_state(
            after_id,
            initial_complete=False
        )

        print(
            f"{page_count}페이지 완료 - "
            f"조회 {len(page_data)}건 / "
            f"신규 저장 {saved_count}건"
        )

        next_path = payload.get(
            "links",
            {}
        ).get("next")

        if not next_path:
            break

        time.sleep(1)

    save_state(
        after_id,
        initial_complete=True
    )

    print()
    print("전체 수집 완료")
    print(f"총 페이지: {page_count}")
    print(f"마지막 API ID: {after_id}")
    print(f"CSV 저장 위치: {OUTPUT_FILE}")
    print(f"상태 저장 위치: {STATE_FILE}")


def incremental_crawl():
    last_id = get_last_id()

    if not last_id:
        print("마지막 ID가 없어 전체 수집을 시작합니다.")
        initial_crawl()
        return

    payload = request_page(last_id)

    page_data = payload.get(
        "data",
        []
    )

    if not page_data:
        print("새로운 데이터가 없습니다.")
        return

    page_data = page_data[
        :INCREMENTAL_MAX_ITEMS
    ]

    saved_count = save_to_csv(
        page_data,
        "a"
    )

    last_id = str(
        page_data[-1]["id"]
    )

    save_state(
        last_id,
        initial_complete=True
    )

    print()
    print("증분 수집 완료")
    print(f"조회 데이터: {len(page_data)}건")
    print(f"신규 저장 데이터: {saved_count}건")
    print(f"마지막 API ID: {last_id}")
    print(f"CSV 저장 위치: {OUTPUT_FILE}")


if not is_initial_complete():
    print("전체 수집이 완료되지 않았습니다.")
    print("이전 위치부터 전체 수집을 계속합니다.")

    initial_crawl()

else:
    print("전체 수집이 완료되었습니다.")
    print("증분 수집을 시작합니다.")

    incremental_crawl()