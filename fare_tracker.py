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


def track_trains(hours: int = 1):
    scraper = nrs.NationalRailScraper()
    while True:
        with open("Data/tracked_trains.json", "r") as f:
            json_data = json.load(f)
        for key in json_data:
            if json_data[key] is not None:
                continue
            origin_code, destination_code, date = key.split("-")
            cheapest_ticket = scraper.find_cheapest_ticket_for_day(origin_code, destination_code, date, 1, None)

            if cheapest_ticket is None:
                # Ticket's aren't released yet
                print("Tickets aren't released yet.")
                continue

            if cheapest_ticket[0].price != json_data[key]:
                print("New price found!")
                print(f"Train: {origin_code} to {destination_code} on {date}")
                print(f"Old price: {json_data[key]}")
                print(f"New price: {cheapest_ticket[0].price}")
                fare_bracket = pb.get_fare_bracket(pb.get_price_bands(origin_code, destination_code), cheapest_ticket[0].price)
                print(f"Price band: {fare_bracket.index(cheapest_ticket[0].price) + 1}/{len(fare_bracket)}")

                with open("Data/tracked_trains.json", "r") as f:
                    json_data = json.load(f)
                with open("Data/tracked_trains.json", "w") as f:
                    json_data[key] = cheapest_ticket[0].price
                    json.dump(json_data, f, indent=4)

        print("Sleeping...")
        time.sleep(hours * 3600)
