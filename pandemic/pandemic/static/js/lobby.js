"use strict";

function getSessionId() {
    return location.pathname.split('/')[3];
}

function checkStart() {
    $.get({url: getSessionBaseUrl()}).done(function(data) {
        var session = data;
        if (session.has_started) {
            location.reload();
        }
    });
}

function check_players(){
    var number_players = $(".col-sm-8 div.card").length;
    if (number_players < 2){
         $('#start-game').prop("disabled", true);
    } else {
        $("#start-game").prop("disabled", false);
    }
}


function main() {
    var refresh_time = 500
    var csrftoken = Cookies.get('csrftoken');
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
                xhr.setRequestHeader("Content-Type", 'application/json');
            }
        }
    });
    check_players()
    setInterval(function(){refreshChat()}, refresh_time);
    handleChatSubmit();
    scheduleUsersUpdate(refresh_time);
    setInterval(function(){check_players()}, refresh_time)
    setInterval(function(){checkStart()}, refresh_time)
    $("#start-game").click(function(){startSession();});
}

$(document).ready(function(){main()})