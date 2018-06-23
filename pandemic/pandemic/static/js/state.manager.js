/**
 * URL Routing getters
 */
function getBaseUrl() {
    return SESSION_HASH;
}

function getSessionBaseUrl() {
    return SESSION_BASE_URL + getBaseUrl() + '/';
}

function getUsersQuery() {
    return SESSION_USERS_BASE_URL;
}

function getOwnerBaseUrl() {
    return SESSION_OWNER_BASE_URL;
}

function getPlayerStateBaseUrl() {
    return PLAYER_STATE_BASE_URL;
}

function getCityStateBaseUrl() {
    return CITY_STATE_BASE_URL;
}

function getCardStateBaseUrl() {
    return CARD_STATE_BASE_URL;
}

function getCureStateBaseUrl() {
    return CURE_STATE_BASE_URL;
}

function getDiseaseStateBaseUrl() {
    return DISEASE_STATE_BASE_URL;
}

function getPawnBaseUrl() {
    return PAWN_BASE_URL;
}

function getSessionStateBaseUrl() {
    return SESSION_STATE_BASE_URL;
}

function getCardBaseUrl() {
    return CARD_BASE_URL;
}


// --- URL END

function updateUsersList(data) {
    var current_users = $(".lobby-username");
    var user_list = $(".col-sm-8")
    for (var i = 0; i < data.length; i++) {
        var username = data[i].username;
        var image_url = data[i].img_url;
        var isThere = false;
        for (var j = 0; j < current_users.length; j++) {
            var user = current_users[j];
            if (user.textContent === username) {
                isThere = true;
            }
        }
        if (!isThere) {
            var element_line = "<div class='card lobby-card d-inline-block'>";
            element_line += "<img class='card-img-top user-img' src='" + image_url + "' alt='User profile image'>";
            element_line += "<div class='card-body' style='height: 50%;'><h5 class='lobby-username'>" + username + "</h5><a class='btn btn-primary' href='/user/" + username + "/'>View Profile</a></div></div>";
            if ($("#start-game").length === 0) {
                user_list.append(element_line);
            } else {
                $(element_line).insertBefore("#start-game");
            }
        }
    }
}

function getUsers() {
    $.get({
        url: getUsersQuery()
    }).done(function (data) {
        updateUsersList(data);
    });
}

function getSessionState(async) {
    $.get({
        url: getSessionStateBaseUrl(),
        async: async
    }).done(function (data) {
        if (session_state == null) {
            session_state = data[0];
            if (String(session_state.current_player) === USER_ID) {
                populateOptions();
            }
            updateStats();
        } else {
            var observed_state = session_state;
            var fetch_time = moment(data.last_changed);
            var observed_state_time = moment(observed_state.last_changed);
            if (fetch_time.isAfter(observed_state_time)) {
                var past_cur_player = session_state.current_player;
                session_state = data[0];
                if (past_cur_player !== session_state.current_player && session_state.current_player === Number(USER_ID)) {
                    populateOptions();
                } else if (past_cur_player === Number(USER_ID) && session_state.current_player !== Number(USER_ID)) {
                    $("#commands").hide();
                    console.log("hide");
                    $("#cards").css({"visibility": "hidden"});
                }
                updateStats();
            }
        }
    });
}

function getDiseaseState(async) {
    $.get({
        url: getDiseaseStateBaseUrl(),
        async: async
    }).done(function (data) {
        for (var i = 0; i < data.length; i++) {
            var disease_state = data[i];
            var id = String(disease_state.id);
            if (disease_states.hasOwnProperty(id)) {
                var observed_state = disease_states[id];
                var fetch_time = moment(disease_state.last_changed)
                var observed_state_time = moment(observed_state.last_changed)
                if (fetch_time.isAfter(observed_state_time)) {
                    disease_states[id] = disease_state;
                }
            } else {
                disease_states[id] = disease_state;
            }
        }
    });
}

