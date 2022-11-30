import gpxpy
import datetime
import requests
import json
import folium


class GpxFile:
    def __init__(self, file: str):
        self.__gpx = self.gpx_parser(file)
        self.coord = self.get_coord()
        self.time = self.get_time()
        self.weather = self.get_weather()
        self.med_point = self.get_med_point()
        self.map = self.create_map()

    @staticmethod
    def gpx_parser(file):
        with open(file, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        return gpx

    def get_coord(self):
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
        info = datetime.datetime.strptime(str(self.__gpx.tracks[0].segments[0].points[med].time)[:-6],
                                          "%Y-%m-%d %H:%M:%S")
        coord = (round(self.__gpx.tracks[0].segments[0].points[med].latitude, 4),
                 round(self.__gpx.tracks[0].segments[0].points[med].longitude, 4))
        date = info.date()
        return {"index": info.hour, "coord": coord, "date": str(date)}

    def get_weather(self):
        data = self.__get_mid_time()
        req = requests.get(f"https://archive-api.open-meteo.com/v1/"
                           f"era5?latitude={data['coord'][0]}&longitude={data['coord'][1]}&"
                           f"start_date={data['date']}&end_date={data['date']}&hourly=temperature_2m")
        req = json.loads(req.text)
        return f"{req['hourly']['temperature_2m'][data['index']]} °C"

    def get_med_point(self):
        lat = [item[0] for item in self.coord]
        lon = [item[1] for item in self.coord]
        lat = {"min": min(lat), "max": max(lat)}
        print(lat)
        lon = {"min": min(lon), "max": max(lon)}
        lat = round((lat["min"] + lat["max"]) / 2, 6)
        lon = round((lon["min"] + lon["max"]) / 2, 6)
        return [lat, lon]

    def create_map(self):
        my_map = folium.Map(location=self.med_point, zoom_start=14)
        folium.vector_layers.PolyLine(self.coord).add_to(my_map)
        return my_map

    def save_map(self, file_name):
        self.map.save(file_name)


if __name__ == "__main__":
    test = GpxFile("test.gpx")
    print(test.time)
    print(test.weather)
    print(test.coord)
    print(test.get_med_point())
    test.save_map("map.html")
