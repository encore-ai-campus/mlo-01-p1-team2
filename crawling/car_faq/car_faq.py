import requests
import json
import time
from bs4 import BeautifulSoup

# 요청 상한선을 브랜드 총 갯수인 8로 제한. 추후 페이지 내 변동사항 발생 시 수정 가능
MAX_REQUESTS = 8

# 질문 답변 내용을 가져올 URL 첨부
category_urls = {
    "Hyundai": "http://192.168.0.51:4000/faqs?brand=hyundai",
    "Kia": "http://192.168.0.51:4000/faqs?brand=kia",
    "Genesis": "http://192.168.0.51:4000/faqs?brand=genesis",
    "Chevrolet": "http://192.168.0.51:4000/faqs?brand=chevrolet",
    "Renault-KOREA": "http://192.168.0.51:4000/faqs?brand=renault-korea",
    "KG-Mobility": "http://192.168.0.51:4000/faqs?brand=kg-mobility",
    "BMW": "http://192.168.0.51:4000/faqs?brand=bmw",
    "Mercedes-Benz": "http://192.168.0.51:4000/faqs?brand=mercedes-benz"
}

# FAQ의 원본 출처인 공식 홈페이지 URL 첨부
official_urls = {
    "Hyundai": "https://www.hyundai.com/kr/ko/e",
    "Kia": "https://www.kia.com/kr",
    "Genesis": "https://www.genesis.com/kr/ko",
    "Chevrolet": "https://www.chevrolet.co.kr/",
    "Renault-KOREA": "https://www.renault.co.kr/ko/main/main.jsp",
    "KG-Mobility": "https://www.kg-mobility.com/",
    "BMW": "https://www.bmw.co.kr/ko/index.html",
    "Mercedes-Benz": "https://www.mercedes-benz.co.kr/passengercars.html"
}

# 크롤링 작동 명령어를 함수로 정의
def collect_faqs():
    all_faqs = {}
    request_count = 0

    for category, url in category_urls.items():
        if request_count >= MAX_REQUESTS:
            break

        # 서버에 요청을 너무 빠르게 보내지 않도록 0.5초의 텀 설정
        time.sleep(0.5)

        # 요청 시 30초간 응답이 없으면 요청을 중단하도록 설정
        response = requests.get(url, timeout=30)
        request_count += 1

        # 서버 응답이 정상인지 확인할 수 있도록 상태 코드 출력
        print(category, "상태 코드:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")
        questions = soup.find_all(
            "h2", # question이 h2로 묶여있어, 해당 부분 가져오기
            attrs={"data-field": "question"}
        )

        answers = soup.find_all(
            "p", # answer가 p로 묶여있어, 해당 부분 가져오기
            attrs={"data-field": "answer"}
        )

        faq_list = []

        for question, answer in zip(questions, answers):

            faq = {
                "Q": question.get_text(" ", strip=True),
                "A": answer.get_text(" ", strip=True),
                "출처": official_urls[category]
                }
            faq_list.append(faq)

        all_faqs[category] = {
            "FAQ 건수": len(faq_list),
            "FAQ 내용": faq_list
        }

        print(category, "FAQ 개수:", len(faq_list))

    # Push 시점 기준 crawling/car_faq/data에 저장되도록 설정되어 있습니다.
    # 아래의 "data/categorized..."의 "data/"를 삭제하면 실행 위치에 파일이 저장됩니다.
    with open("data/categorized_faqs.json", "w", encoding="utf-8") as file:
        json.dump(
            all_faqs,
            file,
            ensure_ascii=False, # ASCII가 아닌 한글로 출력되도록 설정
            indent=2 # 2칸씩 들여쓰기
        )
    # JSON 파일이 저장되었다는 메시지 출력
    print("categorized_faqs.json 파일 저장 완료")

# 함수 실행
collect_faqs()