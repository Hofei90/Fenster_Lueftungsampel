import os
import toml
import datetime
import gpiozero
import weewx_db_model as db
import time


def config_laden():
    configfile = os.path.join(SKRIPTPFAD, "cfg.toml")
    with open(configfile) as file:
        return toml.loads(file.read())


SKRIPTPFAD = os.path.abspath(os.path.dirname(__file__))
CONFIG = config_laden()


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
            self.status = status

    def _set_rgbled(self):
        if self.status == 0:
            self.rgbled.color = self.farben["ok"]
        elif self.status == 1:
            self.rgbled.color = self.farben["warnung"]
        else:
            self.rgbled.color = self.farben["kritisch"]

    def status_ermitteln(self, differenz, hysterese=0):
        if differenz <= self.differenz_ok - hysterese:
            status = 0
        elif differenz <= self.differenz_warnung - hysterese:
            status = 1
        else:
            status = 2
        return status

    def start_test(self):
        for status in range(3):
            self.status = status
            self._set_rgbled()
            time.sleep(2)
        self.status = 0


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


def temp_auslesen(spalte):
    temp = db.Archive.select(temp_mapping(spalte))\
        .order_by(db.Archive.date_time.desc()).limit(1).execute()[0]
    return temp


def feuchte_auslesen(spalte):
    feuchte = db.Archive.select(feuchte_mapping(spalte))\
        .order_by(db.Archive.date_time.desc()).limit(1).execute()[0]
    return feuchte


def differenz_berechnen(aussen, innen):
    differenz = aussen - innen
    return differenz


def temp_differenz():
    aussen = temp_auslesen(CONFIG["spaltenname"]["temp_aussen"])
    innen = temp_auslesen(CONFIG["spaltenname"]["temp_innen"])
    differenz = differenz_berechnen(aussen, innen)
    return differenz


def feuchte_differenz():
    aussen = temp_auslesen(CONFIG["spaltenname"]["feuchte_aussen"])
    innen = temp_auslesen(CONFIG["spaltenname"]["feuchte_innen"])
    differenz = differenz_berechnen(aussen, innen)
    return differenz


def main():
    db_adapter = CONFIG["weewx"]["db"]
    db_ = db.init_db(CONFIG["weewx"][db_adapter]["database"], db_adapter, CONFIG["weewx"].get(db_adapter))
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
    while True:
        now = datetime.datetime.now()
        if (int(now.strftime("%M")) - 1) % 5 == 0:
            temp_ampel.set_status(temp_differenz())
            feuchte_ampel.set_status(feuchte_differenz())
        time.sleep(25)


if __name__ == "__main__":
    main()

