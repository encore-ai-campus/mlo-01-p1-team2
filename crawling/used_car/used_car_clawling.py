import json
import time
import requests

from pathlib import Path
from bs4 import BeautifulSoup
from requests.exceptions import RequestException


# 서버 기본 주소
BASE_URL = "http://192.168.0.51:4000"

# 현재 파이썬 파일과 data 폴더 경로
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# JSON 및 상태 파일 저장 위치
OUTPUT_FILE = DATA_DIR / "used_car.json"
STATE_FILE = DATA_DIR / "crawl_state.json"

# API 요청 설정
PAGE_LIMIT = 500
INCREMENTAL_MAX_ITEMS = 500
SERVER_RETRY_SECONDS = 300

# 차량 식별용 필드명
API_LISTING_NUMBER_FIELD = "listingNumber"


# API 키를 서버에서 자동으로 발급받는 함수
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


# API 데이터에 포함된 HTML 태그를 제거하는 함수
def clean_value(value):
    if value is None:
        return ""

    return BeautifulSoup(
        str(value),
        "html.parser"
    ).get_text(" ", strip=True)


# 상태 JSON 파일을 읽는 함수
def get_state():
    if not STATE_FILE.exists():
        return {
            "last_id": "",
            "initial_complete": False
        }

    try:
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

    except (
        json.JSONDecodeError,
        OSError
    ):
        return {
            "last_id": "",
            "initial_complete": False
        }


# 마지막으로 저장된 API ID를 가져오는 함수
def get_last_id():
    return get_state()["last_id"]


# 최초 전체 수집 완료 여부를 확인하는 함수
def is_initial_complete():
    return get_state()["initial_complete"]


# 현재 수집 위치와 완료 여부를 저장하는 함수
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


# 서버에서 차량 데이터 한 페이지를 요청하는 함수
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

            # 호출 제한 시 서버가 허용할 때까지 대기
            if response.status_code == 429:
                retry_after = response.headers.get(
                    "Retry-After"
                )

                wait_seconds = (
                    int(retry_after) + 1
                    if retry_after and retry_after.isdigit()
                    else 10
                )

                print(
                    f"호출 제한입니다. "
                    f"{wait_seconds}초 후 재시도합니다."
                )

                time.sleep(wait_seconds)
                continue

            # API 키 만료 시 새 키로 재요청
            if response.status_code == 403:
                print("API 키가 만료되어 새 키를 발급받습니다.")

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


# 최초 전체 데이터를 페이지 단위로 수집하는 함수
def initial_crawl():
    page_count = 0
    after_id = get_last_id()

    while True:
        payload = request_page(after_id)

        page_data = payload.get("data", [])

        if not page_data:
            print("더 이상 데이터가 없습니다.")
            break

        saved_count = save_to_json(page_data)

        page_count += 1
        after_id = str(page_data[-1]["id"])

        # 페이지마다 현재 위치 저장
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

    # 전체 수집이 정상적으로 끝난 경우에만 완료 처리
    save_state(
        after_id,
        initial_complete=True
    )

    print()
    print("전체 수집 완료")
    print(f"총 페이지: {page_count}")
    print(f"마지막 API ID: {after_id}")
    print(f"저장 위치: {OUTPUT_FILE}")


# 전체 수집 완료 후 새로운 데이터 최대 500건을 수집하는 함수
def incremental_crawl():
    last_id = get_last_id()

    if not last_id:
        print("마지막 ID가 없어 전체 수집을 시작합니다.")
        initial_crawl()
        return

    payload = request_page(last_id)

    page_data = payload.get("data", [])

    if not page_data:
        print("새로운 데이터가 없습니다.")
        return

    page_data = page_data[
        :INCREMENTAL_MAX_ITEMS
    ]

    saved_count = save_to_json(page_data)

    last_id = str(page_data[-1]["id"])

    save_state(
        last_id,
        initial_complete=True
    )

    print()
    print("증분 수집 완료")
    print(f"조회 데이터: {len(page_data)}건")
    print(f"신규 저장 데이터: {saved_count}건")
    print(f"마지막 API ID: {last_id}")
    print(f"저장 위치: {OUTPUT_FILE}")


# 프로그램의 최초 실행 지점을 정의하는 함수
def main():
    if not is_initial_complete():
        print("전체 수집이 완료되지 않았습니다.")
        print("이전 위치부터 전체 수집을 계속합니다.")
        initial_crawl()
    else:
        print("전체 수집이 완료되었습니다.")
        print("증분 수집을 시작합니다.")
        incremental_crawl()


# 이 파일을 직접 실행했을 때만 main() 실행
if __name__ == "__main__":
    main()