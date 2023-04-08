from SUPJournal.tools.gpx_new import gpx_parser, gpx_file_builder
from gpxpy.gpx import GPX
import unittest

class GPXTest(unittest.TestCase):
    def test_001_gpx_parser(self):
        with open("test.gpx", "rb") as f:
            gpx = gpx_parser(f)
        self.assertEqual(type(gpx), GPX, "Тип возвращаемого значения")
        self.assertEqual(gpx.tracks[0].segments[0].points[0].latitude, 56.38219, "Проверка значений")

