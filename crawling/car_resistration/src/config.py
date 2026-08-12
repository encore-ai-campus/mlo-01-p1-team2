import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    api_url: str
    api_key: str
    form_id: str
    style_num: str
    request_timeout: int
    output_dir: Path


def load_settings() -> Settings:
    load_dotenv()

    api_key = os.getenv("MOLIT_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(".env에 MOLIT_API_KEY가 설정되어 있지 않습니다.")

    return Settings(
        api_url=(
            "http://stat.molit.go.kr/portal/openapi/"
            "service/rest/getList.do"
        ),
        api_key=api_key,
        form_id="5498",
        style_num="2",
        request_timeout=30,
        output_dir=Path("data") / "output",
    )
