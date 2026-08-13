import argparse

from .api_client import fetch_data
from .config import load_settings
from .csv_writer import save_csv
from .transformer import transform_to_long
from .validator import validate_date_range, validate_yyyymm


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="자동차등록대수현황 시도별 데이터를 long CSV로 저장합니다."
    )
    parser.add_argument(
        "--start-dt",
        required=True,
        type=validate_yyyymm,
        help="조회 시작 기준월(YYYYMM)",
    )
    parser.add_argument(
        "--end-dt",
        required=True,
        type=validate_yyyymm,
        help="조회 종료 기준월(YYYYMM)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        validate_date_range(args.start_dt, args.end_dt)
        settings = load_settings()
        payload = fetch_data(settings, args.start_dt, args.end_dt)
        long_rows = transform_to_long(payload, settings.form_id)
        output_path = save_csv(
            rows=long_rows,
            output_dir=settings.output_dir,
            start_dt=args.start_dt,
            end_dt=args.end_dt,
        )
    except (RuntimeError, ValueError) as exc:
        parser.exit(1, f"오류: {exc}\n")

    print(f"저장 완료: {output_path}")
    print(f"행 수: {len(long_rows):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
