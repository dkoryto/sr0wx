# by SQ2IPS
from datetime import datetime, timedelta, timezone

from sr0wx_module import SR0WXModule
import logging


def parse_time_tag(tag):
    """Znacznik czasu SWPC (UTC) w kilku spotykanych formatach."""
    tag = tag.rstrip("Z").replace(" ", "T")
    if "." in tag:
        tag = tag.split(".")[0]
    return datetime.strptime(tag, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)


class SpaceWeather(SR0WXModule):
    """Moduł pobierający informacje o alertach pogody kosmicznej"""

    def __init__(self, language, urlG, urlR, urlS, geomagneticShort, radioNoise):
        self.__language = language
        self.__urlG = urlG
        self.__urlR = urlR
        self.__urlS = urlS
        self.__geomagneticShort = geomagneticShort
        self.__radioNoise = radioNoise
        self.__logger = logging.getLogger(__name__)

    def DownloadData(self, url):
        data = self.requestData(url, self.__logger)
        return data.json()

    def ProcessG(self, data):
        # SWPC zwracało listę list z nagłówkiem w pierwszym wierszu, teraz
        # zwraca listę obiektów -- obsługiwane są oba formaty
        if data and isinstance(data[0], list):
            header = data[0]
            data = [dict(zip(header, row)) for row in data[1:]]
        if not data:
            self.__logger.warning("Brak danych Kp")
            return None
        if self.__geomagneticShort:
            val = float(data[-1]["Kp"])
            self.__logger.info(
                f"Burze geomagnetyczne geomagnetyczne (chwilowe): Kp={val}, data: {data[-1]['time_tag']}"
            )
        else:
            since = datetime.now(timezone.utc) - timedelta(days=1)
            val_list = [float(d["Kp"]) for d in data if parse_time_tag(d["time_tag"]) >= since]
            if not val_list:
                self.__logger.warning("Brak danych Kp z ostatniej doby")
                return None
            val = max(val_list)
            self.__logger.info(f"Burze geomagnetyczne geomagnetyczne: Kp={val}")

        if val < 5:
            message = None
        elif val >= 5 and val < 6:
            message = "mal_e"
        elif val >= 6 and val < 7:
            message = "duz_e"
        elif val >= 7 and val < 8:
            message = "bardzo_duz_e"
        elif val >= 8 and val < 9:
            message = "silne"
        elif val >= 9:
            message = "ekstremalne"

        return message

    def ProcessR(self, data):
        # skala R NOAA jest zdefiniowana dla pasma 0.1-0.8 nm
        val_list = [float(d["flux"]) for d in data if d.get("energy", "0.1-0.8nm") == "0.1-0.8nm"]
        if not val_list:
            self.__logger.warning("Brak danych strumienia promieniowania X")
            return None
        val = max(val_list)
        self.__logger.info(f"zakłucenia jonosfery {val}")

        if val < 10**-5:
            message = None
        elif val >= 10**-5 and val < 5 * 10**-5:
            message = "mal_e"
        elif val >= 5 * 10**-5 and val < 10**-4:
            message = "duz_e"
        elif val >= 10**-4 and val < 10**-3:
            message = "bardzo_duz_e"
        elif val >= 10**-3 and val < 2 * 10**-3:
            message = "silne"
        elif val >= 2 * 10**-3:
            message = "ekstremalne"

        return message

    def ProcessS(self, data):
        # skala S NOAA jest zdefiniowana dla protonów >=10 MeV, ostatnie 6h
        since = datetime.now(timezone.utc) - timedelta(hours=6)
        val_list = [
            float(d["flux"])
            for d in data
            if d.get("energy", ">=10 MeV") == ">=10 MeV" and parse_time_tag(d["time_tag"]) >= since
        ]
        if not val_list:
            self.__logger.warning("Brak danych strumienia protonów z ostatnich 6h")
            return None
        val = max(val_list)

        self.__logger.info(f"Burze radiacyjne: {val}")

        if val < 10:
            message = None
        elif val >= 10 and val < 10**2:
            message = "mal_e"
        elif val >= 10**2 and val < 10**3:
            message = "duz_e"
        elif val >= 10**3 and val < 10**4:
            message = "bardzo_duz_e"
        elif val >= 10**4 and val < 10**5:
            message = "silne"
        elif val >= 10**5:
            message = "ekstremalne"
        return message

    def get_data(self):
        self.__logger.info("::: Pobieranie danych")
        if self.__radioNoise:
            dataR = self.DownloadData(self.__urlR)
        dataG = self.DownloadData(self.__urlG)
        dataS = self.DownloadData(self.__urlS)
        self.__logger.info("::: Przetważanie danych")
        dG = self.ProcessG(dataG)
        if self.__radioNoise:
            dR = self.ProcessR(dataR)
        else:
            dR = None
        dS = self.ProcessS(dataS)
        if dG is None and dR is None and dS is None:
            message = "brak_alerto_w_pogody_kosmicznej"
        else:
            message = "alerty_pogody_kosmicznej _ "
            if dG is not None:
                message += dG
                message += " burze_geomagnetyczne _ "
            if dR is not None:
                message += dR
                message += " zakl_ucenia_jonosfery _ "
            if dS is not None:
                message += dS
                message += " burze_radiacyjne "
        return(
            {
                "message": message,
                "source": "swpc",
            }
        )