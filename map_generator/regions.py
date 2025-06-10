# regions.py

import json
from shapely.geometry import shape
import map_generator.config as config
from map_generator.projection import project_geometry

def load_regions(source_file):
    """Завантаження та проєкція регіонів з GeoJSON."""
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    VALID_TYPES = ["Oblast'", "AutonomousRepublic"]
    features = [
        x for x in data['features']
        if x['properties'].get('TYPE_1') in VALID_TYPES
        and x['properties'].get('NAME_1') not in config.EXCLUDE_REGIONS
    ]

    regions = {}
    for feature in features:
        name = feature['properties']['NAME_1'].replace(" ", "_")
        geom = shape(feature['geometry'])
        projected_geom = project_geometry(geom)
        regions[name] = projected_geom

    return regions
