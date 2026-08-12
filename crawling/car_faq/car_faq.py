import requests
import time
import json
from bs4 import BeautifulSoup


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

def collect_faqs():
    all_faqs = {}

    for category, url in category_urls.items():
        response = requests.get(url, timeout=10)
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
                "Q": question.get_text(" ", strip=True),
                "A": answer.get_text(" ", strip=True)
            }

            faq_list.append(faq)

        all_faqs[category] = {
            "FAQ 건수": len(faq_list),
            "FAQ 내용": faq_list
        }

        print(category, "FAQ 개수:", len(faq_list))

    # Push 시점 기준 crawling/car_faq/data에 저장되도록 설정되어 있습니다.
    # 아래의 "data/categorized..."의 data를 삭제하면 실행 위치에 파일이 저장됩니다.
    with open("data/categorized_faqs.json", "w", encoding="utf-8") as file:
        json.dump(
            all_faqs,
            file,
            ensure_ascii=False,
            indent=2
        )
    print("categorized_faqs.json 파일 저장 완료")

collect_faqs()