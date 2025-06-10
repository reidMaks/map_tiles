# projection.py

from shapely.geometry import shape
from pyproj import Transformer
import map_generator.config as config

# Ініціалізація трансформера WGS84 -> UTM
transformer = Transformer.from_crs(config.WGS84_EPSG, config.UTM_EPSG, always_xy=True)

def project_geometry(geom):
    if geom.geom_type == 'Polygon':
        return shape({
            'type': 'Polygon',
            'coordinates': [list(map(lambda coord: transformer.transform(*coord), geom.exterior.coords))]
        })
    elif geom.geom_type == 'MultiPolygon':
        return shape({
            'type': 'MultiPolygon',
            'coordinates': [
                [list(map(lambda coord: transformer.transform(*coord), poly.exterior.coords))]
                for poly in geom.geoms
            ]
        })
    else:
        raise ValueError(f"Unsupported geometry type: {geom.geom_type}")