function displayOwnCards() {
    var ids = [];
    for (var id in card_states) {
        var card_state = card_states[id];
        var card = cards[String(card_state.card)];
        ids.push(String(card_state.id));
        if ($(".allCards-" + USERNAME + "-" + String(card_state.id)).length === 0) {
            if (card.card_type === "City") {
                var title = city_object_data[String(card.city)].name;
                var bg_color;
                var text_color = '';
                if (card.color === "Black") {
                    bg_color = "bg-dark";
                    text_color = " text-white";
                } else if (card.color === "Red") {
                    bg_color = "bg-danger";
                } else if (card.color === "Yellow") {
                    bg_color = "bg-warning";
                } else {
                    bg_color = "bg-primary";
                }
                $("#allCards-" + USERNAME).append("<div class='card allCards-" + USERNAME + "-" + String(card_state.id) + " " + bg_color + text_color +  "' style='width: 18rem;'>" +
                    "<div class='card-body'><h5>" + title + "</h5><p>Move to " + title + " or discard if in " + title + " to move anywhere.</p></div></div>");
            } else {
                var title = card.description.split(":")[0];
                var description = card.description.split(":")[1];
                $("#allCards-" + USERNAME).append("<div class='card allCards-" + USERNAME + "-" + String(card_state.id) + "' style='width: 18rem;'>" +
                    "<div class='card-body'><h5>" + title + "</h5><p>" + description + "</p></div></div>");
            }
        }
    }
    var displayed_cards = $("#allCards-" + USERNAME + " div.card");
    for (var i = 0; i < displayed_cards.length; i++) {
        var element = displayed_cards[i];
        var id = element.classList[1].split("-")[2];
        if (ids.indexOf(id) === -1) {
            $("." + element.classList[1]).remove();
        }
    }
}

function getCardState(async) {
    $.get({
        url: getCardStateBaseUrl() + "?player=" + USERNAME,
        async: async
    }).done(function (data) {
        var ids = [];
        for (var i = 0; i < data.length; i++) {
            var card_state = data[i];
            var id = String(card_state.id);
            ids.push(id);
            if (card_states.hasOwnProperty(id)) {
                var observed_state = card_states[id];
                var fetch_time = moment(card_state.last_changed);
                var observed_state_time = moment(observed_state.last_changed);
                if (fetch_time.isAfter(observed_state_time)) {
                    card_states[id] = card_state;
                }
            } else {
                card_states[id] = card_state;
            }
        }
        for (var id in card_states) {
            if (ids.indexOf(id) === -1) {
                delete card_states[id];
            }
        }
        displayOwnCards();
    });
}

function getCureState(async) {
    $.get({
        url: getCureStateBaseUrl(),
        async: async
    }).done(function (data) {
        for (var i = 0; i < data.length; i++) {
            var cure_state = data[i];
            var id = String(cure_state.id);
            if (cure_states.hasOwnProperty(id)) {
                var observed_state = cure_states[id];
                var fetch_time = moment(cure_state.last_changed);
                var observed_state_time = moment(observed_state.last_changed);
                if (fetch_time.isAfter(observed_state_time)) {
                    cure_states[id] = cure_state;
                }
            } else {
                cure_states[id] = cure_state;
            }
        }
    });
}

function scheduleUsersUpdate(timer) {
    setInterval(function () {
        getUsers();
    }, timer);
}

function startSession() {
    $.ajax({
        type: "PATCH",
        url: getSessionBaseUrl(),
        data: JSON.stringify({
            "has_started": true
        })
    }).done(function () {
        location.reload();
    });
}

function getPawnInfo(async) {
    $.get({
        url: getPawnBaseUrl(),
        async: async
    }).done(function (data) {
        for (var i = 0; i < data.length; i++) {
            var pawn_obj = data[i];
            var id = String(pawn_obj.id);
            pawn[id] = pawn_obj.color;
        }
    });
}

function getUsersInfo(async) {
    $.get({
        url: getUsersQuery(),
        async: async
    }).done(function (data) {
        for (var i = 0; i < data.length; i++) {
            var user = data[i];
            var username = user.username;
            var id = String(user.id);
            users[id] = username;
        }
    });
    $.get({
        url: getOwnerBaseUrl(),
        async: async
    }).done(function (data) {
        var owner = data[0];
        var username = owner.username;
        var id = String(owner.id);
        users[id] = username;
    });
}

