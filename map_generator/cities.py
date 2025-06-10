# cities.py

import json
from pyproj import Transformer
import map_generator.config as config

def load_cities():
    """Завантаження обласних центрів з файлу."""
    with open(config.CITIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def add_cities_to_dxf(msp, cities, scale_factor, min_x, min_y):
    """Додавання міст у DXF."""
    transformer = Transformer.from_crs(config.WGS84_EPSG, config.UTM_EPSG, always_xy=True)

    for city, coords in cities.items():
        lon, lat = coords
        x_proj, y_proj = transformer.transform(lon, lat)

        x_mm = (x_proj - min_x) * scale_factor
        y_mm = (y_proj - min_y) * scale_factor

        msp.add_circle((x_mm, y_mm), 2)  # Позначаємо місто кружечком 2 мм
        msp.add_text(city, dxfattribs={'height': 3, 'insert': (x_mm + 2, y_mm + 2)})


    print(f"✅ Додано {len(cities)} міст на карту")
