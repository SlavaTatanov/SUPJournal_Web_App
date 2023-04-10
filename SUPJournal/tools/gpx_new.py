import locale
import asyncio
import gpxpy
from folium import Map
from typing import BinaryIO
import httpx


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
    weather = asyncio.run(async_block(med_coord))
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

async def async_block(med_coord: dict):
    """
    Асинхронный блок, задачи которые выполняются параллельно с запросом к API
    """
    api_response = asyncio.create_task(get_weather(med_coord))
    await api_response
    return api_response.result()


if __name__ == '__main__':
    with open("test.gpx", "rb") as f:
        gpx_file_builder(f)