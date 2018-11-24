function init() {
    const canvas = document.getElementById("render");
    const ctx = canvas.getContext("2d");
    ctx.font = "16px Arial";
    ctx.textAlign = "center";
    canvas.width = $(document).height();
    canvas.height = $(document).height();
    document.body.style.overflow = "hidden";
    var token;
    var angle = 0;
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on("token", function (data) {
        if (token === undefined) {
            token = data;
        }
    });
    canvas.onmousemove = function (evt) {
        var mx = evt.pageX - $('#render').offset().left - (canvas.width / 2);
        var my = evt.pageY - $('#render').offset().top - (canvas.height / 2);
        if (Math.hypot(mx, my) < 20) {
            angle = -1
        } else {
        angle = (Math.atan2(my, mx) * 180 / Math.PI);
        }
    }
    $("#nameForm").submit(function (evt) {
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
    socket.on("playerInfoResponse", function (data) {
        if (data.legth === 0) {
            setTimeout(function () {
                socket.emit("playerInfoRequest", {
                    token: token,
                    angle: angle
                })
            }, 40);
            return;
        }
        var scale = canvas.width/600;
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var player = data[0];
        var entities = data[1];
        entities.forEach(function (entity) {
            let cx = entity.x - player.x + 300;
            let cy = entity.y - player.y + 300;
            ctx.fillStyle = entity.color;
            ctx.beginPath();
            ctx.arc(cx*scale, cy*scale, entity.radius*scale, 0, 2 * Math.PI);
            ctx.fill();
            if (entity.it == "player") {
                ctx.fillStyle = "#000000";
                ctx.textAlign="center";
                ctx.fillText(entity.name, cx*scale, cy*scale + 30*scale);
            }
        })
        setTimeout(function () {
            socket.emit("playerInfoRequest", {
                token: token,
                angle: angle
            })
        }, 40);
    });
}
init();
