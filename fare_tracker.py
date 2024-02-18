import json
import time

import price_bands as pb
import national_rail_scraper as nrs


def add_train_to_tracker(origin_code: str, destination_code: str, date: str):
    with open("Data/tracked_trains.json", "r") as f:
        json_data = json.load(f)
    with open("Data/tracked_trains.json", "w") as f:
        key = f"{origin_code}-{destination_code}-{date}"
        if key in json_data:
            print("Train already tracked.")
            return
        json_data.update({key: None})
        json.dump(json_data, f, indent=4)


def get_tracked_trains() -> list[str]:
    with open("Data/tracked_trains.json", "r") as f:
        json_data: dict = json.load(f)
    return [*json_data.keys()]


def remove_train_from_tracker(index: int):
    with open("Data/tracked_trains.json", "r") as f:
        json_data: dict = json.load(f)
    with open("Data/tracked_trains.json", "w") as f:
        try:
            key = [*json_data.keys()][index]
            del json_data[key]
            json.dump(json_data, f, indent=4)
        except IndexError:
            print("Index out of range.")
            return


def track_trains() -> list[str]:
    scraper = nrs.NationalRailScraper()
    notifs = []
    try:
        with open("Data/tracked_trains.json", "r") as f:
            json_data = json.load(f)
    except json.decoder.JSONDecodeError:
        json_data = {}
    for key in json_data:
        origin_code, destination_code, date = key.split("-")
        cheapest_ticket = scraper.find_cheapest_ticket_for_day(origin_code, destination_code, date, 1, None)

        if cheapest_ticket is None:
            # Tickets aren't released yet
            print("Tickets aren't released yet.")
            continue

        if cheapest_ticket[0].price != json_data[key]:
            notif = (f"New price found!\n"
                     f"Train: {origin_code} to {destination_code} on {date}\n"
                     f"Old price: {json_data[key]}\n"
                     f"New price: {cheapest_ticket[0].price}\n")
            fare_bracket = pb.get_fare_bracket(pb.get_price_bands(origin_code, destination_code), cheapest_ticket[0].price)
            notif += f"Price band: {fare_bracket.index(cheapest_ticket[0].price) + 1}/{len(fare_bracket)}"
            notifs.append(notif)

            with open("Data/tracked_trains.json", "r") as f:
                json_data = json.load(f)
            with open("Data/tracked_trains.json", "w") as f:
                json_data[key] = cheapest_ticket[0].price
                json.dump(json_data, f, indent=4)

    return notifs
