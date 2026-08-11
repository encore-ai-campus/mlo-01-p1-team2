#!/usr/bin/env python3
"""국토교통 통계누리 자동차등록대수현황 시도별 Open API 수집기."""

# .env 파일에 MOLIT_API_KEY=발급받은_인증키 를 설정하시고, 환경변수로 등록하여 사용하셔야 합니다.


from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv


API_URL = "http://stat.molit.go.kr/portal/openapi/service/rest/getList.do"
FORM_ID = "5498"
STYLE_NUM = "2"
DEFAULT_TIMEOUT = 30.0


class MolitApiError(RuntimeError):
    """통계누리 API 호출 또는 응답 처리 중 발생한 오류."""


def validate_yyyymm(value: str) -> str:
    """YYYYMM 형식의 연월을 검증한다."""

    if not re.fullmatch(r"\d{6}", value):
        raise argparse.ArgumentTypeError(
            f"'{value}'는 YYYYMM 형식이어야 합니다. 예: 202606"
        )

    try:
        datetime.strptime(value, "%Y%m")
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"'{value}'는 유효한 연월이 아닙니다."
        ) from exc

    return value


def parse_response_json(response: requests.Response) -> dict[str, Any]:
    """JSON 응답을 파싱한다.

    정상 응답은 JSON이므로 requests의 JSON 파서를 우선 사용한다.
    서버 설정에 따라 JSON이 HTML의 <pre> 안에 반환되는 경우에는
    BeautifulSoup으로 본문을 추출한 뒤 JSON으로 변환한다.
    """

    try:
        payload = response.json()
    except ValueError as first_error:
        soup = BeautifulSoup(response.content, "html.parser")
        pre = soup.find("pre")
        raw_text = pre.get_text() if pre is not None else soup.get_text()

        try:
            payload = json.loads(raw_text.strip())
        except (TypeError, json.JSONDecodeError) as second_error:
            raise MolitApiError("API 응답을 JSON으로 해석하지 못했습니다.") from second_error

        if not payload:
            raise MolitApiError("API 응답이 비어 있습니다.") from first_error

    if not isinstance(payload, dict):
        raise MolitApiError("API 응답의 최상위 형식이 객체가 아닙니다.")

    return payload


def fetch_data(
    api_key: str,
    start_dt: str,
    end_dt: str,
    timeout: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """지정한 기간의 자동차등록대수현황 원자료를 조회한다."""

    params = {
        "key": api_key,
        "form_id": FORM_ID,
        "style_num": STYLE_NUM,
        "start_dt": start_dt,
        "end_dt": end_dt,
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers={"User-Agent": "molit-car-registration-crawler/1.0"},
            timeout=timeout,
        )
    except requests.RequestException as exc:
        raise MolitApiError(f"API 요청에 실패했습니다: {exc}") from exc

    try:
        payload = parse_response_json(response)
    except MolitApiError:
        if response.status_code >= 400:
            raise MolitApiError(
                f"HTTP {response.status_code} 응답을 받았고 JSON 파싱에도 실패했습니다."
            ) from None
        raise

    result_status = payload.get("result_status") or {}
    status_code = str(result_status.get("status_code", ""))
    message = str(result_status.get("message", ""))

    if response.status_code >= 400:
        raise MolitApiError(f"HTTP {response.status_code}: {status_code} {message}".strip())

    if status_code != "INFO-000":
        raise MolitApiError(f"통계누리 API 오류: {status_code} {message}".strip())

    result_data = payload.get("result_data") or {}
    form_list = result_data.get("formList", [])

    if not isinstance(form_list, list):
        raise MolitApiError("응답의 result_data.formList가 배열이 아닙니다.")

    rows = [row for row in form_list if isinstance(row, dict)]
    return payload, rows


def collect_field_names(rows: list[dict[str, Any]]) -> list[str]:
    """행에 등장한 키를 최초 등장 순서대로 모은다."""

    field_names: list[str] = []
    seen: set[str] = set()

    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                field_names.append(key)

    return field_names


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    """원자료 행을 한글 Excel에서 바로 열 수 있는 CSV로 저장한다."""

    if not rows:
        raise MolitApiError("저장할 데이터가 없습니다.")

    field_names = collect_field_names(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=field_names,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_json(
    rows: list[dict[str, Any]],
    payload: dict[str, Any],
    output_path: Path,
) -> None:
    """인증 관련 식별자를 제외하고 원자료를 JSON으로 저장한다."""

    result_data = payload.get("result_data") or {}
    safe_payload = {
        "result_status": payload.get("result_status", {}),
        "result_data": {
            "unitName": result_data.get("unitName"),
            "formName": result_data.get("formName"),
            "formList": rows,
        },
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as json_file:
        json.dump(safe_payload, json_file, ensure_ascii=False, indent=2)
        json_file.write("\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="국토교통 통계누리 자동차등록대수현황 시도별 API 수집"
    )
    parser.add_argument(
        "--start_dt",
        "--start",
        dest="start_dt",
        required=True,
        type=validate_yyyymm,
        help="조회 시작 연월(YYYYMM). 기준월 1개월만 조회하려면 end_dt와 같은 값을 입력",
    )
    parser.add_argument(
        "--end_dt",
        "--end",
        dest="end_dt",
        required=True,
        type=validate_yyyymm,
        help="조회 종료 연월(YYYYMM)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="CSV 저장 경로(기본값: data/car_registration_START_END.csv)",
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        help="선택 사항: 인증 식별자를 제외한 원자료 JSON 저장 경로",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help=f"HTTP 타임아웃(초, 기본값: {DEFAULT_TIMEOUT:g})",
    )
    return parser


def main() -> int:
    load_dotenv()
    parser = build_parser()
    args = parser.parse_args()

    if args.start_dt > args.end_dt:
        parser.error("start_dt는 end_dt보다 클 수 없습니다.")

    if args.timeout <= 0:
        parser.error("timeout은 0보다 커야 합니다.")

    api_key = os.getenv("MOLIT_API_KEY", "").strip()
    if not api_key:
        print(
            "오류: .env 파일에 MOLIT_API_KEY=발급받은_인증키 를 설정하세요.",
            file=sys.stderr,
        )
        return 1

    default_output = Path("data") / (
        f"car_registration_{args.start_dt}_{args.end_dt}.csv"
    )
    output_path = args.output or default_output

    try:
        payload, rows = fetch_data(
            api_key=api_key,
            start_dt=args.start_dt,
            end_dt=args.end_dt,
            timeout=args.timeout,
        )
        write_csv(rows, output_path)

        if args.json_output:
            write_json(rows, payload, args.json_output)
    except MolitApiError as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1

    print(f"수집 완료: {len(rows):,}건")
    print(f"CSV: {output_path}")
    if args.json_output:
        print(f"JSON: {args.json_output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
