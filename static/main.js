const canvas = document.getElementById("render");
const ctx = canvas.getContext("2d");
ctx.font = "16px Arial";
ctx.textAlign = "center";
canvas.width = $(document).height();
canvas.height = $(document).height();
document.body.style.overflow = "hidden";
ctx.imageSmoothingEnabled = true;


var token;
var angle = 0;
var actualAngle = 0;
var time = Date.now()/1000;
var data = [{},
    []
];
var rendering = false;
var ping = 40;
var reloading = false;
var runningTime = 1;
var currentFps = 0;
var fps = 0;
var fpsCut = Date.now();
var firing = false;
var dataLastUpdated = Date.now();
var keysDown = {
    "KeyW": false,
    "KeyA": false,
    "KeyS": false,
    "KeyD": false
}
var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

var oldName = window.localStorage.getItem("name");
if (oldName) {
    document.getElementById("name").value = oldName;
}

function radians(degrees) {
    return degrees / 180 * Math.PI;
}
socket.on("token", function(data) {
    if (token === undefined) {
        token = data;
    }
});
document.onkeydown = function(evt) {
    keysDown[evt.code] = true;
}
document.onkeyup = function(evt) {
    keysDown[evt.code] = false;
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
    window.localStorage.setItem("name", name);
    evt.preventDefault();

});
var calculationsLastTime = Date.now();

/* function onBoardCalculations() {
    var t1 = Date.now();
    var entities = data[1];
    var player = data[0];
    entities.forEach(function(entity) {
        var now = Date.now() / 1000;
        entity.x += entity.vel_x * (now - entity.last_updated) * 25;
        entity.y += entity.vel_y * (now - entity.last_updated) * 25;
        entity.last_updated = now;
    })
    if (keysDown.w) {
        player.vel_y += -5;
    }
    if (keysDown.s) {
        player.vel_y += 5;
    }
    if (keysDown.a) {
        player.vel_x += -5;
    }
    if (keysDown.d) {
        player.vel_x += 5;
    }
    var t2 = Date.now();
    runningTime = t2 - t1;
    data[1] = entities;
    setTimeout(onBoardCalculations, 1);
} */
function updateEntity(entity) {
    var now = Date.now() / 1000;
    entity.x += entity.vel_x * (now - dataLastUpdated) * 25;
    entity.y += entity.vel_y * (now - dataLastUpdated) * 25;
    entity.last_updated = now;
}
function renderEntity(entity) {
    var player = data[0];
    var scale = canvas.width / 600;
    let cx = entity.x - player.x + 300;
    let cy = entity.y - player.y + 300;
    if (entity.dead) {
        return;
    }
    ctx.fillStyle = entity.color;
    ctx.strokeStyle = entity.outline;
    ctx.lineWidth = 3 * scale;
    ctx.beginPath();
    ctx.arc(cx * scale, cy * scale, entity.radius * scale, 0, 2 * Math.PI);
    ctx.fill();
    ctx.stroke();
    if (entity.name !== undefined) {
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.font = "16px Arial";
        ctx.fillText(entity.name, cx * scale, cy * scale + 30 * scale);
    }
    if (entity.it == "player" || entity.it == "enemy") {
        ctx.beginPath();
        ctx.fillStyle = "#ffffff";
        ctx.textAlign = "center";
        ctx.font = "16px Arial";
        ctx.fillText("Score: "+entity.score, cx * scale, cy * scale - 30 * scale);
        ctx.beginPath();
        ctx.strokeStyle = "#999999";
        ctx.lineCap = "round";
        ctx.lineWidth = 10 * scale;
        ctx.moveTo(cx * scale, cy * scale);
        //ctx.lineTo(cx*scale+5, cy*scale+5);
        ctx.lineTo((cx * scale) + (Math.cos(radians(entity.direction)) * scale * 50), (cy * scale) + (Math.sin(radians(entity.direction)) * scale * 50));
        ctx.stroke();
        ctx.beginPath();
        ctx.strokeStyle = "#aa0000";
        ctx.lineCap = "round";
        ctx.lineWidth = 10 * scale;
        ctx.moveTo(cx * scale - (20 * scale), cy * scale + (40 * scale));
        ctx.lineTo(cx * scale + (20 * scale), cy * scale + (40 * scale));
        ctx.stroke();
        ctx.beginPath();
        ctx.strokeStyle = "#00aa00";
        ctx.lineCap = "round";
        ctx.lineWidth = 8 * scale;
        if (entity.hp > 0) {
            let healthThing = entity.hp / 2.5;
            ctx.beginPath();
            ctx.moveTo(cx * scale - (20 * scale), cy * scale + (40 * scale));
            ctx.lineTo(cx * scale + ((healthThing - 20) * scale), cy * scale + (40 * scale));
            ctx.stroke();
        }
    }
    if (entity.it == "tree") {
        ctx.beginPath();
        ctx.fillStyle = "#53840a";
        ctx.globalAlpha = 0.6;
        ctx.arc(cx * scale, cy * scale, entity.radius * scale * 5, 0, 2 * Math.PI);
        ctx.fill();
        ctx.globalAlpha = 1;
    }

}

