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
game = Game()
for _ in range(0, 500):
    Wall(game, random.randint(-2000, 2000), random.randint(-2000, 2000))
for _ in range(0, 2000):
    coin = Coin(game, random.randint(-2000, 2000), random.randint(-2000, 2000), 1)
    while coin.colliding():
        coin.delete()
        coin = Coin(game, random.randint(-2000, 2000), random.randint(-2000, 2000), 1)
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
    player = Player(game, random.randint(-2000, 2000), random.randint(-2000, 2000), data["name"])
    #  The client already knows that we are going to initialize a new player, but they don't know the coordinates
    players[data["token"]] = player
    print("Assigned #"+data["token"]+" a new player object with name "+data["name"])
    emit("playerInfoResponse", [players[data["token"]].jsonify(), players[data["token"]].view])


@socketio.on("playerInfoRequest")
def send_info(data):
    players[data["token"]].ping = time.time()
    if data["angle"] == -1:
        players[data["token"]].set_velocity(0, 0)
    else:
        players[data["token"]].set_velocity(math.cos(math.radians(data["angle"]))*5, math.sin(math.radians(data["angle"]))*5)
    emit("playerInfoResponse", [players[data["token"]].jsonify(), players[data["token"]].view])


if __name__ == '__main__':
    set_interval(game.update, 0.001)
    print("Running")
    socketio.run(app, port=os.environ.get("PORT"), host="0.0.0.0")