function getCityState(async) {
    $.get({
        url: getCityStateBaseUrl(),
        async: async
    }).done(function (data) {
        for (var i = 0; i < data.length; i++) {
            var city_state = data[i];
            var id = String(city_state.id);
            var render = false;
            var render_research_station = false;
            if (city_states.hasOwnProperty(id)) {
                var observed_state = city_states[id];
                var fetch_time = moment(city_state.last_changed);
                var observed_state_time = moment(observed_state.last_changed);
                if (fetch_time.isAfter(observed_state_time)) {
                    if (observed_state.research_station === false && city_state.research_station === true) {
                        render_research_station = true;
                    }
                    city_states[id] = city_state;
                    render = true;
                }
            } else {
                city_states[id] = city_state;
                render = true;
                render_research_station = city_state.research_station;
            }
            if (render) {
                if (!disease_layers.hasOwnProperty(id)) {
                    disease_layers[id] = {};
                }
                if (render_research_station) {
                    var research_station_delta_lat = (Math.round(Math.random()) * 2 - 1) * Math.floor((Math.random() * 0.5) + 1);
                    var research_station_delta_lon = (Math.round(Math.random()) * 2 - 1) * Math.floor((Math.random() * 0.5) + 1);
                    var city = city_object_data[String(city_state.city)];
                    var geojsonMarkerOptions = {
                        radius: 8,
                        fillColor: "#FFFFFF",
                        color: "#000",
                        weight: 1,
                        opacity: 1,
                        fillOpacity: 0.8
                    };
                    var geojsonFeature = {
                        "type": "Feature",
                        "properties": {
                            "name": city.name + " research_station",
                        },
                        "geometry": {
                            "type": "Point",
                            "coordinates": [city.latitude + research_station_delta_lat, city.longitude + research_station_delta_lon],
                        },
                    };
                    var geojsonObject = L.geoJSON(geojsonFeature, {
                        pointToLayer: function (feature, latlng) {
                            return L.circleMarker(latlng, geojsonMarkerOptions);
                        }
                    }).addTo(map);
                    geojsonObject.bindPopup("<b>Research Station</b>");
                }
                var _colors = ['Black', 'Yellow', 'Red', 'Blue'];
                for (var k = 0; k < _colors.length; k++) {
                    var _color = _colors[k];
                    if (!disease_layers[id].hasOwnProperty(_color)) {
                        disease_layers[id][_color] = [];
                    }

                    var delta;
                    if (_color === "Black") {
                        delta = city_state.black_cubes - disease_layers[id]["Black"].length;
                    } else if (_color === "Yellow") {
                        delta = city_state.yellow_cubes - disease_layers[id]["Yellow"].length;
                    } else if (_color === "Red") {
                        delta = city_state.red_cubes - disease_layers[id]["Red"].length;
                    } else {
                        delta = city_state.blue_cubes - disease_layers[id]["Blue"].length;
                    }

                    if (delta < 0) {
                        delta *= -1;
                        var j = 0;
                        while (j < delta) {
                            var layer = disease_layers[id][_color][0];
                            map.removeLayer(layer);
                            disease_layers[id][_color].splice(1, 0);
                            j++
                        }
                    } else if (delta > 0) {
                        var j = 0;
                        while (j < delta) {
                            var city = city_object_data[city_state.city];
                            var color;
                            if (_color === "Black") {
                                color = "#000000";
                            } else if (_color === "Yellow") {
                                color = "#e5e500";
                            } else if (_color === "Red") {
                                color = "#ff0000";
                            } else {
                                color = "#0000ff";
                            }
                            var geojsonMarkerOptions = {
                                radius: 8,
                                fillColor: color,
                                color: "#000",
                                weight: 1,
                                opacity: 1,
                                fillOpacity: 0.8
                            };
                            var random_delta_lat = (Math.round(Math.random()) * 2 - 1) * Math.floor((Math.random() * 0.5) + 1);
                            var random_delta_lon = (Math.round(Math.random()) * 2 - 1) * Math.floor((Math.random() * 0.5) + 1);
                            var geojsonFeature = {
                                "type": "Feature",
                                "properties": {
                                    "name": city.name + " block",
                                },
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [city.latitude + random_delta_lat, city.longitude + random_delta_lon],
                                },
                            };
                            var geojsonObject = L.geoJSON(geojsonFeature, {
                                pointToLayer: function (feature, latlng) {
                                    return L.circleMarker(latlng, geojsonMarkerOptions);
                                }
                            }).addTo(map);
                            geojsonObject.bindPopup("<b>Disease Block</b>");
                            disease_layers[id][_color].push(geojsonObject);
                            j++;
                        }
                    }
                }
            }
        }
    });
}

