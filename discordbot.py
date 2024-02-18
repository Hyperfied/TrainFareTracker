import time

import discord
from discord.ext import tasks
import fare_tracker as ft

with open("Data/bottoken.txt", "r") as f:
    token = f.read()


def subscribe_user(user_id: int):
    with open("Data/subscribed_users.txt", "a") as f:
        f.write(f"{user_id}\n")


def get_subscribed_users() -> list[int]:
    with open("Data/subscribed_users.txt", "r") as f:
        return [int(line.strip()) for line in f.readlines()]


def remove_subscribed_user(index: int):
    with open("Data/subscribed_users.txt", "r") as f:
        users = [int(line.strip()) for line in f.readlines()]
    with open("Data/subscribed_users.txt", "w") as f:
        try:
            del users[index]
            for user in users:
                f.write(f"{user}\n")
        except IndexError:
            print("Index out of range.")
            return


class HyperBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f"Logged on as {self.user}")
        self.check_trains.start()

    @tasks.loop(hours=1)
    async def check_trains(self):
        notifs = ft.track_trains()
        for notif in notifs:
            for user in get_subscribed_users():
                print(user)
                await self.get_user(user).send(notif)
                time.sleep(2)
        print("Checked.")


def run_client():
    intents = discord.Intents.default()
    intents.members = True
    intents.message_content = True
    client = HyperBot(intents=intents)
    client.run(token)
