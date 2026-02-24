#!/usr/bin/env python3
"""경제 뉴스 + 종목 리포트 수집/번역 도구."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/123.0.0.0 Safari/537.36"
)
HEADERS = {"User-Agent": USER_AGENT}


@dataclass
class Item:
    title: str
    source: str
    date: str
    url: str
    summary: str


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def translate_to_korean(text: str) -> str:
    from deep_translator import GoogleTranslator

    text = clean_text(text)
    if not text:
        return ""

    hangul_count = len(re.findall(r"[가-힣]", text))
    if hangul_count > max(8, len(text) // 3):
        return text

    try:
        return GoogleTranslator(source="auto", target="ko").translate(text)
    except Exception:
        return text


def fetch_economic_news(limit: int = 10) -> List[Item]:
    from bs4 import BeautifulSoup
    from feedparser import parse as parse_feed

    rss_url = "https://news.google.com/rss/search?q=%EA%B2%BD%EC%A0%9C&hl=ko&gl=KR&ceid=KR:ko"
    feed = parse_feed(rss_url)
    items = []  # type: List[Item]

    for entry in feed.entries[:limit]:
        title = clean_text(entry.get("title", ""))
        source = clean_text(entry.get("source", {}).get("title", "Google News"))
        date = clean_text(entry.get("published", ""))
        url = clean_text(entry.get("link", ""))
        summary_html = entry.get("summary", "")
        summary = clean_text(BeautifulSoup(summary_html, "html.parser").get_text(" "))

        items.append(
            Item(
                title=translate_to_korean(title),
                source=source,
                date=date,
                url=url,
                summary=translate_to_korean(summary),
            )
        )

    return items


def fetch_stock_reports(stock_keyword: str, limit: int = 10) -> List[Item]:
    import requests
    from bs4 import BeautifulSoup

    base_url = "https://finance.naver.com/research/company_list.naver"
    resp = requests.get(base_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.select_one("table.type_1")
    if not table:
        return []

    reports = []  # type: List[Item]

    for row in table.select("tr"):
        cols = row.select("td")
        if len(cols) < 5:
            continue

        title_link = cols[1].select_one("a")
        stock_name = clean_text(cols[0].get_text(" "))
        if not title_link:
            continue

        if stock_keyword.lower() not in stock_name.lower():
            continue

        title = clean_text(title_link.get_text(" "))
        href = title_link.get("href", "")
        report_url = "https://finance.naver.com{0}".format(href)
        analyst = clean_text(cols[2].get_text(" "))
        source = clean_text(cols[3].get_text(" "))
        date = clean_text(cols[4].get_text(" "))
        summary = fetch_report_summary(report_url)

        reports.append(
            Item(
                title=translate_to_korean(title),
                source="{0} / 애널리스트: {1}".format(source, analyst),
                date=date,
                url=report_url,
                summary=translate_to_korean(summary),
            )
        )

        if len(reports) >= limit:
            break

    return reports


def fetch_report_summary(url: str) -> str:
    import requests
    from bs4 import BeautifulSoup

    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        return "리포트 상세 페이지를 불러오지 못했습니다."

    soup = BeautifulSoup(resp.text, "html.parser")
    body = soup.select_one("td.view_cnt")
    if not body:
        return "리포트 요약을 찾지 못했습니다."

    return clean_text(body.get_text(" "))[:1200]


def to_markdown(title: str, items: Iterable[Item]) -> str:
    lines = ["# {0}".format(title), ""]
    for idx, item in enumerate(items, start=1):
        lines.extend(
            [
                "## {0}. {1}".format(idx, item.title),
                "- 출처: {0}".format(item.source),
                "- 날짜: {0}".format(item.date),
                "- 링크: {0}".format(item.url),
                "",
                item.summary or "(요약 없음)",
                "",
            ]
        )

    if len(lines) <= 2:
        lines.append("수집된 데이터가 없습니다.")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="경제 뉴스/종목 리포트 자동 수집 + 한글 번역")
    parser.add_argument("--stock", required=True, help="예: 삼성전자")
    parser.add_argument("--news-limit", type=int, default=8)
    parser.add_argument("--report-limit", type=int, default=5)
    args = parser.parse_args()

    news = fetch_economic_news(limit=args.news_limit)
    reports = fetch_stock_reports(stock_keyword=args.stock, limit=args.report_limit)

    now = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    news_md = to_markdown("경제 뉴스(한글 번역)", news)
    report_md = to_markdown("{0} 증권사 리포트(한글 번역)".format(args.stock), reports)

    news_file = out_dir / "news_{0}.md".format(now)
    report_file = out_dir / "report_{0}_{1}.md".format(args.stock, now)
    news_file.write_text(news_md, encoding="utf-8")
    report_file.write_text(report_md, encoding="utf-8")

    print("완료: {0}".format(news_file))
    print("완료: {0}".format(report_file))


if __name__ == "__main__":
    main()
