# by SQ2IPS
import ephem
import datetime
import logging

from sr0wx_module import SR0WXModule

class SunRiseSet(SR0WXModule):
    """Moduł wyliczajacy wschody i zachody słońca"""

    def __init__(self, language, lat, lon, ele, pre, temp, hori):
        self.__language = language
        self.__lat = lat
        self.__lon = lon
        self.__ele = ele
        self.__pre = pre
        self.__temp = temp
        self.__hori = hori
        self.__logger = logging.getLogger(__name__)

    def hoursToNumbers(self, time="00:00"):
        datetime_object = datetime.datetime.strptime(time, "%H:%M")
        time_words = self.__language.read_datetime(datetime_object, "%H %M")
        return time_words

    def get_data(self):
        self.__logger.info("::: Przeliczam dane...")
        Gdynia = ephem.Observer()
        Gdynia.lat = str(self.__lat)
        Gdynia.lon = str(self.__lon)
        Gdynia.elevation = self.__ele
        Gdynia.pressure = self.__pre
        Gdynia.temp = self.__temp
        Gdynia.horizon = self.__hori
        # ephem traktuje datę jako UTC, czas lokalny przesuwał start
        # wyszukiwania i w oknie tuż przed wschodem/zachodem podawał
        # zdarzenie z następnego dnia
        Gdynia.date = ephem.now()
        sun = ephem.Sun()
        sunrise = " ".join(
            [
                "wscho_d_sl_on_ca",
                "godzina",
                self.hoursToNumbers(
                    str(ephem.localtime(Gdynia.next_rising(sun)).hour)
                    + ":"
                    + str(ephem.localtime(Gdynia.next_rising(sun)).minute)
                ),
                " ",
            ]
        )
        sunset = " ".join(
            [
                "zacho_d_sl_on_ca",
                "godzina",
                self.hoursToNumbers(
                    str(ephem.localtime(Gdynia.next_setting(sun)).hour)
                    + ":"
                    + str(ephem.localtime(Gdynia.next_setting(sun)).minute)
                ),
                " ",
            ]
        )
        message = " ".join(["kalendarium", "_", sunrise, "_", sunset])
        self.__logger.info(f"Wschód: {ephem.localtime(Gdynia.next_rising(sun))}")
        self.__logger.info(f"Zachód: {ephem.localtime(Gdynia.next_setting(sun))}")
        return(
            {
                "message": message,
                "source": "",
            }
        )
