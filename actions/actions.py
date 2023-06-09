
# TODO:
# - aggiungere la possibilità di chiedere il meteo di un giorno specifico
# - aggiungere messaggio di benvenuto
# - aggiungere messaggio di spiegazione funzionamento chatbot


from typing import Any, Text, Dict, List
from rasa_sdk.events import SlotSet
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

import requests

from weather import get_weather_data

#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Hello World from my first action!")

        return []


class Weather(Action):

    def name(self) -> Text:
        return "action_weather"

    def check_alerts(self, weather_data):
        if 'alerts' in weather_data:
            return True
        else:
            return False

    def check_rain(self, weather_data):
        if 'rain' in weather_data['current']:
            return True
        else:
            return False

    def check_rain_predict(self, weather_data, slot):
        if 'rain' in weather_data['daily'][slot]:
            return True
        else:
            return False

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city = tracker.get_slot('city')
        wx_type = tracker.get_slot('wx_type')
        wx_forecast = tracker.get_slot('wx_forecast')

        if wx_type is None:
            wx_type = "meteo"
        if wx_forecast is None:
            wx_forecast = "ora"

        slot = 0
        if wx_forecast == "domani":
            slot = 1

        try:
            # chiamata API che ritorna JSON con info meteo
            weather_data = get_weather_data(city)

            lat = weather_data['lat']
            lon = weather_data['lon']
            timezone = weather_data['timezone']

            # info meteo attuale "current"
            temp = round(weather_data['current']['temp'])
            percepita = round(weather_data['current']['feels_like'])
            pressione = round(weather_data['current']['pressure'])
            umidità = round(weather_data['current']['humidity'])
            uvi = round(weather_data['current']['uvi'])
            vento_velocità = round(weather_data['current']['wind_speed'])
            vento_dir = round(weather_data['current']['wind_deg'])
            descrizione_meteo = weather_data['current']['weather'][0]['description']

            if self.check_rain(weather_data) == True:
                pioggia = weather_data['current']['rain']['1h']
            else:
                pioggia = 0

            # set values to forecasted weather variables from open_wx_msg json
            temp_min_predict = round(
                weather_data['daily'][slot]['temp']['min'])
            temp_max_predict = round(
                weather_data['daily'][slot]['temp']['max'])
            pressione_predict = round(weather_data['daily'][slot]['pressure'])
            umidità_predict = round(weather_data['daily'][slot]['humidity'])
            uvi_predict = round(weather_data['daily'][slot]['uvi'])
            vento_velocità_predict = round(
                weather_data['daily'][slot]['wind_speed'])
            vento_dir_predict = round(weather_data['daily'][slot]['wind_deg'])
            cond_predict = (weather_data['daily']
                            [slot]['weather'][0]["description"])

            if self.check_rain_predict(weather_data, slot) == True:
                pioggia_predict = round(weather_data['daily'][slot]['rain'], 1)
            else:
                pioggia_predict = 0

            if wx_forecast == "ora":

                # ritorna tutto il meteo
                if wx_type.lower() == "meteo":

                    response = f"Meteo attuale a {city}: {descrizione_meteo}\n" \
                        f"Temperatura: {temp} °C (Percepita {percepita} °C)\n" \
                        f"Umidità: {umidità} %\n" \
                        f"Pressione: {pressione} hPa\n" \
                        f"Indice UV: {uvi}\n" \
                        f"Vento: {vento_velocità} m/s, {vento_dir}°\n" \

                    if self.check_rain(weather_data) == True:
                        response = response + \
                            f"Pioggia (nell'ultima ora): {pioggia} mm\n"
                    else:
                        f"Pioggia: attualmente non sta piovendo \n"

                    if self.check_alerts(weather_data) == True:

                        sender = weather_data['alerts'][0]['sender_name']
                        event = weather_data['alerts'][0]['event']
                        alert_descript = weather_data['alerts'][0]['description']

                        response = response + f"ATTENZIONE! Sono previste allerte meteo:\n" \
                            f" - mandante: {sender}\n" \
                            f" - evento: {event}\n" \
                            f" - descrizione: {alert_descript}\n"

                    dispatcher.utter_message(response)

                    # ritorna il singolo parametro richiesto dall'utente
                elif wx_type.lower() == "vento":
                    response = f"La velocità attuale del vento a {city} è di {vento_velocità} metri al secondo da {vento_dir} gradi. "
                    dispatcher.utter_message(response)

                elif wx_type.lower() == "temperatura":
                    response = f"La temperatura attuale a {city} è {temp}°C. "
                    dispatcher.utter_message(response)

                elif wx_type.lower() == "pressione":
                    response = f"La pressione attuale dell'aria a {city} è {pressione} hPa. "
                    dispatcher.utter_message(response)

                elif wx_type.lower() == "umidità":
                    response = f"L'umidità attuale a {city} è {umidità}%. "
                    dispatcher.utter_message(response)

                elif wx_type.lower() == "uvi":
                    response = f"L'indice UV attuale a {city} è {uvi}. "
                    dispatcher.utter_message(response)

                elif wx_type.lower() == "pioggia":
                    if self.check_rain(weather_data) == True:
                        response = f"La pioggia nell'ultima ora a {city} è stata di {pioggia} mm. "
                        dispatcher.utter_message(response)
                    elif pioggia == 0:
                        response = f"Non sta piovendo in questo momento a {city}. "
                        dispatcher.utter_message(response)

            elif wx_forecast == "oggi" or wx_forecast == "domani":

                # generic forecast
                if wx_type.lower() == "meteo":

                    response = f"Meteo previsto per {wx_forecast} a {city}: {descrizione_meteo}\n" \
                        f"Temperatura minima: {temp_min_predict} °C\n" \
                        f"Temperatura massima: {temp_max_predict} °C\n" \
                        f"Umidità: {umidità_predict} %\n" \
                        f"Pressione: {pressione_predict} hPa\n" \
                        f"Indice UV: {uvi_predict}\n" \
                        f"Vento: {vento_velocità_predict} m/s, {vento_dir_predict}°\n" \

                    if self.check_rain_predict(weather_data, slot) == True:
                        response = response + \
                            f"Pioggia: {pioggia_predict} mm\n"
                    else:
                        f"Pioggia: non pioverà\n"

                    dispatcher.utter_message(response)

                # more specific forecasts
                elif wx_type == 'vento':
                    response = f"La velocità del vento prevista per {city} {wx_forecast} è di {vento_velocità_predict} metri al secondo da {vento_dir_predict} gradi."
                    dispatcher.utter_message(response)

                elif wx_type == 'temperatura':
                    response = f"La temperatura massima prevista per {city} {wx_forecast} è di {temp_max_predict}C mentre la minima è di {temp_min_predict}C."
                    dispatcher.utter_message(response)

                elif wx_type == 'pressione':
                    response = f"La pressione atmosferica prevista per {city} {wx_forecast} è di {pressione_predict} millibar."
                    dispatcher.utter_message(response)

                elif wx_type == 'umidità':
                    response = f"L'umidità prevista per {city} {wx_forecast} è del {umidità_predict}%."
                    dispatcher.utter_message(response)

                elif wx_type == 'uvi':
                    response = f"L'indice UV previsto per {city} {wx_forecast} è {uvi_predict}."
                    dispatcher.utter_message(response)

                elif wx_type == 'pioggia':
                    response = f"Le condizioni previste per {city} {wx_forecast} sono {cond_predict} e la pioggia caduta nelle 24 ore dovrebbe essere {pioggia_predict}mm."
                    dispatcher.utter_message(response)

            city = None
            wx_type = None
            wx_forecast = None

            return []

        except requests.HTTPError:
            status = response.status_code
            if status == 401:
                dispatcher.utter_message("Chiave API non valida.")
                return []
            elif status == 404:
                dispatcher.utter_message("Input della città non valido.")
                return []
            elif status in (429, 443):
                dispatcher.utter_message("Chiamate API al minuto superate.")
                return []
            else:
                dispatcher.utter_message(
                    "Si è verificato un errore generico durante la richiesta dei dati meteorologici.")
                return []
