"use strict";

function update_session_list() {
    $.get({url: SESSION_BASE_URL}).done(function(data) {
        for (var i = 0; i < data.length; i++)  {
            var session_data = data[i];
            var session_hash = session_data.session_hash;
            var element = $("#room_" + session_hash)
            
            if (!session_data.has_started && session_data.users.length + 1 < session_data.max_players && element.length === 0) {
                var element_line = "<div class='col-sm-8' id='room_" + session_data.session_hash + "'>";
                element_line += "<div class='card game-room' style='margin-bottom: 15px; margin-top: 10%;'>";
                element_line += "<div class='card-header'><span class='card-title' style='font-weight: bold;'>Waiting for players</span>";
                if (session_data.locked) {
                    element_line += "<span><img class='lock' src='/static/img/locked.png' alt='locked'></span>";
                } else {
                    element_line += "<span><img class='lock' src='/static/img/unlocked.png' alt='unlocked'></span>";
                }
                element_line += "</div><div class='card-body' style='height: 10vh !important;'>";
                element_line += "<span class='card-title session-name'>" + session_data.name + "</span><div class='card-text game-info'>";
                element_line += "<span class='room-space players'>" + String(session_data.users.length + 1) + "</span>";
                element_line += "<span class='room-space dash'>/</span>";
                element_line += "<span class='room-space maxplayers'>" + String(session_data.max_players) + "</span>";
                element_line += "<a href='/game/session/" + session_data.session_hash + "'><img class='play-btn' src='/static/img/play-button256.png'></a>";
                element_line += "</div></div></div></div>";
                $("#home div.container-fluid").append(element_line);
            } else if ((!session_data.has_started && session_data.users.length + 1 == session_data.max_players && element.length !== 0) || (session_data.has_started && element.length !== 0)) {
                element.remove();
            } 
        }
    });
}

function main() {
    var refresh_time = 500;
    var csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                xhr.setRequestHeader("Content-Type", 'application/json');
            }
        }
    });
    setInterval(function() {update_session_list()}, refresh_time);
}

$(document).ready(function(){main()});