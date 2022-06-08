import json
from typing import Any

import requests

short_day_names = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]

clear_minutes = lambda t: ":".join(t.split(":")[:-1])


def prepare_working_hours(regular_daily):
    periods = []
    fd = short_day_names[0]
    for i in range(len(regular_daily) - 1):
        index = regular_daily[i]["weekDay"] - 1
        time_from = clear_minutes(regular_daily[i]["timeFrom"])
        time_till = clear_minutes(regular_daily[i]["timeTill"])
        next_time_from = clear_minutes(regular_daily[i + 1]["timeFrom"])
        next_time_till = clear_minutes(regular_daily[i + 1]["timeTill"])
        if next_time_from != time_from or next_time_till != time_till:
            if fd != short_day_names[index]:
                periods.append(f"{fd}-{short_day_names[index]} {time_from}-{time_till}")
            else:
                periods.append(f"{fd} {time_from}-{time_till}")
            fd = short_day_names[index + 1]
    else:
        if fd == short_day_names[-1]:
            periods.append(f"{fd} {time_from}-{next_time_till}")
        elif fd == short_day_names[0]:
            periods.append(f"{fd}-{short_day_names[-1]} {time_from}-{next_time_till}")
    return periods


def get_or_none(obj, *keys: list[str]) -> Any:
    for attr in keys:
        if obj.get(attr) is not None:
            obj = obj.get(attr)
        else:
            return
    return obj


def parse():
    url = "https://api.kfc.com/api/store/v2/store.get_restaurants?showClosed=true"
    data = json.loads(requests.get(url).content)
    stores = []
    for store in data["searchResults"]:
        st = store.get("storePublic")
        address = get_or_none(st, "contacts", "streetAddress", "ru")
        if address is not None:
            address = " ".join(address.split()[1:])
        latlon = get_or_none(st, "contacts", "coordinates", "geometry", "coordinates")
        name = get_or_none(st, "title", "ru")
        _phone1 = get_or_none(st, "contacts", "phone", "number")
        _phone2 = get_or_none(st, "contacts", "phoneNumber")
        phones = list({phone.split()[0] for phone in [_phone1, _phone2] if phone not in (None, "")})
        if get_or_none(st, "status") == "Open" and get_or_none(st, "openingHours", "regularDaily"):
            working_hours = prepare_working_hours(st["openingHours"]["regularDaily"])
        else:
            working_hours = ["closed"]

        stores.append({
            "address": address,
            "latlon": latlon,
            "name": name,
            "phones": phones,
            "working_hours": working_hours
        })

    return stores


if __name__ == "__main__":
    with open("kfc.json", "w", encoding="utf-8", ) as f:
        json.dump(parse(), f, indent=4, ensure_ascii=False)
