import json

from used_car_config import STATE_FILE


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
