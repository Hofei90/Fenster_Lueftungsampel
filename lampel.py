import datetime
import os
import sys
import time

import gpiozero
import toml

import weewx_db_model as db
import setup_logging
import messwerte_umrechner as mwu


def config_laden():
    configfile = os.path.join(SKRIPTPFAD, "cfg.toml")
    with open(configfile) as file:
        return toml.loads(file.read())


SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))
CONFIG = config_laden()
LOGGER = setup_logging.create_logger("lampel", CONFIG["loglevel"], SKRIPTPFAD)


class Ampel:
    def __init__(self, rgbled, differenz_ok, differenz_warnung, hysterese, farben):
        self.rgbled = rgbled
        self.status = 0
        self.differenz_ok = differenz_ok
        self.differenz_warnung = differenz_warnung
        self.hysterese = hysterese
        self.farben = farben
        self.start_test()
        
    def set_status(self, differenz):
        status = self.status_ermitteln(differenz)
        if status < self.status:
            status = self.status_ermitteln(differenz, self.hysterese)
        if status != self.status:
            LOGGER.debug(f"Statusänderung von {self.status} auf {status}")
            self.status = status
            self._set_rgbled()

    def _set_rgbled(self):
        if self.status == 0:
            self.rgbled.color = self.farben["ok"]
            LOGGER.debug(f"RGB Farbe Ok: {self.rgbled.color}")
        elif self.status == 1:
            self.rgbled.color = self.farben["warnung"]
            LOGGER.debug(f"RGB Farbe Warnung: {self.rgbled.color}")
        else:
            self.rgbled.color = self.farben["kritisch"]
            LOGGER.debug(f"RGB Farbe Kritisch: {self.rgbled.color}")

    def status_ermitteln(self, differenz, hysterese=0):
        if differenz <= self.differenz_ok - hysterese:
            status = 0
        elif differenz <= self.differenz_warnung - hysterese:
            status = 1
        else:
            status = 2
        LOGGER.debug(f"Status: {status}")
        return status

    def start_test(self):
        for status in range(3):
            self.status = status
            self._set_rgbled()
            time.sleep(2)
        self.status = 0
        self._set_rgbled()


class Messwert:
    def __init__(self):
        self.aussen = 0
        self.innen = 0
        self.us_unit = 1

    def set_aussen(self, wert):
        self.aussen = wert

    def set_innen(self, wert):
        self.innen = wert

    def set_us_unit(self, wert):
        self.us_unit = wert


def temp_mapping(name):
    if name == "extra_temp1":
        spalte = db.Archive.extra_temp1
    elif name == "extra_temp2":
        spalte = db.Archive.extra_temp2
    elif name == "extra_temp3":
        spalte = db.Archive.extra_temp3
    elif name == "in_temp":
        spalte = db.Archive.in_temp
    elif name == "out_temp":
        spalte = db.Archive.out_temp
    else:
        raise ValueError(f"Spaltenname {name} unbekannt")
    return spalte


def feuchte_mapping(name):
    if name == "out_humidity":
        spalte = db.Archive.out_humidity
    elif name == "in_humidity":
        spalte = db.Archive.in_humidity
    elif name == "extra_humid1":
        spalte = db.Archive.extra_humid1
    elif name == "extra_humid2":
        spalte = db.Archive.extra_humid2
    else:
        raise ValueError(f"Spaltenname {name} unbekannt")
    return spalte


def rgb_initialisieren(led_nr):
    rgb = gpiozero.RGBLED(CONFIG["led"][led_nr]["pincfg"]["r"],
                          CONFIG["led"][led_nr]["pincfg"]["g"],
                          CONFIG["led"][led_nr]["pincfg"]["b"])
    return rgb


def farben_initialisieren(led_nr):
    return CONFIG["led"][led_nr]["farben"]


def us_units_auslesen(temp, feuchte):
    us_units = db.Archive.select(db.Archive.us_units)\
        .order_by(db.Archive.date_time.desc()).limit(1).scalar()
    temp.set_us_unit(us_units)
    feuchte.set_us_unit(us_units)


def temp_auslesen(spalte, us_units):
    temp = db.Archive.select(temp_mapping(spalte))\
        .order_by(db.Archive.date_time.desc()).limit(1).scalar()
    if us_units:
        temp = mwu.temperaturumrechner(temp)
    return temp


def feuchte_auslesen(spalte):
    feuchte = db.Archive.select(feuchte_mapping(spalte))\
        .order_by(db.Archive.date_time.desc()).limit(1).scalar()
    return feuchte


def sim_daten_schreiben(datadict):
    db.Archive.create(**datadict)


def differenz_berechnen(aussen, innen):
    differenz = aussen - innen
    return differenz


