import time

from used_car_api import request_page
from used_car_config import INCREMENTAL_MAX_ITEMS, OUTPUT_FILE
from used_car_state import (
    get_last_id,
    is_initial_complete,
    save_state,
)
from used_car_storage import save_to_json


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