function init_all() {
    getCards(false);
    getPawnInfo(false);
    getUsersInfo(false);
    getCityState(false);
    getPlayerStates(false);
    getCureState(false);
    getCardState(false);
    getDiseaseState(false);
    getSessionState(false);
    buildEventHandlers();
    displayOtherPlayersCards();
}

function updateAll() {
    getCityState(true);
    getPlayerStates(true);
    getCureState(true);
    getCardState(true);
    getDiseaseState(true);
    getSessionState(true);
    updateStats();
    displayOtherPlayersCards();
}

function getCards(async) {
    $.get({
        url: getCardBaseUrl(),
        async: async
    }).done(function (data) {
        for (var i = 0; i < data.length; i++) {
            var card = data[i];
            var id = String(card.id);
            cards[id] = card;
        }
    });
}

function updatePlayerStates(data) {
    for (var i = 0; i < data.length; i++) {
        var player_state = data[i];
        var id = String(player_state.id);
        var render = false;
        if (!states.hasOwnProperty(id)) {
            states[id] = player_state;
            render = true;
            if (session_state != null && session_state.current_player === Number(USER_ID)) {
                populateOptions();
                updateStats();
            }
        } else {
            var observed_state = states[id];
            var fetch_time = moment(player_state.last_changed);
            var observed_state_time = moment(observed_state.last_changed);
            if (fetch_time.isAfter(observed_state_time)) {
                states[id] = player_state;
                if (session_state != null && session_state.current_player === Number(USER_ID)) {
                    populateOptions();
                    updateStats();
                }
                render = true;
            }
        }
        if (render) {
            var userId = String(player_state.user);
            var pawnColor = pawn[String(player_state.pawn)];
            var username = users[userId];
            var city = city_object_data[String(player_state.city)];
            var delta_lat = (Math.round(Math.random()) * 2 - 1) * Math.floor((Math.random() * 0.5) + 1);
            var delta_lon = (Math.round(Math.random()) * 2 - 1) * Math.floor((Math.random() * 0.5) + 1);
            if (user_layers.hasOwnProperty(userId)) {
                var layer_obj = user_layers[userId];
                map.removeLayer(layer_obj);
                delete user_layers[userId];
            }
            var geojsonMarkerOptions = {
                radius: 8,
                fillColor: pawnColor,
                color: "#000",
                weight: 1,
                opacity: 1,
                fillOpacity: 0.8
            };
            var geojsonFeature = {
                "type": "Feature",
                "properties": {
                    "name": username,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [city.latitude + delta_lat, city.longitude + delta_lon],
                },
            };
            var geojsonObject = L.geoJSON(geojsonFeature, {
                pointToLayer: function (feature, latlng) {
                    return L.circleMarker(latlng, geojsonMarkerOptions);
                }
            }).addTo(map);
            geojsonObject.bindPopup("<b>" + username + "</b>");
            user_layers[userId] = geojsonObject;
        }
    }
}

function getPlayerStates(async) {
    $.get({
        url: getPlayerStateBaseUrl(),
        async: async
    }).done(function (data) {
        updatePlayerStates(data);
    })
}

function findCityState(city_id) {
    for (var id in city_states) {
        var city_state = city_states[id];
        var city_pk = city_state.city;
        if (city_pk === city_id) {
            return id;
        }
    }
}

function findPlayerState(player_id) {
    for (var id in states) {
        var player_state = states[id];
        var user_pk = player_state.user;
        if (player_id === user_pk) {
            return id;
        }
    }
}