def temp_differenz(temp):
    aussen = temp_auslesen(CONFIG["spaltenname"]["temp_aussen"], temp.us_unit)
    innen = temp_auslesen(CONFIG["spaltenname"]["temp_innen"], temp.us_unit)
    differenz = differenz_berechnen(aussen, innen)
    temp.set_aussen(aussen)
    temp.set_innen(innen)
    LOGGER.debug(f"Temperatur außen: {aussen}; innen: {innen}, Differenz: {differenz}")
    return differenz


def feuchte_differenz(temp, feuchte):
    rel_aussen = feuchte_auslesen(CONFIG["spaltenname"]["feuchte_aussen"])
    rel_innen = feuchte_auslesen(CONFIG["spaltenname"]["feuchte_innen"])
    feuchte.set_aussen(rel_aussen)
    feuchte.set_innen(rel_innen)

    abs_aussen = mwu.absolute_luftfeuchtigkeit(temp.aussen, rel_aussen)
    abs_innen = mwu.absolute_luftfeuchtigkeit(temp.innen, rel_innen)

    abs_differenz = differenz_berechnen(abs_aussen, abs_innen)
    LOGGER.debug(f"rel. Luftfeuchtigkeit außen: {rel_aussen}; innen: {rel_innen}")
    LOGGER.debug(f"abs. Luftfeuchtigkeit außen: {abs_aussen}; innen: {abs_innen}, Differenz: {abs_differenz}")

    return abs_differenz


def wert_eingabe(text):
    value = 0
    format_falsch = True
    while format_falsch:
        try:
            value = float(input(f"Bitte {text} eingeben: "))
        except ValueError:
            print("Falsches Format")
        else:
            format_falsch = False
    return value


def sim_daten_eingabe():
    daten_dict = {
        CONFIG["spaltenname"]["temp_innen"]: wert_eingabe("Temperatur innen"),
        CONFIG["spaltenname"]["temp_aussen"]: wert_eingabe("Temperatur außen"),
        CONFIG["spaltenname"]["feuchte_innen"]: wert_eingabe("Luftfeuchtigkeit innen"),
        CONFIG["spaltenname"]["feuchte_aussen"]: wert_eingabe("Luftfeuchtigkeit außen"),
        "date_time": datetime.datetime.now().timestamp(),
        "interval": 1,
        "us_units": 1}
    return daten_dict


def main():
    try:
        if sys.argv[1] == "-s":
            simulationsmodus = True
        else:
            simulationsmodus = False
    except IndexError:
        simulationsmodus = False
    if not simulationsmodus:
        db_adapter = CONFIG["weewx"]["db"]
        db_ = db.init_db(CONFIG["weewx"][db_adapter]["database"], db_adapter, CONFIG["weewx"].get(db_adapter))
    else:
        db_ = db.SqliteDatabase(":memory:")
    db.database.initialize(db_)

    temp_ampel = Ampel(rgb_initialisieren(CONFIG["led"]["mapping"]["temp_anzeige"]),
                       CONFIG["differenz"]["temp"]["ok"],
                       CONFIG["differenz"]["temp"]["warnung"],
                       CONFIG["differenz"]["temp"]["hysterese"],
                       farben_initialisieren(CONFIG["led"]["mapping"]["temp_anzeige"]))
    feuchte_ampel = Ampel(rgb_initialisieren(CONFIG["led"]["mapping"]["feuchte_anzeige"]),
                          CONFIG["differenz"]["feuchte"]["ok"],
                          CONFIG["differenz"]["feuchte"]["warnung"],
                          CONFIG["differenz"]["feuchte"]["hysterese"],
                          farben_initialisieren(CONFIG["led"]["mapping"]["feuchte_anzeige"]))
    if not simulationsmodus:
        exc = False
        while True:
            now = datetime.datetime.now()
            if (int(now.strftime("%M")) - 1) % 5 == 0:
                if not exc:
                    temp = Messwert()
                    feuchte = Messwert()
                    us_units_auslesen(temp, feuchte)
                    temp_ampel.set_status(temp_differenz(temp))
                    feuchte_ampel.set_status(feuchte_differenz(temp, feuchte))
                    del temp, feuchte
                    exc = True
            else:
                if exc:
                    exc = False
            time.sleep(25)
    else:
        while True:
            temp = Messwert()
            feuchte = Messwert()
            db.database.create_tables([db.Archive])
            sim_daten_schreiben(sim_daten_eingabe())
            us_units_auslesen(temp, feuchte)
            temp_ampel.set_status(temp_differenz(temp))
            feuchte_ampel.set_status(feuchte_differenz(temp, feuchte))


if __name__ == "__main__":
    main()
