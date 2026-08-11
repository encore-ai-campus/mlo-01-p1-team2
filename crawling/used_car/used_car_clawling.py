import csv
import json
import time
import requests

from pathlib import Path
from bs4 import BeautifulSoup


# =====================================
# 사용자 설정
# =====================================

BASE_URL = "http://192.168.0.51:4000"

# 실제 API 키 입력
API_KEY = "ucar_v1_993d86bd92a2259a_xnMJx16Nvr5DwhW13apEe0Q4RcbgGTXFm5NviLkpJNA"

BASE_DIR = Path(__file__).resolve().parent

# data 폴더 생성
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# CSV 저장 위치
OUTPUT_FILE = DATA_DIR / "used_car.csv"

# 마지막 수집 ID 저장 위치
STATE_FILE = BASE_DIR / "crawl_state.json"

PAGE_LIMIT = 500
INCREMENTAL_MAX_ITEMS = 500

# API 응답 필드명
API_LISTING_NUMBER_FIELD = "listingNumber"

# CSV에 저장할 고유번호 컬럼명
CSV_LISTING_NUMBER_FIELD = "data-listing-number"


# =====================================
# 요청 설정
# =====================================

headers = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
    "X-API-Key": API_KEY
}


# =====================================
# 데이터 정리
# =====================================

def clean_value(value):
    if value is None:
        return ""

    return BeautifulSoup(
        str(value),
        "html.parser"
    ).get_text(" ", strip=True)


# =====================================
# 마지막 API ID 관리
# =====================================

def get_last_id():
    if not STATE_FILE.exists():
        return ""

    with open(
        STATE_FILE,
        "r",
        encoding="utf-8"
    ) as file:
        state = json.load(file)

    return str(
        state.get("last_id", "")
    )


def save_last_id(last_id):
    with open(
        STATE_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            {
                "last_id": str(last_id)
            },
            file,
            ensure_ascii=False,
            indent=2
        )


# =====================================
# 기존 CSV 고유번호 확인
# =====================================

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


# =====================================
# API 요청
# =====================================

def request_page(after_id):
    while True:
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

        # 호출 제한
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

        # API 키 오류
        if response.status_code == 403:
            raise RuntimeError(
                "API 키가 올바르지 않거나 만료되었습니다."
            )

        response.raise_for_status()

        payload = response.json()
        data = payload.get("data", [])

        # API 응답 필드 확인
        if (
            data
            and API_LISTING_NUMBER_FIELD not in data[0]
        ):
            print("현재 API 응답 필드 목록:")
            print(data[0].keys())

            raise KeyError(
                f"API 응답에 "
                f"'{API_LISTING_NUMBER_FIELD}' "
                "필드가 없습니다."
            )

        return payload


# =====================================
# 기존 CSV 헤더 확인
# =====================================

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


# =====================================
# CSV 저장
# =====================================

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
            print(
                "listingNumber가 없는 데이터는 "
                "건너뜁니다."
            )
            continue

        listing_number = str(listing_number)

        # 이미 저장된 데이터는 건너뜀
        if listing_number in existing_numbers:
            continue

        cleaned_item = {
            key: clean_value(value)
            for key, value in item.items()
        }

        # API 원본 필드 제거
        cleaned_item.pop(
            API_LISTING_NUMBER_FIELD,
            None
        )

        # CSV용 고유번호 필드 추가
        cleaned_item[
            CSV_LISTING_NUMBER_FIELD
        ] = listing_number

        new_items.append(cleaned_item)
        existing_numbers.add(listing_number)

    if not new_items:
        print("새로 저장할 데이터가 없습니다.")
        return 0

    # 최초 실행 시 CSV 헤더 생성
    if file_mode == "w":
        fieldnames = sorted({
            key
            for item in new_items
            for key in item.keys()
        })

    # 이후 실행 시 기존 CSV 헤더 사용
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

        for item in new_items:
            writer.writerow(item)

    return len(new_items)


# =====================================
# 최초 실행: 전체 데이터 수집
# =====================================

def initial_crawl():
    all_data = []
    after_id = ""
    page_count = 0

    while True:
        payload = request_page(after_id)

        page_data = payload.get(
            "data",
            []
        )

        if not page_data:
            print("더 이상 데이터가 없습니다.")
            break

        all_data.extend(page_data)
        page_count += 1

        print(
            f"{page_count}페이지 완료 - "
            f"{len(page_data)}건 추가 / "
            f"누적 {len(all_data)}건"
        )

        # 마지막 데이터의 ID 사용
        after_id = str(
            page_data[-1]["id"]
        )

        next_path = payload.get(
            "links",
            {}
        ).get("next")

        if not next_path:
            break

        time.sleep(1)

    saved_count = save_to_csv(
        all_data,
        "w"
    )

    # 다음 실행을 위한 마지막 ID 저장
    if all_data:
        save_last_id(
            all_data[-1]["id"]
        )

    print()
    print("전체 초기 수집 완료")
    print(f"총 페이지: {page_count}")
    print(f"총 수집 데이터: {len(all_data)}건")
    print(f"새로 저장된 데이터: {saved_count}건")
    print(f"마지막 API ID: {after_id}")
    print(f"저장 위치: {OUTPUT_FILE}")


# =====================================
# 이후 실행: 최대 500건 수집
# =====================================

def incremental_crawl():
    last_id = get_last_id()

    if not last_id:
        print("마지막 ID가 없습니다.")
        print("전체 초기 수집을 시작합니다.")
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

    # 이후 실행은 최대 500건만 처리
    page_data = page_data[
        :INCREMENTAL_MAX_ITEMS
    ]

    saved_count = save_to_csv(
        page_data,
        "a"
    )

    # 다음 실행을 위한 마지막 ID 저장
    save_last_id(
        page_data[-1]["id"]
    )

    print()
    print("증분 수집 완료")
    print(f"조회 데이터: {len(page_data)}건")
    print(f"새로 저장된 데이터: {saved_count}건")
    print(
        f"마지막 API ID: "
        f"{page_data[-1]['id']}"
    )
    print(f"저장 위치: {OUTPUT_FILE}")


# =====================================
# 프로그램 실행
# =====================================

if (
    not OUTPUT_FILE.exists()
    or not STATE_FILE.exists()
):
    print("최초 실행입니다.")
    print("전체 데이터를 수집합니다.")
    initial_crawl()
else:
    print("증분 실행입니다.")
    print("최대 500건을 수집합니다.")
    incremental_crawl()