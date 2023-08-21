import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep
import datetime
import math
import json
import uuid


# Constants
INITIAL_URL = "https://sofifa.com/"
OFFSET_URL = "?col=oa&sort=desc&hl=es-ES&offset="

# Diccionario de relaciones entre posiciones y posIndex
position_mapping = {
    "POR": 1,
    "DFC": 2,
    "CAR": 3,
    "LD": 4,
    "LI": 5,
    "MCD": 6,
    "MC": 7,
    "MCO": 8,
    "MD": 9,
    "MI": 10,
    "EI": 11,
    "ED": 12,
    "SD": 15,
    "DC": 16
}

def get_soup(url, headers):
    """
    Fetches the content from the provided URL and returns a BeautifulSoup object.
    """

    response = requests.get(url, allow_redirects=False, headers=headers)
    seconds_of_sleep = randint(1, 2)
    log(f"Waiting {seconds_of_sleep} seconds")
    sleep(seconds_of_sleep)
    return BeautifulSoup(response.text, "html.parser")


def log(message):
    """Logging function to log messages with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] - {message}")


def extract_value(value_str):
    if value_str.endswith('M'):
        value = float(value_str.replace('€', '').replace('M', ''))
        return math.ceil(value)


def main():

    offset = 0
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })
    players = []
    while offset <= 1200:
        soup = get_soup(f"{INITIAL_URL}{OFFSET_URL}{offset}", headers)
        active_seasons_elements = soup.find("tbody", class_="list")
        a_elements = active_seasons_elements.find_all('tr')
        for row in a_elements:
            fields = row.find_all('td')
            col_name = fields[1]
            name = col_name.find("div", class_="ellipsis").text.strip()
            position = col_name.find('a', rel='nofollow').get_text()
            full_stats_url = f"{INITIAL_URL}{col_name.find('a')['href']}"
            value_str = fields[6].text.strip()
            value = extract_value(value_str)
            img_element = fields[0].find('img')
            src_value = img_element['data-src']
            new_src_value = src_value.replace("60.png", "120.png")  # Reemplazar "60.png" por "120.png"
            log(f"{name} {position} {new_src_value} {value} {full_stats_url}")
            # Obtener posIndex a partir del diccionario de relaciones
            pos_index = position_mapping.get(position, 0)

            player = {
                "_id": {
                    "$oid": f"{uuid.uuid4().hex[:24]}"
                },
                "title": name,
                "clausula": value,
                "clausulaInicial": value,
                "address": position,
                "posIndex": pos_index,
                "image": new_src_value,
                "escudo": "https://futhead.cursecdn.com/static/img/20/leagues/382.png",
                "ofertas": [],
                "transferible": False,
                "marketValue": 0,
                "Expires": 1629501234558,
                "ownerDiscard": {
                    "$oid": "611c2d9302c6a20016929dab"
                },
                "discardExpiresDate": 1630106033234,
                "team": "Sin equipo",
                "creatorName": "Agente Libre",
                "__v": 0
            }

            players.append(player)
        offset = offset + 60

    players_json = json.dumps(players, indent=2, ensure_ascii=False)
    log(players_json)
    with open("players.json", "w", encoding="utf-8") as file:
        file.write(players_json)


main()
