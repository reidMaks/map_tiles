# config.py

# Геометричні налаштування
PIN_DIAMETER_MM = 5.0
PIN_SPACING_MM = 40.0
PIN_MARGIN_MM = 3.0
TOLERANCE_MM = 0.3
TARGET_SIZE_MM = 250
OFFSET_MM = 0.1

# Виключення регіонів
EXCLUDE_REGIONS = ['Kyiv', "Sevastopol'"]

# Проєкції
WGS84_EPSG = "EPSG:4326"
UTM_EPSG = "EPSG:32636"

# Каталоги
OUTPUT_DIR = "tmp"
CITIES_FILE = "source_data/cities.json"
