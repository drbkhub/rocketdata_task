import json

import requests
from bs4 import BeautifulSoup
import re

url = "https://monomax.by/map"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
             "Chrome/102.0.5005.63 Safari/537.36"
headers = {'User-Agent': user_agent}


def get_page(url, headers=headers):
    try:
        page = requests.get(url, headers=headers)
        return page.content
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException(f"download page error {url=}")


def parse():
    page = get_page(url)
    soup = BeautifulSoup(page, 'html.parser')
    shops = soup.find_all(class_="shop")
    results = []
    for shop in shops:
        phones = ["".join(re.split("[ \(\)]+", p.a.text)) for p in shop.find_all(class_="phone") if p.a.text.strip()]
        results.append({
            "address": shop.find(class_="name").text.strip(", "),
            "latlon": None,
            "name": "Мономах",
            "phones": phones
        })

    _latlon = re.findall("\.Placemark\([\s]+\[([\d., ]+)\]", page.decode("utf-8"))
    for i, res in enumerate(results):
        res["latlon"] = _latlon[i].split(', ')

    return results

if __name__ == "__main__":
    with open("monomax.json", "w") as f:
        json.dump(parse(), f, indent=4, ensure_ascii=False)
