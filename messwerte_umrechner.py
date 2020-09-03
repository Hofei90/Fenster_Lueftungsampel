"""
Modul zum Umrechnen der US Einheiten aus Weewx in das Metrische System
Version 0.1
"""

import math
from typing import Optional, Union


def temperaturumrechner(fahrenheit: Optional[Union[int, float]]) -> Optional[float]:
    """
    Umrechnung von Fahrenheit in Celsius
    :param fahrenheit: int, float or None
    :return: float or None
    """
    if isinstance(fahrenheit, (int, float)):
        celsius = (fahrenheit - 32) / 1.8
        celsius = round(celsius, 2)
        return celsius
    else:
        return None


def druckumrechner(inHG):
    """
    Umwandlung von inHG in mBar
    :param inHG: int, float or None
    :return: float or None
    """
    if isinstance(inHG, (int, float)):
        mbar = inHG * 33.86389
        mbar = round(mbar, 2)
        return mbar
    else:
        return None


def himmelsrichtungwandler(grad):
    """
    Umwandlung von Grad in Himmelsrichtung
    von (>)	bis (<=)
    N	348,75	11,25
    NNO	11,25	33,75
    NO	33,75	56,25
    ONO	56,25	78,75
    O	78,75	101,25
    OSO	101,25	123,75
    SO	123,75	146,25
    SSO	146,25	168,75
    S	168,75	191,25
    SSW	191,25	213,75
    SW	213,75	236,25
    WSW	236,25	258,75
    W	258,75	281,25
    WNW	281,25	303,75
    NW	303,75	326,25
    NNW	326,25	348,75
    :param grad: float or None
    :return: String or None
    """
    if isinstance(grad, (int, float)):
        richtung = ("N", "NNO", "NO", "ONO", "O", "OSO", "SO", "SSO", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
                    "N")
        return richtung[int((int(grad / (360 / 32)) + 1) / 2)]
    else:
        return None


def windumrechner(wind):
    """
    Umwandlung von milen pro std in km/h
    :param wind: Int, float or None
    :return: Float or None
    """
    if isinstance(wind, (int, float)):
        kmh = wind * 1.609346
        kmh = round(kmh, 2)
        return kmh
    else:
        return None


def regen_rate(wert):
    """
    Umwandlung von Inch/h in mm/h
    :param wert: Int, float or None
    :return: Float or None
    """
    if isinstance(wert, (int, float)):
        regenrate = wert * 25.4
        regenrate = round(regenrate, 2)
        return regenrate
    else:
        return None


def regen_menge(wert):
    """
    Umwandlung von Inch in mm
    :param wert: Int, float or None
    :return: Float or None
    """
    if isinstance(wert, (int, float)):
        regenmenge = wert * 25.4
        regenmenge = round(regenmenge, 2)
        return regenmenge
    else:
        return None


def magnus_formel_wasser(temperatur):
    sattdampfdruck_wasser = 611.2 * math.e ** ((17.62 * temperatur) / (243.12 + temperatur))
    return sattdampfdruck_wasser


def wasserdampf_partialdruck_berechnen(relative_feuchte, sattdampfdruck_wasser):
    wasserdampf_partialdruck = (relative_feuchte/100) * sattdampfdruck_wasser
    return wasserdampf_partialdruck


def celsius_in_kelvin(temperatur):
    kelvin = temperatur + 273.15
    return kelvin


def absolute_luftfeuchtigkeit(temperatur, relative_feuchte):
    """g/m³"""
    if temperatur is None or relative_feuchte is None:
        return
    sattdampfdruck_wasser = magnus_formel_wasser(temperatur)
    wasserdampf_partialdruck = wasserdampf_partialdruck_berechnen(relative_feuchte, sattdampfdruck_wasser)
    kelvin = celsius_in_kelvin(temperatur)
    abs_feuchte = round((wasserdampf_partialdruck / (461.51 * kelvin)) * 1000, 3)
    return abs_feuchte
