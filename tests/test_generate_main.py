import os
import sys
from types import SimpleNamespace
from shapely.geometry import Polygon
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from map_generator import generate

class DummyMSP:
    def add_circle(self, *a, **kw):
        pass
    def add_lwpolyline(self, *a, **kw):
        pass
    def add_text(self, *a, **kw):
        pass

class DummyDoc:
    def __init__(self):
        self.units = None
    def modelspace(self):
        return DummyMSP()
    def saveas(self, path):
        DummyMain.calls.append(("saveas", path))

class DummyEzdxf:
    units = SimpleNamespace(MM="MM")
    def new(self):
        return DummyDoc()

def fake_load_regions(path):
    DummyMain.calls.append(("load_regions", path))
    return {"A": Polygon([(0,0),(1,0),(1,1),(0,1)])}

def fake_load_cities():
    DummyMain.calls.append(("load_cities",))
    return {"City": [0,0]}

def fake_generate_contours(*a, **kw):
    DummyMain.calls.append(("generate_contours",))

def fake_generate_pins_and_holes(*a, **kw):
    DummyMain.calls.append(("generate_pins_and_holes",))

def fake_add_cities_to_dxf(*a, **kw):
    DummyMain.calls.append(("add_cities_to_dxf",))

class DummyMain:
    calls = []

def test_main(monkeypatch, tmp_path):
    DummyMain.calls.clear()
    monkeypatch.setattr(sys, "argv", ["generate.py", str(tmp_path / "src.json")])
    monkeypatch.setattr(generate, "load_regions", fake_load_regions)
    monkeypatch.setattr(generate, "load_cities", fake_load_cities)
    monkeypatch.setattr(generate, "generate_contours", fake_generate_contours)
    monkeypatch.setattr(generate, "generate_pins_and_holes", fake_generate_pins_and_holes)
    monkeypatch.setattr(generate, "add_cities_to_dxf", fake_add_cities_to_dxf)
    monkeypatch.setattr(generate, "ezdxf", DummyEzdxf())
    monkeypatch.setattr(os, "makedirs", lambda *a, **kw: DummyMain.calls.append(("makedirs", a[0])))
    generate.main()
    assert ("saveas", f"tmp/ukraine_full.dxf") in DummyMain.calls


def test_main_invalid_usage(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["generate.py"])
    with pytest.raises(SystemExit):
        generate.main()
