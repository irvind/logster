$(function() {
    'use strict';

    var socket = new WebSocket('ws://localhost:8888/websock?token=' + wsToken);
    var logBox = $('.log-box');

    socket.onopen = function() {
        console.log('Websocket was openned');
        logBox.html('');
        // socket.send('Hello!');
    };

    socket.onmessage = function(msg) {
        var obj = JSON.parse(msg.data);
        
        logBox.append('<p>' + obj.message + '</p>');
        console.log('New message:', obj);
    };
});
