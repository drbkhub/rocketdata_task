import requests
from bs4 import BeautifulSoup
import json
import re
import time

url = "https://www.ziko.pl/lokalizator/"
base_url = "https://www.ziko.pl"
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
    ziko_places = []
    i = 1
    for item in soup.find_all("tr"):
        if item.has_attr("data-mp-map-id"):
            data = list(item.find("td", class_="mp-table-address").strings)

            address = f"{data[0]}, {data[-3]}"
            name = item.find(class_="mp-pharmacy-head").text.strip()
            phones = re.findall(r"\d[\d ]+\d", data[-2] + "." + data[-1])
            working_hours = [hour.strip() for hour in
                             re.findall(r"[\w\- ]+:[\d \-:]+", item.find(class_="mp-table-hours").text)]
            # get child page to get coordinates
            child_url = base_url + item.find('div', class_="morepharmacy").find('a').get('href')
            child_page = get_page(child_url)
            child_parser = BeautifulSoup(child_page, 'html.parser')
            latlon = re.findall("[\d\.]+", child_parser.find(class_="coordinates").text)

            result = {
                "address": address,
                "latlon": latlon,
                "name": name,
                "phones": phones,
                "working_hours": working_hours
            }

            ziko_places.append(result)

            print(f"{i}. {name=}, {address=}")
            i += 1
            time.sleep(1)

    with open("ziko.json", "w", encoding="utf-8") as f:
        json.dump(ziko_places, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    parse()