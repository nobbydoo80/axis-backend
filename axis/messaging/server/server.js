var express = require('express');
var http = require('http');
var os = require('os');
var path = require('path');
var process = require('process');

var uuid = require('node-uuid');  // for tagging clients upon connecting
var dotenv = require('dotenv');
dotenv.config({ path: path.resolve(process.cwd(), '..', '..', '..', '.env') });

var HOSTNAME = null;
var DJANGO_HTTP_PORT = null;
var WEBSOCKET_ENDPOINT = null;
if (/\.pivotalenergy\.net$/.test(os.hostname()) || /ip-\d+-\d+-\d+-\d+/.test(os.hostname())) {
    // nginx is listening on a separate channel for our internal-only communications on this port
    HOSTNAME = '127.0.0.1';
    DJANGO_HTTP_PORT = 8003;
    WEBSOCKET_ENDPOINT = '/';
    console.log("Production enabled " + HOSTNAME + ":" + DJANGO_HTTP_PORT)
} else {
    if (/^[a-f0-9]{6}[a-f0-9]+$/.test(os.hostname())) {
        HOSTNAME = process.env.APP_HOST || 'app';
        DJANGO_HTTP_PORT = process.env.DJANGO_HTTP_PORT || 8000;
        WEBSOCKET_ENDPOINT = '/';
        console.log("Docker enabled " + HOSTNAME + ":" + DJANGO_HTTP_PORT)
    }else {
        HOSTNAME = 'localhost';
        DJANGO_HTTP_PORT = process.env.DJANGO_HTTP_PORT || 8000;
        WEBSOCKET_ENDPOINT = '/services/websocket';
        console.log("Localhost enabled " + HOSTNAME + ":" + DJANGO_HTTP_PORT)
    }
}
var short_hostname = os.hostname().split('.', 1)[0];

var WEBSOCKET_API_TOKEN = process.env.WEBSOCKET_API_TOKEN;
var INCOMING_WEBSOCKET_PORT = 8080;  // nginx proxies and delivers to us on this port
var PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT = process.env.PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT || 8002;  // choosen arbitrarily in python server code
var URLS = {
    'websocket_endpoint': WEBSOCKET_ENDPOINT,
    'websocket_channel': '/messages',  // incoming connections, subsequent back-and-forth

    // private Django server will listen for POSTs here
    'push': '/push',
    'read': '/read',

    // Endpoints on the Django server that the node server will use to make sure that the Django
    // process knows about the user's various websocket client_ids
    'websocket_start': '/api/v2/messaging/websocket/__session__/__clientid__/start/?host=__hostname__',
    'websocket_end': '/api/v2/messaging/websocket/__session__/__clientid__/end/',
    'websocket_readreceipts': '/api/v2/messaging/websocket/__session__/__messageid__/read/'
}

//console.log("Using token =", WEBSOCKET_API_TOKEN, "for access to private API.");
console.log("Token defined and in use for access to private API")

var websocket_app = express();
var websocket_http = http.Server(websocket_app);
var websocket_io = require('socket.io', {
    'pingInterval': 10000,
    'pingTimeout': 15000
})(websocket_http, {path: URLS.websocket_endpoint});

// Responder for requests to open new sockets to web clients
var clients = {};
var sessions = {};
websocket_io.of(URLS.websocket_channel).on('connection', function(socket){
    var client_id = uuid.v4();
    console.log('connection:', client_id);

    socket.emit('connect:acknowledge', client_id);
    socket.on('connect:ready', function(session_key){
        console.log('Associate :', client_id, short_hostname);
        saveSocketInfo(session_key);
    });
    socket.on('message:read', function(message_id){
        djangoApi(URLS.websocket_readreceipts, message_id);
    });
    socket.on('disconnect', function(){
        console.log('Disconnect:', client_id);

        // Tell Django to forget the client_id
        djangoApi(URLS.websocket_end);

        delete clients[client_id];
        delete sessions[client_id];
    });

    function djangoApi(url, message_id){
        if (message_id !== undefined) {
            url = url.replace('__messageid__', message_id);
        }
        url = url.replace('__session__', sessions[client_id])
                 .replace('__clientid__', client_id)
                 .replace('__hostname__', short_hostname)
        http.request({
            'host': HOSTNAME,
            'path': url,
            'port': DJANGO_HTTP_PORT,
            'method': 'GET',//DELETE
            'headers': {'Authorization': 'Token ' + WEBSOCKET_API_TOKEN}
        }).end();
    }
    function saveSocketInfo(session_key) {
        // Record the fact of the connection for internal private django server to use
        clients[client_id] = socket;
        sessions[client_id] = session_key;
        // Tell Django about the socket identifier
        djangoApi(URLS.websocket_start);
    }
});
websocket_http.listen(INCOMING_WEBSOCKET_PORT, function(){
    console.log('Websocket listening on localhost:' + INCOMING_WEBSOCKET_PORT);
});


// Local-only private communication channel with django app
var django_app = express();
var django_http = require('http').Server(django_app);
django_app.use(require('body-parser').json());
django_app.listen(PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT, function(){
    console.log('Private server for posting back to Django on ' + HOSTNAME + ':' + PRIVATE_DJANGO_HTTP_COMMUNICATIONS_PORT)
});
django_app.post(URLS.push, function(request, response){
    console.log("Received push message for client(s)", request.body.client_ids);
    var client_ids = request.body.client_ids;
    for (var i in client_ids) {
        var client_id = client_ids[i];
        if (client_id in clients) {
            clients[client_id].emit('message:push', request.body.message);
        } else {
            // client_id was terminated before Django app new about it
        }
    }
    response.send("OK");
});
django_app.post(URLS.read, function(request, response){
    console.log("Received read receipt for message(s) ", request.body.message_ids," client(s)", request.body.client_ids);
    var client_ids = request.body.client_ids;
    for (var i in client_ids) {
        var client_id = client_ids[i];
        if (client_id in clients) {
            clients[client_id].emit('message:read_bulk', request.body.message_ids);
        } else {
            // client_id was terminated before Django app new about it
        }
    }
    response.send("OK");
});

process.on('SIGINT', function () {
    console.log("Killing myself!")
    process.exit();
});
