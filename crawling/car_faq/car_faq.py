import requests
import json
import time
from bs4 import BeautifulSoup
import zlib

# 요청 상한선을 브랜드 총 갯수인 8로 제한. 추후 페이지 내 변동사항 발생 시 수정 가능
MAX_REQUESTS = 8

category_urls = {
    "Hyundai": "http://43.203.233.157/faqs?brand=hyundai",
    "Kia": "http://43.203.233.157/faqs?brand=kia",
    "Genesis": "http://43.203.233.157/faqs?brand=genesis",
    "Chevrolet": "http://43.203.233.157/faqs?brand=chevrolet",
    "Renault-KOREA": "http://43.203.233.157/faqs?brand=renault-korea",
    "KG-Mobility": "http://43.203.233.157/faqs?brand=kg-mobility",
    "BMW": "http://43.203.233.157/faqs?brand=bmw",
    "Mercedes-Benz": "http://43.203.233.157/faqs?brand=mercedes-benz"
}

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

def collect_faqs():
    all_faqs = {}
    request_count = 0

    for category, url in category_urls.items():
        if request_count >= MAX_REQUESTS:
            break

        time.sleep(0.5)

        response = requests.get(url, timeout=30)
        request_count += 1

        print(category, "상태 코드:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")
        questions = soup.find_all(
            "h2",
            attrs={"data-field": "question"}
        )

        answers = soup.find_all(
            "p",
            attrs={"data-field": "answer"}
        )


        faq_list = []

        for question, answer in zip(questions, answers):

            faq = {
                "source_id": zlib.crc32(f'{category}:{question.get_text(" ", strip=True)}'.encode("utf-8")),
                "-Q": question.get_text(" ", strip=True),
                "-A": answer.get_text(" ", strip=True),
                "-출처": official_urls[category]
                }
            faq_list.append(faq)

        all_faqs[category] = {
            "FAQ count": len(faq_list),
            "FAQ detail": faq_list
        }

        print(category, "FAQ 개수:", len(faq_list))

    # Push 시점 기준 crawling/car_faq/data에 저장되도록 설정되어 있습니다.
    # 아래의 "data/categorized..."의 data를 삭제하면 실행 위치에 파일이 저장됩니다.
    with open("/home/ec2-user/1st_project/crawling/car_faq/data/categorized_faqs.json", "w", encoding="utf-8") as file:
        json.dump(
            all_faqs,
            file,
            ensure_ascii=False,
            indent=2
        )
    print("categorized_faqs.json 파일 저장 완료")

collect_faqs()