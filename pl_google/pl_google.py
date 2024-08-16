# -*- coding: utf-8 -*-
#
#   Copyright 2009-2014 Michal Sadowski (sq6jnx at hamradio dot pl)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import sys

sys.path.append("./pyliczba/")

import pyliczba
from six import u
import datetime
from functools import wraps


def rmv_pl_chars(string):
    return "".join([i if ord(i) < 128 else "_" for i in string]).lower()


def ra(value):
    return (
        value.replace(u("ą"), "a")
        .replace(u("Ą"), "a")
        .replace(u("ć"), "c")
        .replace(u("Ć"), "c")
        .replace(u("ę"), "e")
        .replace(u("Ę"), "e")
        .replace(u("ł"), "l")
        .replace(u("Ł"), "l")
        .replace(u("ń"), "n")
        .replace(u("Ń"), "n")
        .replace(u("ó"), "o")
        .replace(u("Ó"), "o")
        .replace(u("ś"), "s")
        .replace(u("Ś"), "s")
        .replace(u("ź"), "z")
        .replace(u("Ź"), "z")
        .replace(u("ż"), "z")
        .replace(u("Ż"), "z")
        .lower()
    )


def trim_pl(text):
    text = (
        text.lower()
        .replace(("ą"), "a_")
        .replace(("ć"), "c_")
        .replace(("ę"), "e_")
        .replace(("ł"), "l_")
        .replace(("ń"), "n_")
        .replace(("ó"), "o_")
        .replace(("ś"), "s_")
        .replace(("ź"), "x_")
        .replace(("ż"), "z_")
        .replace(":", "")
        .replace(",", "")
        .replace(".", "")
        .replace(" - ", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(" ", "_")
    )
    return "".join(text.split())


def remove_accents(function):
    """unicodedata.normalize() doesn't work with ł and Ł"""

    @wraps(function)
    def wrapper(*args, **kwargs):
        return ra(function(*args, **kwargs))

    return wrapper


def _(text):
    return text.replace(" ", "_")


class SR0WXLanguage(object):
    def __init__(self):
        """Nothing here for now."""
        pass


class PLGoogle(SR0WXLanguage):
    def __init__(self):
        pass

    @remove_accents
    def read_number(self, value, units=None):
        """Converts numbers to text."""
        if units is None:
            retval = pyliczba.lslownie(abs(value))
        else:
            retval = pyliczba.cosslownie(abs(value), units)

        if retval.startswith(u("jeden tysiąc")):
            retval = retval.replace(u("jeden tysiąc"), u("tysiąc"))
        if value < 0:
            retval = " ".join(("minus", retval))
        return retval

    @remove_accents
    def read_gust(self, f):
        f = str(f)
        d = {
            "1": "jeden",
            "2": "dwoch",
            "3": "trzech",
            "4": "czterech",
            "5": "pieciu",
            "6": "szesciu",
            "7": "siedmiu",
            "8": "osmiu",
            "9": "dziewieciu",
            "10": "dziesieciu",
            "11": "jedenastu",
            "12": "dwunastu",
            "13": "trzynastu",
            "14": "czternastu",
            "15": "pietnastu",
            "16": "szesnastu",
            "17": "siedemnastu",
            "18": "osiemnastu",
            "19": "dziewietnastu",
            "20": "dwudziestu",
            "30": "trzydziestu",
            "40": "czterdziestu",
            "50": "piecdziesieciu",
            "60": "szejscdziesieciu",
            "70": "siedemdziesieciu",
            "80": "osiemdziesieciu",
            "90": "dziewiecdziesieciu",
            "100": "stu",
            "200": "dwustu",
            "300": "trzystu",
            "400": "czterystu",
            "500": "pieciuset",
            "600": "szesciuset",
            "700": "siedmiuset",
            "800": "osmiuset",
            "900": "dziewieciuset",
        }
        if len(f) == 1:
            if f == "1":
                return "jednego kilometra_na_godzine"
            else:
                return d[f] + " kilometrow_na_godzine"
        elif len(f) == 2:
            if f[1] == "0" or f[0] == "1":
                return d[f] + " kilometrow_na_godzine"
            else:
                return d[f[0] + "0"] + " " + d[f[1]] + " kilometrow_na_godzine"
        elif len(f) == 3:
            if f[1] == "0" and f[2] == "0":
                return d[f] + " kilometrow_na_godzine"
            else:
                if f[2] != "0":
                    if f[1] == "0":
                        return d[f[0] + "00"] + " " + d[f[2]] + " kilometrow_na_godzine"
                    else:
                        return (
                            d[f[0] + "00"]
                            + " "
                            + d[f[1] + "0"]
                            + " "
                            + d[f[2]]
                            + " kilometrow_na_godzine"
                        )
                else:
                    if f[1] == "0":
                        return d[f[0] + "00"] + " kilometrow_na_godzine"
                    else:
                        return (
                            d[f[0] + "00"]
                            + " "
                            + d[f[1] + "0"]
                            + " kilometrow_na_godzine"
                        )

    @remove_accents
    def read_pressure(self, value):
        hPa = ["hektopaskal", "hektopaskale", "hektopaskali"]
        return self.read_number(value, hPa)

    @remove_accents
    def read_distance(self, value):
        hPa = ["kilometr", "kilometry", "kilometrow"]
        return self.read_number(value, hPa)

    @remove_accents
    def read_percent(self, value):
        percent = ["procent", "procent", "procent"]
        return self.read_number(value, percent)

    @remove_accents
    def read_temperature(self, value):
        C = [_(u("stopień Celsjusza")), _("stopnie Celsjusza"), _("stopni Celsjusza")]
        return read_number(value, C)

    @remove_accents
    def read_speed(self, no, unit="mps"):
        units = {
            "mps": [
                _(u("metr na sekundę")),
                _(u("metry na sekundę")),
                _(u("metrów na sekundę")),
            ],
            "kmph": [
                _(u("kilometr na godzinę")),
                _(u("kilometry na godzinę")),
                _(u("kilometrów na godzinę")),
            ],
        }
        return read_number(no, units[unit])

    @remove_accents
    def read_precipitation(self, value):
        units = [_(u("milimetr")), _(u("milimetry")), _(u("milimetrów"))]
        return read_number(value, units)

    @remove_accents
    def read_power(self, value, prefix):
        units = [_(u("wat")), _(u("waty")), _(u("watow"))]
        for i, unit in enumerate(units):
            units[i] = "_".join([prefix, unit])
        return read_number(value, units)

    @remove_accents
    def read_degrees(self, value):
        deg = [u("stopień"), u("stopnie"), u("stopni")]
        return read_number(value, deg)

    @remove_accents
    def read_micrograms(self, value):
        deg = [
            u("mikrogram na_metr_szes_cienny"),
            u("mikrogramy na_metr_szes_cienny"),
            u("mikrogramo_w na_metr_szes_cienny"),
        ]
        return read_number(value, deg)

    @remove_accents
    def read_decimal(self, value):
        deg100 = [
            u("setna"),
            u("setne"),
            u("setnych"),
        ]

        deg10 = [
            u("dziesia_ta"),
            u("dziesia_te"),
            u("dziesia_tych"),
        ]
        if value >= 10:
            return read_number(value, deg100)
        else:
            return read_number(value, deg10)

    @remove_accents
    def read_direction(self, value, short=False):
        directions = {
            "N": (u("północno"), u("północny")),
            "E": (u("wschodnio"), u("wschodni")),
            "W": (u("zachodnio"), u("zachodni")),
            "S": (u("południowo"), u("południowy")),
        }
        if short:
            value = value[-2:]
        return "-".join(
            [
                directions[d][0 if i < 0 else 1]
                for i, d in enumerate(value, -len(value) + 1)
            ]
        )

    @remove_accents
    def read_validity_hour(self, hour):
        hours = [
            u("godzine"),
            u("godziny"),
            u("godzin"),
        ]
        if hour == 1:
            return hours[0]
        elif hour == 2:
            return " ".join(["dwie", hours[1]])
        else:
            return read_number(hour, hours)

    @remove_accents
    def read_datetime(self, value, out_fmt, in_fmt=None):
        if type(value) != datetime.datetime and in_fmt is not None:
            value = datetime.datetime.strptime(value, in_fmt)
        elif type(value) == datetime.datetime:
            pass
        else:
            raise TypeError(
                "Either datetime must be supplied or both " "value and in_fmt"
            )

        MONTHS = [
            u(""),
            u("stycznia"),
            u("lutego"),
            u("marca"),
            u("kwietnia"),
            u("maja"),
            u("czerwca"),
            u("lipca"),
            u("sierpnia"),
            u("września"),
            u("października"),
            u("listopada"),
            u("grudnia"),
        ]

        DAYS_N0 = [
            u(""),
            u(""),
            u("dwudziestego"),
            u("trzydziestego"),
        ]
        DAYS_N = [
            u(""),
            u("pierwszego"),
            u("drugiego"),
            u("trzeciego"),
            u("czwartego"),
            u("piątego"),
            u("szóstego"),
            u("siódmego"),
            u("ósmego"),
            u("dziewiątego"),
            u("dziesiątego"),
            u("jedenastego"),
            u("dwunastego"),
            u("trzynastego"),
            u("czternastego"),
            u("piętnastego"),
            u("szesnastego"),
            u("siedemnastego"),
            u("osiemnastego"),
            u("dziewiętnastego"),
        ]
        HOURS = [
            u("zero"),
            u("pierwsza"),
            u("druga"),
            u("trzecia"),
            u("czwarta"),
            u("piąta"),
            u("szósta"),
            u("siódma"),
            u("ósma"),
            u("dziewiąta"),
            u("dziesiąta"),
            u("jedenasta"),
            u("dwunasta"),
            u("trzynasta"),
            u("czternasta"),
            u("piętnasta"),
            u("szesnasta"),
            u("siedemnasta"),
            u("osiemnasta"),
            u("dziewiętnasta"),
            u("dwudziesta"),
        ]

        _, tm_mon, tm_mday, tm_hour, tm_min, _, _, _, _ = value.timetuple()
        retval = []
        for word in out_fmt.split(" "):
            if word == "%d":  # Day of the month
                if tm_mday <= 20:
                    retval.append(DAYS_N[tm_mday])
                else:
                    retval.append(DAYS_N0[tm_mday // 10])
                    retval.append(DAYS_N[tm_mday % 10])
            elif word == "%B":  # Month as locale’s full name
                retval.append(MONTHS[tm_mon])
            elif word == "%H":  # Hour (24-hour clock) as a decimal number
                if tm_hour <= 20:
                    retval.append(HOURS[tm_hour])
                elif tm_hour > 20:
                    retval.append(HOURS[20])
                    retval.append(HOURS[tm_hour - 20])
            elif word == "%M":  # Minute as a decimal number
                if tm_min == 0:
                    retval.append(u("zero-zero"))
                else:
                    retval.append(read_number(tm_min))
            elif word.startswith("%"):
                raise ValueError("Token %s' is not supported!", word)
            else:
                retval.append(word)
        return " ".join((w for w in retval if w != ""))

    @remove_accents
    def read_callsign(self, value):
        # literowanie polskie wg. "Krótkofalarstwo i radiokomunikacja - poradnik",
        # Łukasz Komsta SQ8QED, Wydawnictwa Komunikacji i Łączności Warszawa, 2001,
        # str. 130
        LETTERS = {
            "a": u("adam"),
            "b": u("barbara"),
            "c": u("celina"),
            "d": u("dorota"),
            "e": u("edward"),
            "f": u("franciszek"),
            "g": u("gustaw"),
            "h": u("henryk"),
            "i": u("irena"),
            "j": u("józef"),
            "k": u("karol"),
            "l": u("ludwik"),
            "m": u("marek"),
            "n": u("natalia"),
            "o": u("olga"),
            "p": u("paweł"),
            "q": u("quebec"),
            "r": u("roman"),
            "s": u("stefan"),
            "t": u("tadeusz"),
            "u": u("urszula"),
            "v": u("violetta"),
            "w": u("wacław"),
            "x": u("xawery"),
            "y": u("ypsilon"),
            "z": u("zygmunt"),
            "/": u("łamane"),
        }
        retval = []
        for char in value.lower():
            try:
                retval.append(LETTERS[char])
            except KeyError:
                try:
                    retval.append(read_number(int(char)))
                except ValueError:
                    raise ValueError('"%s" is not a element of callsign', char)
        return " ".join(retval)


# ##########################################
#
# module dependant words
# #############################################


# World Weather Online

wwo_weather_codes = {
    # Clear/Sunny
    "113": _(ra(u("bezchmurnie"))),
    # Partly Cloudy
    "116": _(ra(u("częściowe zachmurzenie"))),
    # Cloudy
    "119": _(ra(u("pochmurno"))),
    # Overcast
    "122": _(ra(u("zachmurzenie całkowite"))),
    "143": _(ra(u("zamglenia"))),  # Mist
    # Patchy rain nearby
    "176": _(ra(u("lokalne przelotne opady deszczu"))),
    # Patchy snow nearby
    "179": _(ra(u("śnieg"))),
    # Patchy sleet nearby
    "182": _(ra(u("śnieg z deszczem"))),
    # Patchy freezing drizzle nearby
    "185": _(ra(u("lokalna przelotna marznąca mżawka"))),
    # Thundery outbreaks in nearby
    "200": _(ra(u("lokalne burze"))),
    # Blowing snow
    "227": _(ra(u("zamieć śnieżna"))),
    # Blizzard
    "230": _(ra(u("zamieć śnieżna"))),
    "248": _(ra(u("mgła"))),  # Fog
    # Freezing fog
    "260": _(ra(u("marznąca mgła"))),
    # Patchy light drizzle
    "263": _(ra(u("mżawka"))),
    # Light drizzle
    "266": _(ra(u("mżawka"))),
    # Freezing drizzle
    "281": _(ra(u("marznąca mżawka"))),
    # Heavy freezing drizzle
    "284": _(ra(u("marznąca mżawka"))),
    # Patchy light rain
    "293": _(ra(u("lokalny słaby deszcz"))),
    # Light rain
    "296": _(ra(u("słaby deszcz"))),
    # Moderate rain at times
    "299": _(ra(u("przelotne opady deszczu"))),
    # Moderate rain
    "302": _(ra(u("umiarkowane opady deszczu"))),
    # Heavy rain at times
    "305": _(ra(u("przelotne ulewy"))),
    # Heavy rain
    "308": _(ra(u("ulewy"))),
    # Light freezing rain
    "311": _(ra(u("słabe opady marznącego deszczu"))),
    # Moderate or Heavy freezing rain
    "314": _(ra(u("umiarkowane opady marznącego deszczu"))),
    # Light sleet
    "317": _(ra(u("słabe opady śniegu z deszczem"))),
    # Moderate or heavy sleet
    "320": _(ra(u("umiarkowane lub ciężkie opady śniegu z deszczem"))),
    # Patchy light snow
    "323": _(ra(u("słabe opady śniegu"))),
    # Light snow
    "326": _(ra(u("słabe opady śniegu"))),
    # Patchy moderate snow
    "329": _(ra(u("umiarkowane opady śniegu"))),
    # Moderate snow
    "332": _(ra(u("umiarkowane opady śniegu"))),
    # Patchy heavy snow
    "335": _(ra(u("opady śniegu"))),
    # Heavy snow
    "338": _(ra(u("intensywne_opady_sniegu"))),
    # Ice pellets
    "350": _(ra(u("grad"))),
    # Light rain shower
    "353": _(ra(u("słabe przelotne opady deszczu"))),
    # Moderate or heavy rain shower
    "356": _(ra(u("przelotne opady deszczu"))),
    # Torrential rain shower
    "359": _(ra(u("ulewny deszcz"))),
    # Light sleet showers
    "362": _(ra(u("słabe opady śniegu z deszczem"))),
    # Moderate or heavy sleet showers
    "365": _(ra(u("umiarkowane opady śniegu z deszczem"))),
    # Light snow showers
    "368": _(ra(u("słabe opady śniegu"))),
    # Moderate or heavy snow showers
    "371": _(ra(u("umiarkowane opady śniegu"))),
    # Light showers of ice pellets
    "374": _(ra(u("słabe opady śniegu ziarnistego"))),
    # Moderate or heavy showers of ice pellets
    "377": _(ra(u("umiarkowane opady śniegu ziarnistego"))),
    # Patchy light rain in area with thunder
    "386": _(ra(u("burza"))),
    # Moderate or heavy rain in area with thunder
    "389": _(ra(u("burza"))),
    # Patchy light snow in area with thunder
    "392": _(ra(u("burza śnieżna"))),
    # Moderate or heavy snow in area with thunder
    "395": _(ra(u("burza śnieżna"))),
}


# to be removed from code
source = "zrodlo"

pl = PLGoogle()

read_number = pl.read_number
read_pressure = pl.read_pressure
read_distance = pl.read_distance
read_percent = pl.read_percent
read_temperature = pl.read_temperature
read_speed = pl.read_speed
read_gust = pl.read_gust
read_precipitation = pl.read_precipitation
read_degrees = pl.read_degrees
read_micrograms = pl.read_micrograms
read_decimal = pl.read_decimal
read_direction = pl.read_direction
read_validity_hour = pl.read_validity_hour
read_datetime = pl.read_datetime
read_callsign = pl.read_callsign
read_power = pl.read_power
