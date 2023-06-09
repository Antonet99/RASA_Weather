import requests
import json
import sys
import datetime


def get_api():

    path = "/Users/antoniobaio/Desktop/Progetti/ProgettiDS/Chatbot_RASA/config.json"
    with open(path) as f:
        data = json.load(f)

    owm_api = data['owm_api']

    return owm_api


def get_lat_lon(city):

    owm_api = get_api()

    url = (
        f"http://api.openweathermap.org/geo/1.0/direct?"
        f"q={city}&limit=2&appid={owm_api}"
    )
    response = requests.get(url)

    if response.status_code == 200:
        # parsing della risposta JSON
        data = response.json()
        if len(data) > 0:
            # accesso alle coordinate geografiche della città
            lat = data[0]['lat']
            lon = data[0]['lon']

            lat = round(lat, 1)
            lon = round(lon, 1)

            return lat, lon
        else:
            print(
                f"Non sono state trovate informazioni geografiche per la città di {city}")
    else:
        print("Errore durante la richiesta delle informazioni geografiche")


def get_weather_data(city):
    """Get weather data from the API and return the necessary data."""

    owm_api = get_api()
    lat, lon = get_lat_lon(city)

    url = (
        f"https://api.openweathermap.org/data/3.0/onecall?"
        f"lat={lat}&lon={lon}"
        f"&lang=it"
        f"&units=metric"
        f"&exclude=hourly,minutely"
        f"&appid={owm_api}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()

    except requests.HTTPError:
        status = response.status_code
        if status == 401:
            print("Chiave API non valida.")
        elif status == 404:
            print("Input non valido.")
        elif status in (429, 443):
            print("Chiamate API al minuto superate.")

        sys.exit(1)

    weather_data = response.json()

    return weather_data
