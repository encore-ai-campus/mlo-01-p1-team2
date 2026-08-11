from __future__ import annotations

import time
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup


@dataclass
class CrawlResult:
    url: str
    html: str
    records: list[dict]


def crawl_faq(
    url: str,
    timeout: int = 20,
    delay_seconds: float = 0.5,
) -> CrawlResult:
    time.sleep(delay_seconds)

    response = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "faq-crawler/0.1 educational-project"
        },
    )
    response.raise_for_status()

    response.encoding = response.apparent_encoding or response.encoding

    soup = BeautifulSoup(response.text, "html.parser")
    records = []

    for article in soup.select("article.faq-item"):
        source_id = (
            article.get("data-faq-id")
            or _text(article.select_one('[data-field="faq-id"]'))
        )

        company = _text(
            article.select_one('[data-field="brand"]')
        )

        category = _text(
            article.select_one('[data-field="category"]')
        )

        question = _text(
            article.select_one("h2")
        )

        answer = _text(
            article.select_one('[data-field="answer"]')
        )

        source_url = article.get("data-source-url")

        if not source_url:
            source_link = article.select_one(
                '[data-field="source"][href]'
            )
            source_url = (
                source_link.get("href")
                if source_link
                else None
            )

        verified_date = article.get("data-reviewed-at")

        if not source_id or not question:
            continue

        records.append(
            {
                "source_id": source_id,
                "company": company,
                "category": category,
                "question": question,
                "answer": answer,
                "source_url": source_url,
                "verified_date": verified_date,
                "page_url": url,
            }
        )

    return CrawlResult(
        url=url,
        html=response.text,
        records=records,
    )


def _text(element) -> str:
    if not element:
        return ""

    return " ".join(
        element.get_text(" ", strip=True).split()
    )