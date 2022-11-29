import gpxpy
import datetime
import requests
import json


class GpxFile:
    def __init__(self, file: str):
        self.__gpx = self.gpx_parser(file)
        self.coord = self.get_coord(self.__gpx)
        self.time = self.get_time(self.__gpx)
        self.weather = self.get_weather(self.__gpx)

    @staticmethod
    def gpx_parser(file):
        with open(file, "r") as gpx_file:
            gpx = gpxpy.parse(gpx_file)
        return gpx

    @staticmethod
    def get_coord(gpx):
        gpx_data = []
        for tracks in gpx.tracks:
            for segments in tracks.segments:
                for point in segments.points:
                    gpx_data.append((point.latitude, point.longitude))
        return gpx_data

    @staticmethod
    def get_time(gpx):
        start = datetime.datetime.strptime(str(gpx.tracks[0].segments[0].points[0].time)[:-6], "%Y-%m-%d %H:%M:%S")
        end = datetime.datetime.strptime(str(gpx.tracks[-1].segments[-1].points[-1].time)[:-6], "%Y-%m-%d %H:%M:%S")
        return end - start

    @staticmethod
    def __get_mid_time(gpx):
        med = int(len(gpx.tracks[0].segments[0].points) / 2)
        info = datetime.datetime.strptime(str(gpx.tracks[0].segments[0].points[med].time)[:-6], "%Y-%m-%d %H:%M:%S")
        coord = (round(gpx.tracks[0].segments[0].points[med].latitude, 4),
                 round(gpx.tracks[0].segments[0].points[med].longitude, 4))
        date = info.date()
        return {"index": info.hour, "coord": coord, "date": str(date)}

    def get_weather(self, gpx):
        data = self.__get_mid_time(gpx)
        req = requests.get(f"https://archive-api.open-meteo.com/v1/"
                           f"era5?latitude={data['coord'][0]}&longitude={data['coord'][1]}&"
                           f"start_date={data['date']}&end_date={data['date']}&hourly=temperature_2m")
        req = json.loads(req.text)
        return f"{req['hourly']['temperature_2m'][data['index']]} °C"


if __name__ == "__main__":
    test = GpxFile("test.gpx")
    print(test.time)
    print(test.weather)
    print(test.coord)
