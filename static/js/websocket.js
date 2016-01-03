console.log('Opening websocket');

var socket = new WebSocket('ws://localhost:8888/websock?token=' + wsToken);

socket.onopen = function() {
    // socket.send('Hello!');
};

socket.onmessage = function(msg) {
    console.log(msg.data);
};