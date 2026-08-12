VEHICLE_TYPE_MAP = {
    "승용": "passenger",
    "승합": "van",
    "화물": "truck",
    "특수": "special",
    "총계": "total",
}

USE_TYPE_MAP = {
    "자가용": "private",
    "영업용": "business",
    "관용": "official",
    "계": "total",
}


def to_integer(value) -> int:
    return int(str(value).replace(",", "").strip())


def transform_to_long(
    payload: dict,
    form_id: str,
) -> list[dict]:
    result_data = payload["result_data"]
    form_list = result_data["formList"]
    long_rows: list[dict] = []

    for source_row_no, raw_row in enumerate(form_list, start=1):
        if not isinstance(raw_row, dict):
            continue

        sigungu_name = raw_row.get("시군구")
        if sigungu_name == "계":
            region_level = "시도"
            sigungu_name = None
        else:
            region_level = "시군구"

        for source_measure_key, raw_value in raw_row.items():
            if not isinstance(source_measure_key, str):
                continue
            if ">" not in source_measure_key:
                continue

            vehicle_type_ko, use_type_ko = source_measure_key.split(">", 1)

            long_rows.append(
                {
                    "stat_month": raw_row.get("date"),
                    "region_level": region_level,
                    "sido_name": raw_row.get("시도명"),
                    "sigungu_name": sigungu_name,
                    "vehicle_type": VEHICLE_TYPE_MAP.get(
                        vehicle_type_ko, vehicle_type_ko
                    ),
                    "use_type": USE_TYPE_MAP.get(use_type_ko, use_type_ko),
                    "registration_count": to_integer(raw_value),
                    "unit": result_data.get("unitName"),
                    "source_measure_key": source_measure_key,
                    "source_form_id": form_id,
                    "is_aggregate": int(
                        vehicle_type_ko == "총계" or use_type_ko == "계"
                    ),
                }
            )

    if not long_rows:
        raise RuntimeError("변환할 시도별 데이터가 없습니다.")

    return long_rows
