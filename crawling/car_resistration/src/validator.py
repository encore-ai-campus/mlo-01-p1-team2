import re
from datetime import datetime


def validate_yyyymm(value: str) -> str:
    if not re.fullmatch(r"\d{6}", value):
        raise ValueError("기준월은 YYYYMM 형식이어야 합니다.")

    try:
        datetime.strptime(value, "%Y%m")
    except ValueError as exc:
        raise ValueError(f"유효하지 않은 기준월입니다: {value}") from exc

    return value


def validate_date_range(start_dt: str, end_dt: str) -> None:
    if start_dt > end_dt:
        raise ValueError("start-dt는 end-dt보다 늦을 수 없습니다.")


def validate_api_payload(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise RuntimeError("API 응답의 최상위 형식이 객체가 아닙니다.")

    result_status = payload.get("result_status")
    if not isinstance(result_status, dict):
        raise RuntimeError("API 응답에 result_status가 없습니다.")

    status_code = result_status.get("status_code")
    if status_code != "INFO-000":
        message = result_status.get("message", "알 수 없는 오류")
        raise RuntimeError(f"API 오류: {message}")

    result_data = payload.get("result_data")
    if not isinstance(result_data, dict):
        raise RuntimeError("API 응답에 result_data가 없습니다.")

    if not isinstance(result_data.get("formList"), list):
        raise RuntimeError("API 응답에 formList가 없습니다.")

    return payload
