import csv
from pathlib import Path


CSV_COLUMNS = [
    "stat_month",
    "region_level",
    "sido_name",
    "sigungu_name",
    "vehicle_type",
    "use_type",
    "registration_count",
    "unit",
    "source_measure_key",
    "source_form_id",
    "source_row_no",
    "is_aggregate",
]


def save_csv(
    rows: list[dict],
    output_dir: Path,
    start_dt: str,
    end_dt: str,
) -> Path:
    output_path = output_dir / (
        f"car_registration_long_{start_dt}_{end_dt}.csv"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return output_path
