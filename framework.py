import time
import math
import threading


class Game:
    def __init__(self):
        self.entities = set()
        self.running_time = 0.01

    def update(self):
        t1 = time.time()
        for entity in list(self.entities):
            entity.act()
        t2 = time.time()
        self.running_time = t2-t1
        thr = threading.Thread(target=self.update)
        thr.start()

    def add_entity(self, entity):
        self.entities.add(entity)

    def remove_entity(self, entity):
        self.entities.remove(entity)


class Entity:
    def __init__(self, game, x, y):
        self.game = game
        self.game.add_entity(self)
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.radius = 0
        self.it = "entity"
        self.color = "#ffffff"

    def delete(self):
        self.game.remove_entity(self)
        del self

    def act(self):
        self.x += self.vel_x * (self.game.running_time*25)
        self.y += self.vel_y * (self.game.running_time*25)

    def colliding(self):
        for entity in self.game.entities:
            delta_x = entity.x - self.x
            delta_y = entity.y - self.y
            if math.hypot(abs(delta_x), abs(delta_y)) < self.radius+entity.radius and entity != self:
                return entity
        return False

    def colliding_with(self, entity):
        delta_x = entity.x - self.x
        delta_y = entity.y - self.y
        if math.hypot(abs(delta_x), abs(delta_y)) < self.radius+entity.radius and entity != self:
            return True
        return False

    def jsonify(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "it": self.it,
            "color": self.color,
            "vel_x": self.vel_x,
            "vel_y": self.vel_y
        }


class Coin(Entity):
    def __init__(self, game, x, y, value):
        Entity.__init__(self, game, x, y)
        self.value = value
        self.radius = 10
        self.it = "coin"
        self.color = "#fdd700"


class Wall(Entity):
    def __init__(self, game, x, y):
        Entity.__init__(self, game, x, y)
        self.radius = 50
        self.it = "wall"
        self.color = "#ffffff"


class Player(Entity):
    def __init__(self, game, x, y, name):
        Entity.__init__(self, game, x, y)
        self.name = name
        self.radius = 20
        self.score = 0
        self.view = list()
        self.it = "player"
        self.ping = time.time()
        self.hp = 100

    def set_velocity(self, vel_x, vel_y):
        self.vel_x = vel_x
        self.vel_y = vel_y
        if self.x > 2000 and self.vel_x > 0:
            self.vel_x = 0
        if self.y > 2000 and self.vel_y > 0:
            self.vel_y = 0
        if self.x < -2000 and self.vel_x < 0:
            self.vel_x = 0
        if self.y < -2000 and self.vel_y < 0:
            self.vel_y = 0

    def handle_collisions(self):
        self.new_view = list()
        for entity in list(self.game.entities):
            if abs(self.x-entity.x) < 300+entity.radius and abs(self.y-entity.y) < 300+entity.radius:
                self.new_view.append(entity.jsonify())
            if self.colliding_with(entity):
                if type(entity) == Coin:
                    self.score += entity.value
                    entity.delete()
                if type(entity) == Wall:
                    self.vel_x = -self.vel_x
                    self.vel_y = -self.vel_y
                    while self.colliding_with(entity):
                        self.x += self.vel_x
                        self.y += self.vel_y
                    self.vel_x = -self.vel_x
                    self.vel_y = -self.vel_y
        self.view = self.new_view

    def act(self):
        if time.time() - self.ping >= 3:
            print("Player "+self.name+" has disconnected")
            self.delete()
        Entity.act(self)
        self.handle_collisions()

    def jsonify(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "it": self.it,
            "name": self.name,
            "color": self.color,
            "score": self.score,
            "hp": self.hp,
            "vel_x": self.vel_x,
            "vel_y": self.vel_y
        }
