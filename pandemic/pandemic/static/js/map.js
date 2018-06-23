"use strict";

function buildCityData(data) {
    var city_data = {};

    for (var i = 0; i < data.length; i++) {
        var city = data[i];
        city_data[city.name] = {};
        city_data[city.name]['latitude'] = city.latitude;
        city_data[city.name]['longitude'] = city.longitude;
        city_data[city.name]['color'] = city.color;
        city_data[city.name]['connections'] = city.connections;
    }
    
    return city_data;
}

function placeCities(map, city_data) {
    for (var city in city_data) {
        var name = city;
        var latitude = city_data[city].latitude;
        var longitude = city_data[city].longitude;
        var color = city_data[city].color;
        var geojsonMarkerOptions = {
            radius: 8,
            fillColor: color,
            color: "#000",
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8
        };
        var geojsonFeature = {
            "type": "Feature",
            "properties": {
                "name": name,
            },
            "geometry": {
                "type": "Point",
                "coordinates": [latitude, longitude],
            },
        }
        var geojsonObject = L.geoJSON(geojsonFeature, {
            pointToLayer: function(feature, latlng) {
                return L.circleMarker(latlng, geojsonMarkerOptions);
            }
        }).addTo(map);
        geojsonObject.bindPopup("<b>" + name + "</b>");
    }
}

function specialCase(city1, city2) {
    var cityPair = [city1, city2].toString();
    var cityPairReverse = [city2, city1].toString();
    var isSpecial = false;
    var prohibited_cases = [
        ["Los Angeles", "Sydney"],
        ["San Francisco", "Manila"],
        ["San Francisco", "Tokyo"],
    ]

    for (var i = 0; i < prohibited_cases.length; i++) {
        var ar = prohibited_cases[i].toString();
        if (ar == cityPair || ar == cityPairReverse) {
            isSpecial = true;
        }
    }

    return isSpecial;
}

function lineEquation(point1, point2) {
    var offset = 180 + point1[0];
    var offset_lat = 180 + offset;
    var m = (Math.max(point1[1], point2[1]) - Math.min(point1[1], point2[1])) / (Math.max(offset_lat, point2[0]) - Math.min(offset_lat, point2[0]));
    var b = point2[1] - m * point2[0];
    return [m, b];
}

function findSpecialLong(lineEquation) {
    return lineEquation[0] * 180 + lineEquation[1];
}

function cacheCheck(cache, item1, item2) {
    var isNotThere = true;
    var pair1 = [item1, item2].toString();
    var pair2 = [item2, item1].toString();

    for (var i = 0; i < cache.length; i++) {
        var ar = cache[i].toString();
        if (pair1 == ar || pair2 == ar) {
            isNotThere = false;
        }    
    }

    return isNotThere;
}

function connectCities(map, city_data) {
    var cache = []
    var specialCache = []
    for (var city in city_data) {
        for (var i = 0; i < city_data[city].connections.length; i++) {
            var latlngs = [];
            var connected_city = city_data[city].connections[i];
            var city_lat = city_data[connected_city].latitude;
            var city_lang = city_data[connected_city].longitude;
            var lat = city_data[city].latitude;
            var lng = city_data[city].longitude;
            
            latlngs.push([city_lat, city_lang]);
            latlngs.push([lat, lng]);
            if (!specialCase(city, connected_city)) {
                if (cacheCheck(cache, latlngs[0], latlngs[1])) {
                    cache.push(latlngs);
                    var line_feature = {
                        "type": "LineString",
                        "coordinates": latlngs,
                    }
                    var line_style = {
                        "color": "#98FB98",
                        "weight": 2,
                        "opacity": 0.85,
                    }
                    L.geoJSON(line_feature, {style: line_style}).addTo(map);
                }
            } else {
                if (cacheCheck(specialCache, city, connected_city)) {
                    specialCache.push([city, connected_city]);
                    var lineEq = lineEquation(latlngs[0], latlngs[1]);
                    var long = findSpecialLong(lineEq);
                    var point1_node;
                    var point2_node;
                    
                    if (latlngs[0][0] > latlngs[1][0]) {
                        point1_node = [180, long];
                        point2_node = [-180, long];
                    } else {
                        point1_node = [-180, long];
                        point2_node = [180, long];
                    }

                    var line_features = [{
                        "type": "LineString",
                        "coordinates": [latlngs[0], point1_node],
                    }, {
                        "type": "LineString",
                        "coordinates": [latlngs[1], point2_node],
                    }]
                    L.geoJSON(line_features, {style: line_style}).addTo(map);
                }
            }
        }    
    }
}

function storeData(data) {
    for (var i = 0; i < data.length; i++) {
        var city = data[i];
        var id = String(city.id);
        city_object_data[id] = city;
    }
}

function getCities(map) {
    $.get({url: CITY_BASE_URL, async: false}).done(function(data){
        var city_data = buildCityData(data);
        storeData(data);
        connectCities(map, city_data);
        placeCities(map, city_data);
    });
}

function wrapCoordinate(type, value) {
    if (type === "Latitude") {
        if (value > 90.0) {
            return -value + 90.0;
        } else if (value < -90.0) {
            return -value - 90.0;
        } else {
            return value;
        }
    } else {
        if (value > 180.0) {
            return -value + 180.0;
        } else if (value < -180.0) {
            return -value - 180.0;
        } else {
            return value;
        }
    }
}