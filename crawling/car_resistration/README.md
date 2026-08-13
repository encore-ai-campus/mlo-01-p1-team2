
### `src/csv_writer.py`

변환된 딕셔너리 목록을 CSV 파일로 저장합니다. `csv`와 `pathlib`은 Python 표준 라이브러리이므로 별도 설치가 필요하지 않습니다.

```python
CSV_COLUMNS = [...]
```

CSV의 헤더와 컬럼 순서를 정합니다.

```python
output_path.parent.mkdir(parents=True, exist_ok=True)
```

`pathlib.Path.mkdir()`으로 `data/output` 폴더를 만듭니다. 상위 폴더도 함께 만들고, 이미 폴더가 있어도 오류를 발생시키지 않습니다.

```python
with output_path.open("w", encoding="utf-8", newline="") as csv_file:
```

UTF-8 인코딩과 줄바꿈 설정으로 CSV 파일을 쓰기 모드로 엽니다. `with` 블록이 끝나면 파일이 자동으로 닫힙니다.

```python
writer = csv.DictWriter(csv_file, fieldnames=CSV_COLUMNS)
writer.writeheader()
writer.writerows(rows)
```

`csv.DictWriter`가 딕셔너리의 값을 지정된 컬럼 순서에 맞춰 저장합니다.

### `src/main.py`

사용자가 터미널에서 실행하는 시작점입니다.

```python
import argparse
```

Python 표준 라이브러리인 `argparse`로 `--start-dt`, `--end-dt` 명령행 인자를 받습니다.

`main()`은 다음 순서로 각 모듈을 호출합니다.

```text
기준월 인자 받기
→ 기간 검증
→ 설정 읽기
→ API 호출
→ API 응답 검증
→ long format 변환
→ CSV 저장
→ 저장 경로와 행 수 출력
```

파일 마지막의 다음 코드는 파일을 직접 실행했을 때만 `main()`을 실행하도록 합니다.

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

## CSV 컬럼

| 컬럼 | 의미 |
|---|---|
| `stat_month` | 기준월 (`YYYYMM`) |
| `region_level` | 지역 수준 (`시도` 또는 `시군구`) |
| `sido_name` | 시도명 |
| `sigungu_name` | 구·군명, 시도 합계 행은 빈 값 |
| `vehicle_type` | 차량 종류 |
| `use_type` | 사용 용도 |
| `registration_count` | 자동차등록대수 |
| `unit` | 단위, 현재는 `대` |
| `source_measure_key` | API 원본 측정 항목 |
| `source_form_id` | 통계표 ID, 현재는 `5498` |
| `source_row_no` | API 응답에서의 원본 행 번호 |
| `is_aggregate` | 차량 종류 또는 용도가 총계인지 나타내는 값 (`0` 또는 `1`) |

## 원본 데이터와 변환 데이터의 차이

원본 JSON은 한 행에 여러 측정 항목이 있는 wide format입니다.

```text
서울, 강남구, 승용>자가용, 승용>영업용, 화물>자가용, ...
```

변환 후에는 측정 항목 하나가 한 행이 되는 long format입니다.

```text
서울, 강남구, passenger, private, 218199
서울, 강남구, passenger, business, ...
서울, 강남구, truck, private, 13442
```

이 구조에서는 차량 종류, 용도, 지역을 조건으로 사용해 MySQL에서 `WHERE`, `GROUP BY`, `SUM()`을 적용하기 쉽습니다.

## 참고 사항

- 현재 코드는 시도 합계와 구·군 데이터를 모두 CSV에 저장합니다.
- `transformer.py`는 API 원본 JSON을 별도 파일로 보관하지 않습니다. 원본 보관이 필요하면 API 응답 파일을 별도로 저장해야 합니다.
- `.env`와 `__pycache__/`는 Git에 올리지 않는 것이 좋습니다.
- 현재 실행 방식은 상대 import를 사용하므로 프로젝트 루트에서 `python -m src.main`으로 실행해야 합니다.