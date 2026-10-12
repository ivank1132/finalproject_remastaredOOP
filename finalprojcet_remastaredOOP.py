
import requests
import sqlite3
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class SteamGame:
    def __init__(self, name, appid, price):
        self.name = name
        self.appid = appid
        self.price = price
    def can_afford(self, budget):
        if self.price <= budget:
            return True
        else:
            return False
    def show_info(self):
        print("Game:", self.name)
        print(f"Price: ${self.price:.2f}")
conn = sqlite3.connect("steam_games.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS games (id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,appid INTEGER,price REAL,budget REAL,date_time TEXT)""")
conn.commit()
def find_game(game_name):
    url = "https://store.steampowered.com/api/storesearch/"
    params = {
        "term": game_name,
        "l": "en",
        "cc": "us"
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()
    if not data.get("items"):
        return None
    game_data = data["items"][0]
    appid = game_data["id"]
    url = "https://store.steampowered.com/api/appdetails/"
    params = {
        "appids": appid,
        "cc": "us",
        "l": "en"
    }
    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()
    result = response.json()[str(appid)]
    if not result.get("success"):
        return None
    info = result["data"]
    if info.get("is_free"):
        price = 0.0
    else:
        price_info = info.get("price_overview")

        if not price_info:
            return None
        price = price_info["final"] / 100
    game = SteamGame(
        info["name"],
        appid,
        price
    )
    return game
def main():
    try:
        budget = float(input("Ваш бджет в долларах США: "))
        if budget < 0:
            print(Fore.RED + "Бюджет не може бути негативним!")
            return
        game_name = input("Назва гри: ")
        if not game_name.strip():
            print(Fore.RED + "НАЗВУ ГРИ")
            return
        game = find_game(game_name)
        if game is None:
            print(Fore.RED + "Гру не знайдено")
            return
        print()
        game.show_info()
        print(f"Ваш бюджет: ${budget:.2f}")
        if game.can_afford(budget):
            print(Fore.GREEN + "Ви можете купити цю гру")
        else:
            print(Fore.RED + "Ви не можете купити цю гру")
            difference = game.price - budget
            print(f"Вам потрібно ще ${difference:.2f}.")
        answer = input("\nЗавантажити цю гру у БД (y/n): ")

        if answer.lower() == "y":
            date_time = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            cursor.execute("""
                INSERT INTO games
                (name, appid, price, budget, date_time)
                VALUES (?, ?, ?, ?, ?)
            """, (game.name,game.appid,game.price,budget,date_time))
            conn.commit()
            print(Fore.GREEN + "Гру завантажено")
    except ValueError:
        print(Fore.RED + "Напишіть правльний номер.")
    except requests.RequestException as error:
        print(Fore.RED + "Помилка к підключенню з стімом:", error)
    finally:
        conn.close()
if __name__ == "__main__":
    main()
