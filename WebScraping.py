import time
import re
from typing import List, Dict, Optional

import pandas as pd
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def build_indeed_url(query: str, location: str, start: int = 0) -> str:
    """Build an Indeed search URL."""
    base = "https://www.indeed.com/jobs"
    params = {
        "q": query,
        "l": location,
        "start": start,
    }
    return requests.Request("GET", base, params=params).prepare().url


def get_page(url: str) -> BeautifulSoup:
    """Fetch and parse a single Indeed page."""
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def clean_text(element) -> str:
    if element is None:
        return ""
    return re.sub(r"\s+", " ", element.get_text(" ", strip=True))


def get_job_link(card) -> str:
    anchor = card.select_one("h2 a")
    if not anchor:
        anchor = card.select_one("a[jobtitle]")
    if not anchor:
        return ""
    href = anchor.get("href", "")
    if href.startswith("/"):
        return "https://www.indeed.com" + href
    return href


def extract_jobs_from_page(soup: BeautifulSoup) -> List[Dict[str, str]]:
    jobs = []
    cards = soup.select("div.job_seen_beacon")

    if not cards:
        cards = soup.select("div. jobsearch-SerpJobCard")

    for card in cards:
        title = card.select_one("h2.jobTitle a")
        if title is None:
            title = card.select_one("h2 a")
        if title is None:
            continue

        job = {
            "title": clean_text(title),
            "company": clean_text(card.select_one("span.companyName")),
            "location": clean_text(card.select_one("div.companyLocation")),
            "salary": clean_text(card.select_one("div.metadata.salary-snippet-container")),
            "summary": clean_text(card.select_one("div.job-snippet")),
            "link": get_job_link(card),
        }

        if job["title"]:
            jobs.append(job)

    return jobs


def scrape_indeed(query: str, location: str, pages: int = 5, sleep_time: float = 2.0) -> pd.DataFrame:
    """Scrape job listings from Indeed for a given keyword and location."""
    all_jobs = []

    for page in range(pages):
        start = page * 10
        url = build_indeed_url(query=query, location=location, start=start)
        print(f"Fetching page {page + 1}: {url}")

        try:
            soup = get_page(url)
        except requests.exceptions.RequestException as exc:
            print(f"Error while fetching {url}: {exc}")
            break

        jobs = extract_jobs_from_page(soup)
        if not jobs:
            print("No jobs found on this page. Stopping.")
            break

        all_jobs.extend(jobs)

        if page < pages - 1:
            time.sleep(sleep_time)

    return pd.DataFrame(all_jobs)


if __name__ == "__main__":
    query = "python developer"
    location = "United States"
    jobs_df = scrape_indeed(query=query, location=location, pages=3)

    print(f"Found {len(jobs_df)} jobs.")
    print(jobs_df.head())

    jobs_df.to_csv("indeed_jobs.csv", index=False)
    print("Saved results to indeed_jobs.csv")
