import requests

from .config import Settings
from .validator import validate_api_payload


def fetch_data(
    settings: Settings,
    start_dt: str,
    end_dt: str,
) -> dict:
    params = {
        "key": settings.api_key,
        "form_id": settings.form_id,
        "style_num": settings.style_num,
        "start_dt": start_dt,
        "end_dt": end_dt,
    }

    try:
        response = requests.get(
            settings.api_url,
            params=params,
            timeout=settings.request_timeout,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"API 요청에 실패했습니다: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError("API 응답을 JSON으로 읽을 수 없습니다.") from exc

    return validate_api_payload(payload)
