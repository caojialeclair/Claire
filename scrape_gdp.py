import csv
import json
import time
from typing import List, Dict, Optional

import requests

# Example list of prefecture-level city codes. Expand as needed.
CITY_CODES = {
    "110000": "北京市",
    "310000": "上海市",
    "440100": "广州市",
    # Add more city codes here
}

API_URL = "https://data.stats.gov.cn/easyquery.htm"


def fetch_gdp(city_code: str, year: int) -> Optional[float]:
    """Fetch GDP data for a given city code and year."""
    params = {
        "m": "QueryData",
        "dbcode": "fsnd",
        "rowcode": "reg",
        "colcode": "sj",
        "wds": json.dumps([{"wdcode": "zb", "valuecode": "A020101"}]),
        "dfwds": json.dumps([
            {"wdcode": "reg", "valuecode": city_code},
            {"wdcode": "sj", "valuecode": str(year)},
        ]),
    }
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(API_URL, params=params, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        node = data["returndata"]["datanodes"][0]
        return float(node["data"]["data"])
    except Exception:
        return None


def scrape(years: List[int]) -> List[Dict[str, Optional[float]]]:
    results = []
    for city_code, city_name in CITY_CODES.items():
        for year in years:
            gdp = fetch_gdp(city_code, year)
            results.append({
                "city": city_name,
                "code": city_code,
                "year": year,
                "gdp": gdp,
            })
            time.sleep(0.5)  # polite delay
    return results


def save_csv(records: List[Dict[str, Optional[float]]], filename: str) -> None:
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["city", "code", "year", "gdp"])
        writer.writeheader()
        writer.writerows(records)


def main() -> None:
    years = list(range(2019, 2024))
    data = scrape(years)
    save_csv(data, "gdp_data.csv")
    print("Saved data to gdp_data.csv")


if __name__ == "__main__":
    # Note: check the target website's terms of service before scraping.
    main()
