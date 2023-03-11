import gpxpy
import datetime
import requests
import json
import folium
from geopy.distance import geodesic as gd


class GpxFile:
    def __init__(self, file):
        self.__gpx = self.gpx_parser(file)
        self.coord = self.get_coord()
        self.time_points = self.get_time_points()
        self.time = self.time_points[-1] - self.time_points[0]
        self.weather_info = self.get_weather_info()
        self.weather = self.get_weather()
        self.med_min_max_point = self.get_med_min_max_point()
        self.zoom = self.find_zoom()
        self.map = self.create_map()
        self.dist = str(round((self.__gpx.tracks[0].segments[0].length_2d() / 1000), 2)) + " км"

    @staticmethod
    def gpx_parser(file):
        """
        Базовый метод, выполняет парсинг гпх файла
        """
        gpx = gpxpy.parse(file)
        return gpx

    def get_coord(self):
        """
        Составляет список координат
        """
        gpx_data = []
        for tracks in self.__gpx.tracks:
            for segments in tracks.segments:
                for point in segments.points:
                    gpx_data.append((point.latitude, point.longitude))
        return gpx_data

    def get_time(self):
        start = datetime.datetime.strptime(str(self.__gpx.tracks[0].segments[0].points[0].time)[:-6],
                                           "%Y-%m-%d %H:%M:%S")
        end = datetime.datetime.strptime(str(self.__gpx.tracks[-1].segments[-1].points[-1].time)[:-6],
                                         "%Y-%m-%d %H:%M:%S")
        return end - start

    def __get_mid_time(self):
        med = int(len(self.__gpx.tracks[0].segments[0].points) / 2)
        info = self.time_points[med]
        coord = (round(self.coord[med][0], 4),
                 round(self.coord[med][1], 4))
        date = info.date()
        return {"index": info.hour, "coord": coord, "date": str(date)}

    def get_weather(self):
        weather_info = {}
        for inf in self.weather_info:
            date  = self.time_points[inf["ind"]].date()
            req = requests.get(f"https://archive-api.open-meteo.com/v1/"
                               f"era5?latitude={inf['coord'][0]}&longitude={inf['coord'][1]}&"
                               f"start_date={date}&end_date={date}&hourly=temperature_2m")
            req = json.loads(req.text)
            weather_info[self.time_points[inf["ind"]].time()] = req['hourly']['temperature_2m'][inf["hour"]]
        return weather_info

    def get_med_min_max_point(self):
        lat = [item[0] for item in self.coord]
        lon = [item[1] for item in self.coord]
        lat = {"min": min(lat), "max": max(lat)}
        lon = {"min": min(lon), "max": max(lon)}
        min_point = (lat["min"], lon["min"])
        max_point = (lat["max"], lon["max"])
        lat = round((lat["min"] + lat["max"]) / 2, 6)
        lon = round((lon["min"] + lon["max"]) / 2, 6)
        med_point = [lat, lon]
        return {"med_point": med_point, "min_point": min_point, "max_point": max_point}

    def find_zoom(self):
        dist = gd(self.med_min_max_point["min_point"], self.med_min_max_point["max_point"]).km
        if dist <= 2:
            return 16
        if dist <= 4:
            return 15
        if dist <= 8:
            return 14
        if dist <= 15:
            return 13
        if dist <= 30:
            return 12
        else:
            return 11

    def create_map(self):
        my_map = folium.Map(location=self.med_min_max_point["med_point"], zoom_start=self.zoom)
        folium.vector_layers.PolyLine(self.coord).add_to(my_map)
        for pt, tm in zip(self.weather_info, self.weather.values()):
            inf = f"Время - {pt['hour']}:00 ::: Температура {tm} °C"
            folium.vector_layers.Marker(pt["coord"], tooltip=inf).add_to(my_map)
        return my_map

    def save_map(self):
        return self.map.save()

    def get_time_points(self):
        time_points = []
        for tracks in self.__gpx.tracks:
            for segments in tracks.segments:
                for point in segments.points:
                    time_points.append(point.time.astimezone())
        return time_points

    def get_weather_info(self):
        """
        Метод рассчитывающий количество часов в тренировке,
        для получения данных о погоде в каждый отдельный час
        """
        index = [0]
        hours_coord = []
        for ind in range(1, len(self.time_points)):
            if self.time_points[ind].hour != self.time_points[ind-1].hour:
                index.append(ind)
        for ind in index:
            hours_coord.append(self.coord[ind])
        hours = list({hour.hour for hour in self.time_points})
        info = []
        for hr, cor, ind in zip(hours, hours_coord, index):
            info.append({"hour": hr, "coord": cor, "ind": ind})
        return info

    def get_root_map(self):
        return self.map.get_root().render()


if __name__ == "__main__":
    test = GpxFile("test.gpx")
    print(test.weather_info)
    test.save_map("map.html")
