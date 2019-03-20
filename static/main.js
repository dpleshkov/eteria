const canvas = document.getElementById("render");
const ctx = canvas.getContext("2d");
ctx.font = "16px Arial";
ctx.textAlign = "center";
canvas.width = $(document).height();
canvas.height = $(document).height();
document.body.style.overflow = "hidden";



var token;
var angle = 0;
var actualAngle = 0;
var time = Date.now();
var data;
var rendering = false;
var ping = 40;
var runningTime = 1;
var firing = false;
var keysDown = {
    "w": false,
    "a": false,
    "s": false,
    "d": false
}
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);



socket.on("token", function(data) {
    if (token === undefined) {
        token = data;
    }
});
document.onkeydown = function(evt) {
    keysDown[evt.key] = true;
}
document.onkeyup = function(evt) {
    keysDown[evt.key] = false;
}
canvas.onmousemove = function(evt) { // This is the function that changes the player direction when the player moves their mouse.
    var mx = evt.pageX - $('#render').offset().left - (canvas.width / 2);
    var my = evt.pageY - $('#render').offset().top - (canvas.height / 2);
    if (Math.hypot(mx, my) < 20) {
        angle = -1
    } else {
        angle = (Math.atan2(my, mx) * 180 / Math.PI);
    }
    actualAngle = (Math.atan2(my, mx) * 180 / Math.PI);
}
canvas.onmousedown = function(evt) {
    if (evt.button == 0) {
        firing = true;
    }
}
canvas.onmouseup = function(evt) {
    if (evt.button == 0) {
        firing = false;
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
        entity.x += entity.vel_x * (runningTime / 40);
        entity.y += entity.vel_y * (runningTime / 40);
    })
    var t2 = Date.now();
    runningTime = t2 - t1;
}

function render(timestamp) {
    var time1 = timestamp;
    var scale = canvas.width / 600;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "left";
    ctx.font = "16px Arial";
    ctx.fillText(ping + "ms", 20 * scale, 20 * scale);
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
            ctx.font = "16px Arial";
            ctx.fillText(entity.name, cx * scale, cy * scale + 30 * scale);
        }
        if (entity.it == "player") {
            ctx.beginPath();
            ctx.strokeStyle = "#aa0000";
            ctx.lineCap = "round";
            ctx.lineWidth = 10;
            ctx.moveTo(cx * scale - (20 * scale), cy * scale + (40 * scale));
            ctx.lineTo(cx * scale + (20 * scale), cy * scale + (40 * scale));
            ctx.stroke();
            ctx.beginPath();
            ctx.strokeStyle = "#00aa00";
            ctx.lineCap = "round";
            ctx.lineWidth = 8;
            if (entity.hp > 0) {
                let healthThing = entity.hp / 2.5
                ctx.moveTo(cx * scale - (20 * scale), cy * scale + (40 * scale));
                ctx.lineTo(cx * scale + ((healthThing - 20) * scale), cy * scale + (40 * scale));
                ctx.stroke();
            }
        }
    });
    if (player.dead) {
        ctx.fillStyle = "#ff0000";
        ctx.font = "100px Arial";
        ctx.textAlign = "center";
        ctx.fillText("You died :(", 300 * scale, 300 * scale);
        setTimeout(function() {
            location.reload(true)
        }, 3000);
    }
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
                angle: actualAngle,
                firing: firing,
                keysDown: keysDown
            })
        }, 1);
        return;
    }
    setTimeout(function() {
        socket.emit("playerInfoRequest", {
            token: token,
            angle: actualAngle,
            firing: firing,
            keysDown: keysDown
        })
    }, 1);
});