function canCure() {
    var blue;
    var red;
    var yellow;
    var black;
    for (var id in card_states) {
        var card_state = card_states[id];
        var card = cards[String(card_state.card)];
        if (card.card_type === "City") {
            if (card.color === "Black") {
                black++;
                if (black === 5) {
                    return "Black";
                }
            } else if (card.color === "Yellow") {
                yellow++;
                if (yellow === 5) {
                    return "Yellow";
                }
            } else if (card.color === "Red") {
                red++;
                if (red === 5) {
                    return "Red";
                }
            } else if (card.color === "Blue") {
                blue++;
                if (blue === 5) {
                    return "Blue";
                }
            }
        }
    }
    return null;
}

function buildCheck(city_id) {
    for (var id in card_states) {
        var card_state = card_states[id];
        var card = cards[String(card_state.card)];
        if (card.card_type === "City" && card.city === city_id) {
            return true;
        }
    }
    return false;
}

function populateOptions() {
    $("#commands").show();
    $("#cards").css({"visibility":"visible"});
    // move
    var possible_cities = [];
    var player_state_id = findPlayerState(Number(USER_ID));
    var player_state = states[player_state_id];
    var city_state_id = findCityState(player_state.city);
    var city_state = city_states[city_state_id];
    var city = city_object_data[city_state.city];
    if ($("#cards").children().length > 0) {
        $("#cards").empty();
    }
    for (var id in card_states) {
        var card_state = card_states[id];
        var card = cards[String(card_state.card)];
        if (card.card_type === "City") {
            if ($("#card-state-" + String(card_state.id)).length === 0) {
                var title = city_object_data[String(card.city)].name;
                var bg_color;
                var text_color = '';
                if (card.color === "Black") {
                    bg_color = "bg-dark";
                    text_color = " text-white";
                } else if (card.color === "Red") {
                    bg_color = "bg-danger";
                } else if (card.color === "Yellow") {
                    bg_color = "bg-warning";
                } else {
                    bg_color = "bg-primary";
                }
                $("#cards").append("<div class='card d-inline-block " + bg_color + text_color + "' id='card-state-" + String(card_state.id) + "' style='width: 18rem; cursor:pointer; height:50%;'>" +
                    "<div class='card-body'><h5>" + title + "</h5><p>Move to " + title + " or discard if in " + title + " to move anywhere.</p></div></div>");
            }
        } else {
            if ($("#card-state-" + String(card_state.id)).length === 0) {
                var title = card.description.split(":")[0];
                var description = card.description.split(":")[1];
                $("#cards").append("<div class='card d-inline-block' id='card-state-" + String(card_state.id) + "' style='width: 18rem; cursor:pointer'>" +
                    "<div class='card-body'><h5>" + title + "</h5><p>" + description + "</p></div></div>");
            }
        }
    }
    for (var id in city_states) {
        var _city_state = city_states[id];
        var _city = city_object_data[String(_city_state.city)];
        if ((id !== city_state_id && _city_state.research_station && city_state.research_station) || city.connections.indexOf(_city.name) !== -1) {
            possible_cities.push(_city_state.city);
        }
    }
    if ($("#moveModalBody").children().length > 0) {
        $("#moveModalBody").empty();
    }
    $("#moveModalBody").append("<ul></ul>");
    for (var i = 0; i < possible_cities.length; i++) {
        var id = possible_cities[i];
        var _city = city_object_data[String(id)];
        $("#moveModalBody ul").append("<li class='" + String(id) + "' style='cursor:pointer'>" + String(_city.name) + "</li>");
    }
    // treat
    if (city_state.black_cubes > 0 || city_state.yellow_cubes > 0 || city_state.red_cubes > 0 || city_state.blue_cubes > 0) {
        if ($("#treat").prop("disabled")) {
            $("#treat").prop("disabled", false);
        }
        $("#treatModalBody ul").empty();
        if (city_state.black_cubes > 0) {
            $("#treatModalBody ul").append("<li class='Black-disease' style='cursor:pointer;'>Black Disease</li>");
        }
        if (city_state.yellow_cubes > 0) {
            $("#treatModalBody ul").append("<li class='Yellow-disease' style='cursor:pointer;'>Yellow Disease</li>");
        }
        if (city_state.red_cubes > 0) {
            $("#treatModalBody ul").append("<li class='Red-disease' style='cursor:pointer;'>Red Disease</li>");
        }
        if (city_state.blue_cubes > 0) {
            $("#treatModalBody ul").append("<li class='Blue-disease' style='cursor:pointer;'>Blue Disease</li>");
        }
    } else {
        if (!$("#treat").prop("disabled")) {
            $("#treat").prop("disabled", true);
        }
    }
    // cure
    var can_cure = canCure();
    if (can_cure != null) {
        $("#cure").prop("disabled", false);
    } else {
        $("#cure").prop("disabled", true);
    }
    // build
    var build_check = buildCheck(city.id);
    if (build_check) {
        $("#build").prop("disabled", false);
    } else {
        $("#build").prop("disabled", true);
    }
    if (card_states.length === 0) {
        $("#share").prop("disabled", true);
    } else {
        $("#share").prop("disabled", false);
    }
}

