#!/bin/bash

# Зчитуємо значення з .env
source .env

echo "▶ Рівень спрощення (Planar Quantile): $SIMPLIFY_PLANAR_QUANTILE"

# Формуємо ім'я файлу для спрощеного GeoJSON
SIMPLIFIED_FILE="source_data/simplified_gadm41_UKR_1_P-${SIMPLIFY_PLANAR_QUANTILE}.json"

# Запуск контейнера для конвертації
docker run --rm -v $(pwd):/data topojson-tool bash -c "
    cd /data && \
    geo2topo -q 1e5 oblasts=source_data/gadm41_UKR_1.json > ukraine.topojson && \
    toposimplify -P $SIMPLIFY_PLANAR_QUANTILE -f < ukraine.topojson > ukraine_simplified.topojson && \
    node smooth_topojson.js && \
    topo2geo oblasts=$SIMPLIFIED_FILE < ukraine_smoothed.topojson
"

echo "✅ Спрощений GeoJSON збережено: $SIMPLIFIED_FILE"

# Запуск Python-скрипта для генерації DXF
echo "🚀 Генерація DXF..."
python3 -m map_generator.generate "$SIMPLIFIED_FILE"
