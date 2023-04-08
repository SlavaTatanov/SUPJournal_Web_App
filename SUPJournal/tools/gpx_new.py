import locale
import gpxpy
from folium import Map
from typing import BinaryIO


# Устанавливаем общее форматирование для даты - времени
locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

class SpeedValues:
    """
    Константы коэффициентов для перевода из (м/с) в target
    """
    KM_PER_HOUR = 3.6
    KNOT_PER_HOUR = 1.94

class GpxFile:
    def __init__(self, tr_date: str, tr_time: str, tr_dist: str, tr_avg_speed: str, tr_map: Map, tr_speed_plot: dict):
        self.date = tr_date
        self.time = tr_time
        self.dist = tr_dist
        self.avg_speed = tr_avg_speed
        self.map = tr_map
        self.speed_plot = tr_speed_plot

def gpx_file_builder(file: BinaryIO) -> GpxFile:
    gpx = gpx_parser(file)
    return gpx

def gpx_parser(file) -> gpxpy.gpx.GPX:
    """
    Парсит gpx файл
    """
    return gpxpy.parse(file)

