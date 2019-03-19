const canvas = document.getElementById("render");
const ctx = canvas.getContext("2d");
ctx.font = "16px Arial";
ctx.textAlign = "center";
canvas.width = $(document).height();
canvas.height = $(document).height();
document.body.style.overflow = "hidden";

var token;
var angle = 0;
var time = Date.now();
var data;
var rendering = false;
var ping = 40;
var runningTime = 1;
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
socket.on("token", function(data) {
    if (token === undefined) {
        token = data;
    }
});
canvas.onmousemove = function(evt) { // This is the function that changes the player direction when the player moves their mouse.
    var mx = evt.pageX - $('#render').offset().left - (canvas.width / 2);
    var my = evt.pageY - $('#render').offset().top - (canvas.height / 2);
    if (Math.hypot(mx, my) < 20) {
        angle = -1
    } else {
        angle = (Math.atan2(my, mx) * 180 / Math.PI);
    }
}
$("#nameForm").submit(function(evt) { // Sends our name to the server
    var name = document.getElementById('name').value;
    if (name.length === 0) {
        name = "Guest"
    }
    socket.emit("playerRequest", {
        token: token,
        name: name
    });
    document.getElementById("main").style = "display: none";
    evt.preventDefault();
});

function onBoardCalculations() {
    var t1 = Date.now();
    var entities = data[1];
    entities.forEach(function(entity) {
        entity.x += entity.vel_x * (runningTime/40);
        entity.y += entity.vel_y * (runningTime/40);
    })
    var t2 = Date.now();
    runningTime = t2-t1;
}

function render(timestamp) {
    var time1 = timestamp;
    var scale = canvas.width / 600;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    var player = data[0];
    var entities = data[1];
    entities.forEach(function(entity) {
        let cx = entity.x - player.x + 300;
        let cy = entity.y - player.y + 300;
        ctx.fillStyle = entity.color;
        ctx.beginPath();
        ctx.arc(cx * scale, cy * scale, entity.radius * scale, 0, 2 * Math.PI);
        ctx.fill();
        if (entity.name !== undefined) {
            ctx.fillStyle = "#ffffff";
            ctx.textAlign = "center";
            ctx.fillText(entity.name, cx * scale, cy * scale + 30 * scale);
        }
    })
    var time2 = Date.now();
    var diff = time2 - time1;
    window.requestAnimationFrame(render);
}
socket.on("playerInfoResponse", function(stuff) {
    if (data) {
        var dx = stuff[0].x - data[0].x;
        var dy = stuff[0].y - data[0].y;
        console.log(dx, dy);
    }
    data = stuff;
    ping = Date.now() - time;
    time = Date.now();
    if (!rendering) {
        window.requestAnimationFrame(render);
        onBoardCalculations();
        rendering = true;
    }
    if (data.length === 0) { // If the message is empty that means the player was just initialized.
        setTimeout(function() {
            socket.emit("playerInfoRequest", {
                token: token,
                angle: angle
            })
        }, 40 - ping);
        return;
    }
    setTimeout(function() {
        socket.emit("playerInfoRequest", {
            token: token,
            angle: angle
        })
    }, 40 - ping);
});
