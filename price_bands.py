import requests
import json
import os

with open("apikey.txt", "r") as f:
    apikey = f.read()


def get_api_request(origin_code: str, destination_code: str) -> dict:
    url = f"https://{apikey}@gw.brfares.com/legacy_querysimple?orig={origin_code}&dest={destination_code}"
    return requests.get(url).json()


def write_bands_to_cache(json_dict: dict):
    filename = f"{json_dict['orig']['code']}-{json_dict['dest']['code']}"
    with open(f"Data/RequestCache/{filename}.json", "w") as f:
        json.dump(json_dict, f, indent=4)


def parse_bands_from_dict(json_dict: dict) -> dict:
    fares = json_dict["fares"]
    bands = {}
    for fare in fares:
        name = fare["ticket"]["longname"]
        price = round(fare["adult"]["fare"]/100, 2)

        if name not in bands:
            bands.update({name: [price]})
        else:
            bands[name].append(price)

    return bands


def get_price_bands(origin_code: str, destination_code: str) -> dict:
    if os.path.exists(f"Data/RequestCache/{origin_code}-{destination_code}.json"):
        with open(f"Data/RequestCache/{origin_code}-{destination_code}.json", "r") as f:
            return parse_bands_from_dict(json.load(f))
    else:
        request = get_api_request(origin_code, destination_code)
        write_bands_to_cache(request)
        return parse_bands_from_dict(request)


def get_fare_bracket(price_band: dict, price: float) -> list[float]:
    for fare in price_band:
        if price in price_band[fare]:
            return price_band[fare]
    return []


