import gpxpy
import datetime
import requests
import json
import folium
import locale
from geopy.distance import geodesic as gd
from bokeh.plotting import figure
from bokeh.models import HoverTool, CustomJS
from bokeh.resources import CDN
from bokeh.embed import components
from bokeh.events import MouseMove
from statistics import mean
from pympler import asizeof

locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')

class GpxFile:
    """
    Связующее GPX парсера и Folium для отрисовки карты,
    хранит в себе параметры тренировки и саму карту, созданную Folium
    """

    SPEED_KM_PER_HOUR = 3.6
    SPEED_KNOT_PER_HOUR = 1.94

    def __init__(self, file):
        self.__gpx = self.gpx_parser(file)
        self._coord_and_speed = self.get_coord()
        self.time_points = self.get_time_points()
        self.training_date = self.time_points[0]
        self.time = self.time_points[-1] - self.time_points[0]
        self.weather_info = self.get_weather_info()
        self.weather = self.get_weather()
        self.med_min_max_point = self.get_med_min_max_point()
        self.zoom = self.find_zoom()
        self.map = self.create_map()
        self.dist = str(round((self.__gpx.tracks[0].segments[0].length_2d() / 1000), 2)) + " км"
        self.format_date = self.training_date.date().strftime('%d %B %Y')
        avg_speed = mean([spd["speed"] for spd in self._coord_and_speed if spd["speed"] is not None])
        self.avg_speed = round(avg_speed * self.SPEED_KM_PER_HOUR, 2)
        self.avg_speed_knot = round(avg_speed * self.SPEED_KNOT_PER_HOUR, 2)
        self.speed_plot = self.create_speed_plot(self.SPEED_KNOT_PER_HOUR)

        # Чистим память от ненужных после вычислений объектов
        del self.__gpx
        del self._coord_and_speed
        del self.time_points

        # Смотрим сколько объект занимает в памяти, для тестов
        # На проде можно закомментировать
        # print(f"Размер объекта {self.get_size(self)}")
        # print("-"*30)
        # for key, value in self.__dict__.items():
        #     print(f"{key} -> {self.get_size(value)}")
        # print("-" * 30)

    @staticmethod
    def get_size(obj):
        """
        Служебный метод определения размера разных объектов
        """
        obj = asizeof.asizeof(obj)
        obj = round(obj/(1024 * 1024), 2)
        return f"{obj} Мб"


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
        last_point = None
        last_time = None
        delta_time_points = None
        current_time = None
        for tracks in self.__gpx.tracks:
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
                                     "time": current_time})
                    last_point = gpxpy.gpx.GPXTrackPoint(point.latitude, point.longitude, time=point.time)
                    delta_time_points = point.time - last_time
                    last_time = point.time
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
        coord = (round(self._coord_and_speed[0][med][0], 4),
                 round(self._coord_and_speed[0][med][1], 4))
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
        lat = [item["coord"][0] for item in self._coord_and_speed]
        lon = [item["coord"][1] for item in self._coord_and_speed]
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

    def create_map(self):
        my_map = folium.Map(location=self.med_min_max_point["med_point"], zoom_start=self.zoom)
        my_map._id = "TrainingMap"
        only_coord = [point["coord"] for point in self._coord_and_speed]
        folium.vector_layers.PolyLine(only_coord).add_to(my_map)
        for pt, tm in zip(self.weather_info, self.weather.values()):
            inf = f"Время - {pt['hour']}:00 ::: Температура {tm} °C"
            folium.vector_layers.Marker(pt["coord"], tooltip=inf).add_to(my_map)
        return my_map

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
            hours_coord.append(self._coord_and_speed[ind]["coord"])
        hours = list({hour.hour for hour in self.time_points})
        info = []
        for hr, cor, ind in zip(hours, hours_coord, index):
            info.append({"hour": hr, "coord": cor, "ind": ind})
        return info

    def get_root_map(self):
        """
        Создает карту которую можно передать в HTML шаблон через Jinja
        """
        return self.map.get_root().render()

    def create_speed_plot(self, factor: float):
        """
        Создает график, на вход принимает еденицы измерения и конвертирует значения скоростей
        """
        speeds = [spd["speed"] * factor for spd in self._coord_and_speed if spd["speed"] is not None]
        units = None
        match factor:
            case self.SPEED_KNOT_PER_HOUR:
                units = "узлов/ч"
            case self.SPEED_KM_PER_HOUR:
                units = "км/ч"
        plot = figure(title="Скорость", y_axis_label=units, x_axis_type="datetime", width=380, height=350)
        if len(speeds) > 100:
            smooth_line = self.smooth_plot_line(speeds, len(speeds) // 100)
        else:
            smooth_line = self.smooth_plot_line(speeds, 1)

        custom_js = CustomJS(args=dict(xr=plot.x_range,
                                       data=smooth_line,
                                       times=[it["time"] for it in smooth_line]),
                             code="""
          var ind = cb_data['index'].line_indices
          console.log(ind)
          console.log(data.length)
          if (ind.length == 1) {
            var coord = data[ind]["coord"]
          } else {
            var coord = null
          }
          showUserPoint(coord)
        """)
        hover = HoverTool(tooltips=[("Скорость", "@y{0.00}" + units)], mode='vline', callback=custom_js)
        plot.add_tools(hover)
        plot.line(
            [it["time"] for it in smooth_line],
            [it["speed"] for it in smooth_line],
            line_width=3,
            line_alpha=0.8
        )
        script, div = components(plot)
        return {"script": script, "div": div, "css": CDN.render_css(), "res": CDN.render()}


    def smooth_plot_line(self, line_points: list, smooth_val: int) -> list:
        """
        Расчет скользящего среднего, сглаживает значения точек на графике
        """
        counter = 1
        index_point = 0
        res_points_list = []
        avg_stack = []
        for it in line_points:
            if counter >= smooth_val:
                res_points_list.append({
                    "speed": mean(avg_stack),
                    "time": self._coord_and_speed[index_point]["time"],
                    "coord": self._coord_and_speed[index_point]["coord"]
                })
                counter = 0
                avg_stack = [it]
            else:
                avg_stack.append(it)
                counter += 1
            index_point += 1
        return res_points_list
