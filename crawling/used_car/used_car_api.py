import time

import requests

from requests.exceptions import RequestException

from used_car_config import (
    API_LISTING_NUMBER_FIELD,
    BASE_URL,
    PAGE_LIMIT,
    SERVER_RETRY_SECONDS,
)


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
