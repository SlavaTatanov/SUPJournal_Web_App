import locale
import asyncio
import gpxpy
from folium import Map
from typing import BinaryIO
import httpx
import time
from SUPJournal.tools.gpx import GpxFile as OldGPXFile
from geopy.distance import geodesic


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
    coord, coord_per_hour = gpx_get_coord(gpx)
    med_coord = get_med_coord(coord)
    weather, med_min_max_pt, zoom, dist = asyncio.run(async_block(med_coord, coord, gpx))
    return gpx

def gpx_parser(file) -> gpxpy.gpx.GPX:
    """
    Парсит gpx файл
    """
    return gpxpy.parse(file)

def gpx_get_coord(gpx: gpxpy.gpx.GPX) -> tuple:
    """
    Получаем (список координат со словарем (lon, lat, time, speed) &&
    словарь с координатами в каждый час(для погоды))
    """
    gpx_data = []
    coord_per_hour = []
    last_point = None
    last_time = None
    delta_time_points = None
    current_time = None
    for tracks in gpx.tracks:
        for segments in tracks.segments:
            for point in segments.points:
                if last_point is None:
                    last_point = gpxpy.gpx.GPXTrackPoint(point.latitude, point.longitude, time=point.time)
                    last_time = point.time
                    delta_time_points = point.time - point.time
                    current_time = delta_time_points
                speed = point.speed_between(last_point)
                current_time += delta_time_points
                if speed is not None:
                    speed = round(speed, 2)
                gpx_data.append({"coord": [point.latitude, point.longitude],
                                 "speed": speed,
                                 "time": current_time,
                                 "date": point.time})
                last_point = gpxpy.gpx.GPXTrackPoint(point.latitude, point.longitude, time=point.time)
                delta_time_points = point.time - last_time
                last_time = point.time
    return gpx_data, coord_per_hour

def get_med_coord(coord: list):
    """
    Ищем среднюю координату и дату тренировки, делаем запрос погоды
    """
    med_position = len(coord) // 2
    return {"date": coord[med_position]["date"].date(),
            "lat": coord[med_position]["coord"][0], "lon": coord[med_position]["coord"][1]}

async def get_weather(med_coord: dict):
    """
    Запрос погоды к api, если тренировка давняя то запрос к архивам api
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {"latitude": med_coord["lat"], "longitude": med_coord["lon"],
              "start_date": med_coord["date"], "end_date": med_coord["date"],
              "hourly": "temperature_2m"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 400:
            url = "https://archive-api.open-meteo.com/v1/archive"
            resp = await client.get(url, params=params)
    return resp.json()

async def get_med_min_max_point(coord):
    """
    Средняя, минимальная, максимальная точки
    """
    lat = [item["coord"][0] for item in coord]
    lon = [item["coord"][1] for item in coord]
    lat = {"min": min(lat), "max": max(lat)}
    lon = {"min": min(lon), "max": max(lon)}
    min_point = (lat["min"], lon["min"])
    max_point = (lat["max"], lon["max"])
    lat = round((lat["min"] + lat["max"]) / 2, 6)
    lon = round((lon["min"] + lon["max"]) / 2, 6)
    med_point = (lat, lon)
    return {"med_point": med_point, "min_point": min_point, "max_point": max_point}

async def find_zoom(max_min_points: dict) -> int:
    """Поиск уровня увеличения для карты"""
    dist = geodesic(max_min_points["min_point"], max_min_points["max_point"]).km
    if dist <= 2:
        return 15
    if dist <= 4:
        return 16
    if dist <= 8:
        return 13
    if dist <= 15:
        return 12
    if dist <= 30:
        return 11
    else:
        return 10

async def get_dist(gpx: gpxpy.gpx.GPX) -> str:
    """
    Дистанция в строковом представлении
    """
    return str(round((gpx.tracks[0].segments[0].length_2d() / 1000), 2)) + " км"

async def async_block(med_coord: dict, coord: list, gpx: gpxpy.gpx.GPX):
    """
    Асинхронный блок, задачи которые выполняются параллельно с запросом к API
    """
    task_api_response = asyncio.create_task(get_weather(med_coord))
    task_med_min_max_points = asyncio.create_task(get_med_min_max_point(coord))
    task_dist = asyncio.create_task(get_dist(gpx))
    await task_med_min_max_points
    task_zoom = asyncio.create_task(find_zoom(task_med_min_max_points.result()))
    await task_api_response
    await task_zoom
    await task_dist
    return task_api_response.result(), \
        task_med_min_max_points.result(), \
        task_zoom.result(), \
        task_dist.result()


if __name__ == '__main__':
    start1 = time.time()
    with open("test.gpx", "rb") as f:
        gpx_file_builder(f)
    end1 = time.time()
    print(f"Результат новой функции {round(end1 - start1, 2)} сек.")
    start2 = time.time()
    with open("test.gpx", "rb") as f:
        OldGPXFile(f)
    end2 = time.time()
    print(f"Результат старой функции {round(end2 - start2, 2)} сек.")
