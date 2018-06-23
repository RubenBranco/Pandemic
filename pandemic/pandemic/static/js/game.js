    "use strict";

// STATES
var states = {};
var pawn = {};
var cards = {};
var users = {};
var city_object_data = {};
var user_layers = {};
var disease_layers = {};
var session_state;
var turn;
var cure_states = {};
var city_states = {};
var disease_states = {};
var card_states = {};
var my_player_state_id;
var share = false;
var share_card_id;
// END STATES
var map;

function main() {
    var refresh_time = 500;
    var bounds = new L.LatLngBounds(new L.LatLng(90.0, -180.0), new L.LatLng(-90.0, 180.0)); 
    map = L.map('map', {zoomControl: false, maxBounds: bounds, maxBoundsViscosity: 1.0});
    var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {attribution: osmAttrib, noWrap: true});		
    map.addLayer(osm).setView([-2.108898659243126, 11.77734375], 2);
    map.fitWorld().zoomIn();
    map.touchZoom.disable();
    map.doubleClickZoom.disable();
    map.scrollWheelZoom.disable();
    map.boxZoom.disable();
    getCities(map);
    var csrftoken = Cookies.get('csrftoken');
    $(".player-btn").click(function(){
        var username = $(this).text()
        $("#allCards-" + username).toggle();
    });
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                xhr.setRequestHeader("Content-Type", 'application/json');
            }
        }
    });
    setInterval(function(){refreshChat()}, refresh_time);
    handleChatSubmit();
    init_all();
    setInterval(function(){updateAll()}, refresh_time);
}

$(document).ready(function(){main();});