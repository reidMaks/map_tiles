import json
import os
import sys
from tempfile import NamedTemporaryFile
from shapely.geometry import shape

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import map_generator.config as config
from map_generator.regions import load_regions
from map_generator.cities import load_cities, add_cities_to_dxf


class DummyMSP:
    def __init__(self):
        self.circles = []
        self.texts = []

    def add_circle(self, center, radius):
        self.circles.append((center, radius))

    def add_text(self, text, dxfattribs):
        self.texts.append((text, dxfattribs))


def test_load_regions_and_projection():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"TYPE_1": "Oblast'", "NAME_1": "Test"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
                },
            }
        ],
    }
    with NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(geojson, tmp)
        tmp_path = tmp.name

    regions = load_regions(tmp_path)
    os.unlink(tmp_path)
    assert "Test" in regions
    poly = regions["Test"]
    assert poly.bounds[0] != 0  # projected


def test_load_cities_and_add():
    data = {"City": [0.0, 0.0]}
    with NamedTemporaryFile("w", delete=False, suffix=".json") as tmp:
        json.dump(data, tmp)
        tmp_path = tmp.name
    old_path = config.CITIES_FILE
    config.CITIES_FILE = tmp_path
    cities = load_cities()
    config.CITIES_FILE = old_path
    os.unlink(tmp_path)

    msp = DummyMSP()
    add_cities_to_dxf(msp, cities, 1.0, 0, 0)

    assert msp.circles and msp.texts
    assert msp.texts[0][0] == "City"
