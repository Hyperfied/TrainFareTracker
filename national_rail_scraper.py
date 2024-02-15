from datetime import datetime, timedelta
import time
from enum import Enum
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


class LeavingType(Enum):
    DEPARTING = "departing"
    ARRIVING = "arriving"


class Ticket:
    def __init__(self, price: float, departure_time: datetime, arrival_time: datetime,
                 duration: timedelta, changes: int):
        self.price = price
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.duration = duration
        self.changes = changes

    def __repr__(self):
        return (f"Price: {self.price}, Departs: {self.departure_time.time()}, Arrives: {self.arrival_time.time()},"
                f" Duration: {self.duration}, Changes: {self.changes} |")

    def __eq__(self, other):
        return (self.price == other.price and self.departure_time == other.departure_time and
                self.arrival_time == other.arrival_time and self.duration == other.duration and
                self.changes == other.changes)


def get_single_url(origin: str, destination: str, leaving_type: LeavingType, leaving_date: str, leaving_hour: str,
                   leaving_min: str, adults: int, railcard: str = None) -> str:
    if not railcard:
        url = (f"https://www.nationalrail.co.uk/journey-planner/?type=single&origin={origin}&destination={destination}"
               f"&leavingType={leaving_type.value}&leavingDate={leaving_date}&leavingHour={leaving_hour}&leavingMin="
               f"{leaving_min}&adults={adults}&extraTime=0")
    else:
        url = (f"https://www.nationalrail.co.uk/journey-planner/?type=single&origin={origin}&destination={destination}"
               f"&leavingType={leaving_type.value}&leavingDate={leaving_date}&leavingHour={leaving_hour}"
               f"&leavingMin={leaving_min}&adults={adults}&railcards={railcard}&extraTime=0")
    return url


class NationalRailScraper:
    accepted_cookies = False

    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=options)

    def get_tickets(self, url) -> list[Ticket] | None:
        if not self.accepted_cookies:
            self.accept_cookies()

        self.browser.get(url)

        while True:
            time.sleep(0.1)

            soup = BeautifulSoup(self.browser.page_source, "html.parser")
            train_list = soup.find_all("section")[0].find("ul")
            if train_list is None:
                return None
            if len(train_list) > 0:
                break

        tickets = []
        if train_list is None:
            print("No journeys found.")
            return None
        for li in train_list:
            spans = li.find_all("span")
            times = li.find_all("time")
            if spans[0].get_text().startswith("No fares available."):
                continue
            for span in spans:
                if span.get_text().startswith("£"):
                    price = float(span.get_text().replace("£", ""))
                    break
            else:
                continue
            departure_time = datetime.strptime(times[0].get_text(), "%H:%M")
            arrival_time = datetime.strptime(times[1].get_text(), "%H:%M")
            hours_minutes = times[2].get_text().replace("h", "").replace("m", "").split(" ")
            if len(hours_minutes) == 1:
                hours_minutes.append("0")
            duration = timedelta(hours=int(hours_minutes[0]), minutes=int(hours_minutes[1]))
            for span in spans:
                if span.get_text().endswith("change(s)"):
                    changes = int(span.get_text().replace("change(s)", ""))
                    break
            else:
                continue

            ticket = Ticket(price, departure_time, arrival_time, duration, changes)
            tickets.append(ticket)

        return tickets

    def accept_cookies(self):
        self.browser.get("https://www.nationalrail.co.uk/")
        time.sleep(0.5)
        self.browser.find_element(By.ID, 'onetrust-accept-btn-handler').click()
        self.accepted_cookies = True

    def find_cheapest_ticket_for_day(self, origin: str, destination: str, leaving_date: str,
                                     adults: int, railcard: str = None) -> list[Ticket] | None:
        url = get_single_url(origin, destination, LeavingType.DEPARTING, leaving_date, "00", "00", adults, railcard)

        found_all_tickets = False
        tickets = []
        last_hour = None
        while not found_all_tickets:
            current_tickets = self.get_tickets(url)
            if current_tickets is None:
                return None

            hour = str(current_tickets[-1].departure_time.hour)
            minute = str(15 * round(current_tickets[-1].departure_time.minute / 15))
            if len(hour) == 1:
                hour = f"0{hour}"
            if len(minute) == 1:
                minute = f"0{minute}"
            url = get_single_url(origin, destination, LeavingType.DEPARTING,
                                 leaving_date, hour, minute, adults, railcard)

            for ticket in current_tickets:
                if last_hour is not None:
                    if ticket.departure_time.hour < last_hour:
                        found_all_tickets = True
                        break
                last_hour = ticket.departure_time.hour

                if ticket not in tickets:
                    tickets.append(ticket)

        cheapest_ticket = []
        for ticket in tickets:
            if len(cheapest_ticket) == 0:
                cheapest_ticket = [ticket]
            elif ticket.price < cheapest_ticket[0].price:
                cheapest_ticket = [ticket]
            elif ticket.price == cheapest_ticket[0].price:
                cheapest_ticket.append(ticket)

        return cheapest_ticket

    def close(self):
        self.browser.quit()