function render(timestamp) {
    if (!data[3]) {
        window.requestAnimationFrame(render);
        return;
    }
    var time1 = timestamp;
    var scale = canvas.width / 600;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#000000";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    var entities = data[1];
    var trees = data[3].tree;
    var players = data[3].player;
    var bullets = data[3].bullet;
    var enemies = data[3].enemy;
    var walls = data[3].wall;
    /*if (keysDown.w) {
        data[0].vel_y += -5;
    }
    if (keysDown.s) {
        data[0].vel_y += 5;
    }
    if (keysDown.a) {
        data[0].vel_x += -5;
    }
    if (keysDown.d) {
        data[0].vel_x += 5;
    }*/
    updateEntity(data[0]);
    var player = data[0];
    if (enemies) {
        enemies.forEach(renderEntity);
        enemies.forEach(updateEntity);
    }
    if (walls) {
        walls.forEach(renderEntity);
        walls.forEach(updateEntity);
    }
    if (players) {
        players.forEach(renderEntity);
        players.forEach(updateEntity);
    }
    if (bullets) {
        bullets.forEach(renderEntity);
        bullets.forEach(updateEntity);
    }
    if (trees) {
        trees.forEach(renderEntity);
        trees.forEach(updateEntity);

    }
    dataLastUpdated = Date.now()/1000;
    if (player.dead) {
        ctx.fillStyle = "#ff0000";
        ctx.font = "100px Arial";
        ctx.textAlign = "center";
        ctx.fillText("You died :(", 300 * scale, 300 * scale);
        if (!reloading) {
            setTimeout(function() {
                location.reload(true)
            }, 1000);
            reloading = true;
        }
    }
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "left";
    ctx.font = "16px Arial";
    ctx.fillText(ping + "ms", 20 * scale, 20 * scale);
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "right";
    ctx.font = "16px Arial";
    ctx.fillText(fps + " fps", 570 * scale, 20 * scale);
    var time2 = Date.now();
    var diff = time2 - time1;
    if (Date.now() - fpsCut > 1000) {
        fps = currentFps;
        fpsCut = Date.now();
        currentFps = 0;
    } else {
        currentFps += 1;
    }

    window.requestAnimationFrame(render);
}

socket.on("playerInfoResponse", function(stuff) {
    if (data) {
        var dx = stuff[0].x - data[0].x;
        var dy = stuff[0].y - data[0].y;
    }
    data = stuff;
    dataLastUpdated = Date.now()/1000;
    ping = Date.now() - time;
    time = Date.now();
    var int;
    if (ping < 17) {
        int = 17 - ping;
    } else {
        int = 1;
    }
    if (data.length === 0) { // If the message is empty that means the player was just initialized.
        setTimeout(function() {
            socket.emit("playerInfoRequest", {
                token: token,
                angle: actualAngle,
                firing: firing,
                keysDown: keysDown
            })
        }, int);
        return;
    }
    setTimeout(function() {
        socket.emit("playerInfoRequest", {
            token: token,
            angle: actualAngle,
            firing: firing,
            keysDown: keysDown
        })
    }, int);
});
window.requestAnimationFrame(render);