function buildEventHandlers() {
    $("#move").click(function () {
        $("#moveModal").modal("show");
    });
    $("#moveModalBody").on("click", "li", function () {
        var id = $(this).prop("class");
        var player_state_id = findPlayerState(Number(USER_ID));
        $.ajax({
            type: "PATCH",
            url: getPlayerStateBaseUrl() + player_state_id + "/",
            data: JSON.stringify({
                city: Number(id)
            })
        }).done(function () {
            updateAll()
        });
        $("#moveModal").modal("hide");
    });
    $("#treatModalBody").on("click", "li", function () {
        var disease_color = $(this).prop("class").split("-")[0];
        var player_state = states[findPlayerState(Number(USER_ID))];
        var city_id = player_state.city;
        var city_state = city_states[findCityState(city_id)];
        var new_block_num;

        if (disease_color === "Black") {
            new_block_num = city_state.black_cubes - 1;
            $.ajax({
                type: "PATCH",
                url: getCityStateBaseUrl() + city_state.id + "/",
                data: JSON.stringify({
                    black_cubes: new_block_num
                })
            }).done(function () {
                updateAll()
            });
        } else if (disease_color === "Yellow") {
            new_block_num = city_state.yellow_cubes - 1;
            $.ajax({
                type: "PATCH",
                url: getCityStateBaseUrl() + city_state.id + "/",
                data: JSON.stringify({
                    yellow_cubes: new_block_num
                })
            }).done(function () {
                updateAll()
            });
        } else if (disease_color === "Red") {
            new_block_num = city_state.red_cubes - 1;
            $.ajax({
                type: "PATCH",
                url: getCityStateBaseUrl() + city_state.id + "/",
                data: JSON.stringify({
                    red_cubes: new_block_num
                })
            }).done(function () {
                updateAll()
            });
        } else if (disease_color === "Blue") {
            new_block_num = city_state.blue_cubes - 1;
            $.ajax({
                type: "PATCH",
                url: getCityStateBaseUrl() + city_state.id + "/",
                data: JSON.stringify({
                    blue_cubes: new_block_num
                })
            }).done(function () {
                updateAll()
            });
        }
        $("#treatModal").modal("hide");
    });
    $("#treat").click(function () {
        $("#treatModal").modal("show");
    });
    $("#cure").click(function () {
        var player_state = states[findPlayerState(Number(USER_ID))];
        var city_id = player_state.city;
        var city = city_object_data[String(city_id)];
        var card_state_ids = [];
        var cureColor = canCure();
        for (var id in card_states) {
            var card_state = card_states[id];
            var card_id = card_state.card;
            var card = cards[String(card_id)];
            if (card.color === cureColor && card.card_type === "City") {
                card_state_ids.push(id);
            }
        }
        $.ajax({
            type: "PATCH",
            url: getCureStateBaseUrl + "?color=" + cureColor + "/",
            data: JSON.stringify({
                "found": true,
                "extra": card_state_ids
            })
        }).done(function () {
            updateAll()
        });
    });
    $("#build").click(function () {
        var player_state = states[findPlayerState(Number(USER_ID))];
        var city_id = player_state.city;
        var city_state = city_states[findCityState(city_id)];
        $.ajax({
            type: "PATCH",
            url: getCityStateBaseUrl() + city_state.id + "/",
            data: JSON.stringify({
                "research_station": true
            })
        }).done(function () {
            updateAll()
        });
    });
    $("#share").click(function () {
        if (share) {
            share = false;
        } else {
            share = true;
        }
        $("#cards div.card").toggleClass("border-pulsate-class");
    });
    $("#cards").on("click", ".card", function () {
        var id = $(this).prop("id").split("-")[2];
        var card_state = card_states[id];
        var card = cards[String(card_state.card)];
        var player_state = states[findPlayerState(Number(USER_ID))];
        share_card_id = id;
        if (share) {
            if ($("#shareModalBody ul").children().length > 0) {
                $("#shareModalBody ul").empty();
            }
            for (var id in users) {
                var player_username = users[id];
                if (player_username !== USERNAME) {
                    $("#shareModalBody ul").append("<li style='cursor:pointer'>" + player_username + "</li>");
                }
            }
            $("#shareModal").modal("show");
        } else {
            if (card.card_type === "City") {
                if (card.city === player_state.city) {
                    $("#moveModalBody ul").empty();
                    for (var id in city_object_data) {
                        var city = city_object_data[id];
                        if (city.id !== player_state.city) {
                            $("#moveModalBody ul").append("<li style='cursor:pointer' class='" + city.id + "'>" + city.name + "</li>");
                        }
                    }
                    $("#moveModal").modal("show");
                    $.ajax({
                        type: "PATCH",
                        url: getCardStateBaseUrl() + id + "/",
                        data: JSON.stringify({
                            "user": null,
                            "extra": "Discard"
                        })
                    }).done(function () {
                        updateAll()
                    });
                } else {
                    $.ajax({
                        type: "PATCH",
                        url: getCardStateBaseUrl() + String(card_state.id) + "/",
                        data: JSON.stringify({
                            "user": null
                        })
                    }).done(function () {
                        updateAll()
                    });
                }
            } // e' aqui
        }
    });
    $("#shareModalBody ul").on("click", "li", function () {
        var player_username = $(this).text();
        $.ajax({
            type: "PATCH",
            url: getCardStateBaseUrl() + share_card_id + "/",
            data: JSON.stringify({
                "user": player_username
            })
        }).done(function () {
            updateAll()
        });
        $("#shareModal").modal("hide");
    });
    $("#pass").click(function () {
        $.ajax({
            type: "PATCH",
            url: getSessionStateBaseUrl() + session_state.id + "/",
            data: JSON.stringify({
                "current_player": null
            })
        }).done(function () {
            updateAll()
        });
    });
}

