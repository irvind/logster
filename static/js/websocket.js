$(function() {
    'use strict';

    var listenLog = 'test_log',
        logBox = $('.log-box');

    var socket = new WebSocket('ws://localhost:8888/websock?log=' + listenLog);

    socket.onopen = function() {
        console.log('Websocket was openned');
    };

    socket.onmessage = function(msg) {
        var resp = JSON.parse(msg.data);
        console.log('New message:', resp);

        if (resp['message_type'] == 'error') {
            alert(resp['error']);
        } else if (resp['message_type'] == 'new_entries') {
            var entry;
            for (var i = 0; i < resp.entries.length; i++) {
                entry = resp.entries[i];
                logBox.append('<p data-order="' + entry.order + '">'
                    + entry.content + '</p>');
            }
        }
    };
});
