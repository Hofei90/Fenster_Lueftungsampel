# Fenster_Lueftungsampel

## Verwendungszweck

Der Sinn des Projektes besteht darin, mit Hilfe von 2 RGB LEDs zu visualisieren ob es sinnvoll ist in der Wohnung zu
lüften oder nicht.
Eine LED visualisiert die Temperatur, die zweite LED die absolute Luftfeuchtigkeit.
Als Datenquelle ist aktuell eine weeWx Datenbank vorgesehen. Aber es ist möglich auch seine eigene Datenquelle zu 
definieren sofern man darauf mit sqlite3, mariadb oder postgresql zugreifen kann.

Es gibt 3 verschiedene Zustände:

 * OK
 * Warnung
 * Kritisch

Für jeden Zustand lässt sich eine eigene Farbe definieren und ein Schwellwert.
 
## Hardware
Der Schaltplan und Platinendesign für den Nachbau der Lüftungsampel befinden sich unter [hardware](hardware)
Zusätzlich wird ein Raspberry Pi benötigt

## Installation

Ist der Speicherort nicht `/home/pi` so muss die Service Unit angepasst werden!

Betreten des gewünschten Installationsverzeichnisses am Raspberry Pi
Anschließend das Projekt auf den Pi laden.

`git clone https://github.com/Hofei90/Fenster_Lueftungsampel.git` 

Als nächstes die Modulabhängigkeiten installieren

`pip3 install -r requirements.txt` 

Die Konfigurationsvorlage kopieren und anschließend sorgfältig den gewünschten Gegebenheiten anpassen

```
cp vorlage_cfg.toml cfg.toml
nano cfg.toml
```

Die Systemd Files für den automatischen Start an den passenden Ort kopieren und aktivieren

```` 
cp /systemd_files/lampel.service /etc/systemd/system/
systemctl start lampel.service
systemctl enable lampel.service
````

## Simulationsmodus

Simulationsmodus zum Eingeben von manuellen Temperatur- und Feuchtigkeitswerten
mit:

````python3 lampl.py -s````

Der Simulationsmodus verwendet immer eine sqlite3 Datenbank welche im RAM erstellt wird. Werte gehen nach beenden
des Skriptes verloren 