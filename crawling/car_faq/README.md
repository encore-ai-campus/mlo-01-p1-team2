# 자동차 브랜드별 FAQ 크롤러

자동차 브랜드별 공식 FAQ 페이지에서 질문과 답변을 수집하고, JSON 파일로 저장하는 프로그램이다.

## 주요 기능

- 브랜드별 FAQ 페이지 수집
- 질문과 답변 추출
- 브랜드별 FAQ 건수 구분
- 공식 홈페이지 주소를 `출처`로 저장
- 브랜드별(`category_urls`) 등록된 FAQ 페이지만 요청
- 요청 횟수 상한(`MAX_REQUESTS`) 설정
- 요청 간 0.5초 대기
- 수집 결과를 한글 JSON 형식으로 저장

## 지원 브랜드

- Hyundai
- Kia
- Genesis
- Chevrolet
- Renault-KOREA
- KG-Mobility
- BMW
- Mercedes-Benz

## 폴더 구조

crawling/car_faq/
├── car_faq.py
└── data/
    └── categorized_faqs.json

## 사용 라이브러리

- Python 3
- `requests`
- `beautifulsoup4`

### 설치

```bash
pip install requests beautifulsoup4
```

## 실행 방법

python car_faq.py (해당 파일이 있는 폴더에서 실행한다.)

## 수집 방식

1. 브랜드별 FAQ URL을 `category_urls`에 등록한다.
2. `requests`로 FAQ 페이지를 요청한다.
3. BeautifulSoup으로 질문과 답변을 추출한다다.
4. 브랜드별 FAQ 건수와 내용을 정리한다다.
5. `data/categorized_faqs.json`에 저장한다다.

질문과 답변은 다음 HTML 속성을 기준으로 찾는다.

```html
<h2 data-field="question">질문</h2>
<p data-field="answer">답변</p>
```

## 요청 제한

한 번 실행할 때 요청할 수 있는 최대 FAQ 페이지 수이다.
```python
MAX_REQUESTS = 8
```

요청 사이에는 다음과 같이 0.5초 대기한다.
```python
time.sleep(0.5)
```

또한 한 요청은 최대 30초까지 기다린다.
```python
requests.get(url, timeout=30)
```

## 저장 형식

결과 파일은 `data/categorized_faqs.json`에 저장된다.

```json
{
  "BMW": {
    "FAQ 건수": 1,
    "FAQ 내용": [
      {
        "Q": "BMW 차량의 리콜 대상 여부는 어떻게 확인하나요?",
        "A": "공식 홈페이지에서 확인할 수 있습니다.",
        "출처": "https://www.bmw.com"
      }
    ]
  }
}
```

## 데이터 출처

각 FAQ에는 해당 브랜드 공식 홈페이지 주소를 저장한다. 실제 사용시에는 각 사이트의 이용약관, 저작권, 출처 표시 조건을 확인해야 한다.

## 주의사항

- 대상 서버가 실행 중이고 접근 가능한지 확인한다.
- `category_urls`에 등록된 주소만 사용한다.
- 서버에 과도한 요청을 보내지 않는다.
- JSON 파일은 프로그램 실행 시 새 수집 결과로 덮어써진다.