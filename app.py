from flask import *
from flask_socketio import *
from framework import *
from functions import *
import os
import random
import sys
import math
import time


app = Flask(__name__)
app.secret_key = "taksa tapka"
socketio = SocketIO(app)
sys.setrecursionlimit(100000)
game = Game(2000)
for _ in range(0, 500):
    Wall(game, random.randint(-game.radius, game.radius), random.randint(-game.radius, game.radius))
for _ in range(0, 0):
    coin = Coin(game, random.randint(-game.radius, game.radius), random.randint(-game.radius, game.radius), 1)
    while coin.colliding():
        coin.delete()
        coin = Coin(game, random.randint(-game.radius, game.radius), random.randint(-game.radius, game.radius), 1)
players = dict()


@app.route("/")
def root():
    return send_from_directory("templates", "index2.html")


@app.route("/static/<filename>")
def static_file(filename):
    return send_from_directory("static", filename)


@socketio.on("connect")
def connect():
    token = random.randint(0, 100000)
    emit("token", str(token))
    print("Gave new client token "+str(token))


@socketio.on("playerRequest")
def add_player(data):
    player = Player(game, random.randint(-game.radius, game.radius), random.randint(-game.radius, game.radius), data["name"])
    #  The client already knows that we are going to initialize a new player, but they don't know the coordinates
    players[data["token"]] = player
    print("Assigned #"+data["token"]+" a new player object with name "+data["name"])
    emit("playerInfoResponse", [players[data["token"]].jsonify(), players[data["token"]].view])


@socketio.on("playerInfoRequest")
def send_info(data):
    players[data["token"]].ping = time.time()
    if data["firing"]:
        players[data["token"]].fire_bullet(data["angle"])
    players[data["token"]].direction = data["angle"]
    #if data["angle"] == -1:
    #    players[data["token"]].set_velocity(0, 0)
    #else:
    #    players[data["token"]].set_velocity(math.cos(math.radians(data["angle"]))*5, math.sin(math.radians(data["angle"]))*5)
    vx = 0
    vy = 0
    if data["keysDown"]["w"]:
        vy -= 5
    if data["keysDown"]["s"]:
        vy += 5
    if data["keysDown"]["a"]:
        vx -= 5
    if data["keysDown"]["d"]:
        vx += 5
    players[data["token"]].set_velocity(vx, vy)
    emit("playerInfoResponse", [players[data["token"]].jsonify(), players[data["token"]].view, game.running_time])


if __name__ == '__main__':
    game.update()
    print("Running")
    socketio.run(app, port=os.environ.get("PORT"), host="0.0.0.0")
