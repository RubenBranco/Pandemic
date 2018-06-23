function loadMessage(data) {
    var message_date = data.date_time;
    var username = data.sender;
    var text = data.text;
    var message_id = data.id;
    var message = "[" + message_date + "] " + username + ": " + text
    $("#chat_box").append("<div class='message' style='color:white' id='" + message_id + "'+>" + message + "</div>");
}

function get_query_params() {
    var chat_messages = $("#chat_box").children();
    if (chat_messages.length === 0) {
        return '';
    } 
    return "?last_comment=" + String(chat_messages.last().prop('id'));
}


function refreshChat() {
    $.get({url: CHAT_MESSAGE_BASE_URL + get_query_params()}).done(function(data) {
        for (var i = 0; i < data.length; i++) {
            loadMessage(data[i]);
        }
    });
}

function eventProcess() {
    var chat_textarea = $("#chat_textarea");
    var message = chat_textarea.val();
    if (message != "") {
        $.post({url: CHAT_MESSAGE_BASE_URL, data: JSON.stringify({"text": message})}).done(function(){
            refreshChat();
            chat_textarea.val('');
        });
    }
}
function handleChatSubmit() {
    $("#submit_message").click(function(){
        eventProcess();
    });
    $("#chat_textarea").keyup(function(e){
        if (e.which === 13) {
            eventProcess();
        }
    });
}