function updateStats() {
    if ($("#startedAt").text() === "") {
        $("#startedAt").text(START_DATE.format("DD/MM/YYYY hh:mm:ss"));
    }
    var cur_player_turn = $("#playerTurn").text();
    var cur_moves_left = $("#movesLeft").text();
    var cur_infection_rate = $("#infectionRate").text();
    var cur_outbreak_count = $("#outbreakCount").text();
    var player_state_id = findPlayerState(session_state.current_player);
    var cures_found = $("#CuresFound").text().split(",");
    if (cures_found.indexOf("") !== -1) {
        cures_found.splice(cures_found.indexOf(""), 1);
    }
    cures_found = cures_found.map(x => x.trim());
    var cures_found_len = cures_found.length;
    var diseases_erradicated = $("#DiseasesErradicated").text().split(",");
    if (diseases_erradicated.indexOf("") !== -1) {
        diseases_erradicated.splice(cures_found.indexOf(""), 1);
    }
    diseases_erradicated = diseases_erradicated.map(x => x.trim());
    var diseases_erradicated_len = diseases_erradicated.length;
    var player_state = states[player_state_id];
    if (cur_player_turn !== users[String(session_state.current_player)]) {
        $("#playerTurn").text(users[String(session_state.current_player)]);
    }
    if (cur_moves_left !== String(player_state.num_actions)) {
        $("#movesLeft").text(String(player_state.num_actions));
    }
    if (cur_infection_rate !== String(session_state.infection_rate)) {
        $("#infectionRate").text(String(session_state.infection_rate));
    }
    if (cur_outbreak_count !== String(session_state.outbreak_count)) {
        $("#outbreakCount").text(String(session_state.outbreak_count));
    }
    for (var id in disease_states) {
        disease_state = disease_states[id];
        if (disease_state.eradication_status) {
            if (diseases_erradicated.indexOf(disease_state.color) === -1) {
                diseases_erradicated.push(disease_state.color);
            }
        }
    }
    for (var id in cure_states) {
        cure_state = cure_states[id];
        if (cure_state.found) {
            if (cures_found.indexOf(cure_state.color) === -1) {
                cures_found.push(cure_state.color);
            }
        }
    }
    if (cures_found_len !== cures_found.length) {
        $("#CuresFound").text(cures_found.join(", "));
    }
    if (diseases_erradicated_len !== diseases_erradicated.length) {
        $("#DiseasesErradicated").text(diseases_erradicated.join(", "));
    }
    if (session_state.has_ended) {
        if (session_state.end_result === "Win") {
            if ($("#win_div").length === 0 && $("#dark_div").length === 0) {
                $("body").append("<div id='dark_div' style='z-index=99998;'></div><div id='win_div' class='alert alert-success' style='z-index=99999;'><div>Congrats you guys WON!!</div><a href='http://" + location.hostname + "' class='btn btn-primary'>Play again!</a></div>");
            }
        } else if (session_state.end_result === "Loss") {
            if ($("#loose_div").length === 0 && $("#dark_div").length === 0) {
                $("body").append("<div id='dark_div' style='z-index=99998;'></div><div id='loose_divs' class='alert alert-danger' style='z-index=99999;'><div>Better luck next time :/</div><a href='http://" + location.hostname + "' class='btn btn-primary'>Play again!</a></div>");
            }
        }
    }
}


