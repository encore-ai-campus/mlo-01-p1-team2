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