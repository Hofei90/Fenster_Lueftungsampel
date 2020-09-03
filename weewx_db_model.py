from peewee import *

database = Proxy()


class UnknownField(object):
    def __init__(self, *_, **__): pass


class BaseModel(Model):
    class Meta:
        database = database


class Archive(BaseModel):
    et = FloatField(column_name='ET', null=True)
    uv = FloatField(column_name='UV', null=True)
    altimeter = FloatField(null=True)
    barometer = FloatField(null=True)
    cons_battery_voltage = FloatField(column_name='consBatteryVoltage', null=True)
    date_time = AutoField(column_name='dateTime')
    dewpoint = FloatField(null=True)
    extra_humid1 = FloatField(column_name='extraHumid1', null=True)
    extra_humid2 = FloatField(column_name='extraHumid2', null=True)
    extra_temp1 = FloatField(column_name='extraTemp1', null=True)
    extra_temp2 = FloatField(column_name='extraTemp2', null=True)
    extra_temp3 = FloatField(column_name='extraTemp3', null=True)
    hail = FloatField(null=True)
    hail_rate = FloatField(column_name='hailRate', null=True)
    heatindex = FloatField(null=True)
    heating_temp = FloatField(column_name='heatingTemp', null=True)
    heating_voltage = FloatField(column_name='heatingVoltage', null=True)
    in_humidity = FloatField(column_name='inHumidity', null=True)
    in_temp = FloatField(column_name='inTemp', null=True)
    in_temp_battery_status = FloatField(column_name='inTempBatteryStatus', null=True)
    interval = IntegerField()
    leaf_temp1 = FloatField(column_name='leafTemp1', null=True)
    leaf_temp2 = FloatField(column_name='leafTemp2', null=True)
    leaf_wet1 = FloatField(column_name='leafWet1', null=True)
    leaf_wet2 = FloatField(column_name='leafWet2', null=True)
    out_humidity = FloatField(column_name='outHumidity', null=True)
    out_temp = FloatField(column_name='outTemp', null=True)
    out_temp_battery_status = FloatField(column_name='outTempBatteryStatus', null=True)
    pressure = FloatField(null=True)
    radiation = FloatField(null=True)
    rain = FloatField(null=True)
    rain_battery_status = FloatField(column_name='rainBatteryStatus', null=True)
    rain_rate = FloatField(column_name='rainRate', null=True)
    reference_voltage = FloatField(column_name='referenceVoltage', null=True)
    rx_check_percent = FloatField(column_name='rxCheckPercent', null=True)
    soil_moist1 = FloatField(column_name='soilMoist1', null=True)
    soil_moist2 = FloatField(column_name='soilMoist2', null=True)
    soil_moist3 = FloatField(column_name='soilMoist3', null=True)
    soil_moist4 = FloatField(column_name='soilMoist4', null=True)
    soil_temp1 = FloatField(column_name='soilTemp1', null=True)
    soil_temp2 = FloatField(column_name='soilTemp2', null=True)
    soil_temp3 = FloatField(column_name='soilTemp3', null=True)
    soil_temp4 = FloatField(column_name='soilTemp4', null=True)
    supply_voltage = FloatField(column_name='supplyVoltage', null=True)
    tx_battery_status = FloatField(column_name='txBatteryStatus', null=True)
    us_units = IntegerField(column_name='usUnits')
    wind_battery_status = FloatField(column_name='windBatteryStatus', null=True)
    wind_dir = FloatField(column_name='windDir', null=True)
    wind_gust = FloatField(column_name='windGust', null=True)
    wind_gust_dir = FloatField(column_name='windGustDir', null=True)
    wind_speed = FloatField(column_name='windSpeed', null=True)
    windchill = FloatField(null=True)

    class Meta:
        table_name = 'archive'


def init_db(name, type_="sqlite", config=None):
    config = config or {}
    drivers = {
        "sqlite": SqliteDatabase,
        "mysql": MySQLDatabase,
    }

    try:
        cls = drivers[type_]
    except KeyError:
        raise ValueError("Unknown database type: {}".format(type_)) from None
    del config["database"]
    db = cls(name, **config)
    return db