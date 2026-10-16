# by SQ9ATK
import re
import logging

from datetime import datetime

from bs4 import BeautifulSoup

from sr0wx_module import SR0WXModule


class MeteoOnet(SR0WXModule):
    """Klasa pobierająca informacje o pogodzie"""

    def __init__(self, language, service_url, saytime, current):
        self.__service_url = service_url
        self.__language = language
        self.__current = current
        self.__saytime = saytime
        self.__logger = logging.getLogger(__name__)

    def downloadFile(self, url):
        data = self.requestData(url, self.__logger)
        return data.text

    def getHour(self):
        time = ":".join([str(datetime.now().hour), str(datetime.now().minute)])
        datetime_object = datetime.strptime(time, "%H:%M")
        time_words = self.__language.read_datetime(datetime_object, "%H %M")
        return time_words

    def parseForecastDesc(self, html):
        match = html.find_all("div", {"class": "forecastDesc"})[0].text.strip()
        # klucze sampli opisów w słowniku powstały przez zamianę każdego znaku
        # spoza [a-z0-9] na "_", np. "przeja_nienia__zachmurzenie_umiarkowane"
        return re.sub("[^a-z0-9]", "_", match.lower())

    def parseValue(self, html, label):
        """Liczba z pozycji listy o etykiecie `label`, None gdy jej nie ma.

        Pozycje są wyszukiwane po etykiecie, nie po indeksie -- onet zmienia
        kolejność i zestaw pól (ciśnienie zniknęło, na jego miejscu pojawiła
        się szansa opadów)."""
        for li in html.find_all("li"):
            spans = li.find_all("span")
            if len(spans) >= 2 and spans[0].text.strip().startswith(label):
                match = re.search(r"[-\u2212]?\d+", spans[1].text)
                if match is not None:
                    return int(match.group().replace("\u2212", "-"))
        return None

    def parseConditions(self, html):
        parts = [self.parseForecastDesc(html)]
        temp = self.parseValue(html, "T. odczuw")
        if temp is not None:
            parts += [" _ ", "temperatura_odczuwalna", self.__language.read_temperature(temp)]
        clouds = self.parseValue(html, "Zachm")
        if clouds is not None:
            parts += [" _ ", "pokrywa_chmur", self.__language.read_percent(clouds)]
        wind = self.parseValue(html, "Wiatr")
        if wind is not None:
            parts += [" _ ", "predkosc_wiatru", self.__language.read_speed(wind, "kmph")]
        pressure = self.parseValue(html, "Ciśnienie")
        if pressure is not None:
            parts += [" _ ", "cisnienie", self.__language.read_pressure(pressure)]
        humidity = self.parseValue(html, "Wilgotno")
        if humidity is not None:
            parts += [" _ ", "wilgotnosc", self.__language.read_percent(humidity)]
        parts.append(" _ ")
        return " ".join(parts)

    def get_data(self):
        rawHtml = self.downloadFile(self.__service_url)
        soup = BeautifulSoup(rawHtml, "lxml")
        self.__logger.info("::: Przetwarzam dane...")
        now = soup.find_all("li", {"id": "wts_p0"})[0]
        after = soup.find_all("li", {"id": "wts_p3"})[0]
        forecast = soup.find_all("li", {"id": "wts_p13"})[0]
        message = ""
        if self.__saytime:
            message += " ".join(["stan_pogody_z_godziny", self.getHour(), " _ "])
        if self.__current:
            message += self.parseConditions(now)
        message += " ".join(
            [
                "prognoza_na_nastepne",
                "cztery",
                "godziny",
                " _ ",
                self.parseConditions(after),
                "prognoza_na_nastepne",
                "dwanascie",
                "godzin",
                " _ ",
                self.parseConditions(forecast),
            ]
        )
        return(
            {
                "message": message,
                "source": "pogoda_onet",
            }
        )