function displayOtherPlayersCards() {
    for (var id in users) {
        var player_username = users[id];
        if (player_username !== USERNAME) {
            $.get({
                url: getCardStateBaseUrl() + "?player=" + player_username
            }).done(function (data) {
                var ids = [];
                var player_username;
                for (var i = 0; i < data.length; i++) {
                    var card_state = data[i];
                    var user = users[String(card_state.user)];
                    if (player_username == null) {
                        player_username = user;
                    }
                    var card = cards[String(card_state.card)];
                    ids.push(String(card_state.id));
                    if ($(".allCards-" + user + "-" + String(card_state.id)).length === 0) {
                        if (card.card_type === "City") {
                            var title = city_object_data[String(card.city)].name;
                            var bg_color;
                            var text_color = '';
                            if (card.color === "Black") {
                                bg_color = "bg-dark";
                                text_color = " text-white";
                            } else if (card.color === "Red") {
                                bg_color = "bg-danger";
                            } else if (card.color === "Yellow") {
                                bg_color = "bg-warning";
                            } else {
                                bg_color = "bg-primary";
                            }
                            $("#allCards-" + user).append("<div class='card allCards-" + user + "-" + String(card_state.id) + " " + bg_color + text_color + "' style='width: 18rem;'>" +
                                "<div class='card-body'><h5>" + title + "</h5><p>Move to " + title + " or discard if in " + title + " to move anywhere.</p></div></div>");
                        } else {
                            var title = card.description.split(":")[0];
                            var description = card.description.split(":")[1];
                            $("#allCards-" + user).append("<div class='card allCards-" + user + "-" + String(card_state.id) + "' style='width: 18rem;'>" +
                                "<div class='card-body'><h5>" + title + "</h5><p>" + description + "</p></div></div>");
                        }
                    }
                }
                var displayed_cards = $("#allCards-" + player_username + " div.card");
                for (var i = 0; i < displayed_cards.length; i++) {
                    var element = displayed_cards[i];
                    var id = element.classList[1].split("-")[2];
                    if (ids.indexOf(id) === -1) {
                        $("." + element.classList[1]).remove();
                    }
                }
            });
        }
    }
}