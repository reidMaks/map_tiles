const fs = require('fs');
const topojson = require('topojson-client');

// === Chaikin's Algorithm ===
function chaikinSmooth(coords, iterations = 1) {
    for (let iter = 0; iter < iterations; iter++) {
        let newCoords = [];
        for (let i = 0; i < coords.length - 1; i++) {
            let p0 = coords[i];
            let p1 = coords[i + 1];

            let Q = [
                0.75 * p0[0] + 0.25 * p1[0],
                0.75 * p0[1] + 0.25 * p1[1]
            ];
            let R = [
                0.25 * p0[0] + 0.75 * p1[0],
                0.25 * p0[1] + 0.75 * p1[1]
            ];
            newCoords.push(Q, R);
        }
        newCoords.push(coords[coords.length - 1]);
        coords = newCoords;
    }
    return coords;
}

// === Основний процес ===
const inputFile = 'ukraine_simplified.topojson';
const outputFile = 'ukraine_smoothed.topojson';

// 1. Завантаження TopoJSON
let topoData = JSON.parse(fs.readFileSync(inputFile));

// 2. Декодування арок
let transform = topoData.transform;
let scale = transform.scale;
let translate = transform.translate;

function decodeArc(arc) {
    let points = [];
    let x = 0, y = 0;
    arc.forEach(d => {
        x += d[0];
        y += d[1];
        points.push([x * scale[0] + translate[0], y * scale[1] + translate[1]]);
    });
    return points;
}

// 3. Згладжування арок
let newArcs = topoData.arcs.map(arc => {
    let decoded = decodeArc(arc);
    let smoothed = chaikinSmooth(decoded, 1);  // 1 ітерація для легкого згладжування

    // Перекодування назад у delta
    let prev = [0, 0];
    let deltaArc = smoothed.map((p, idx) => {
        let absX = (p[0] - translate[0]) / scale[0];
        let absY = (p[1] - translate[1]) / scale[1];
        if (idx === 0) {
            prev = [absX, absY];
            return [absX, absY];
        } else {
            let dx = absX - prev[0];
            let dy = absY - prev[1];
            prev = [absX, absY];
            return [dx, dy];
        }
    });

    // Перша точка має бути дельтою
    deltaArc[0] = [deltaArc[0][0], deltaArc[0][1]];
    return deltaArc;
});

// 4. Заміна арок у TopoJSON
topoData.arcs = newArcs;

// 5. Збереження
fs.writeFileSync(outputFile, JSON.stringify(topoData));
console.log(`✅ Згладжений TopoJSON збережено до ${outputFile}`);
