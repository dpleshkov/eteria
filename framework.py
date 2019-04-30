from functions import *
import time
import math
import threading
import random


class Game:
    def __init__(self, radius=2000):
        self.entities = set()
        self.running_time = 0.01
        self.radius = radius
        self.last_time = time.time()
        self.mapped_entities = dict()

    def update(self):
        self.running_time = round((time.time()-self.last_time)*1000)
        self.last_time = time.time()
        for entity in list(self.entities):
            entity.act()
        thr = threading.Thread(target=self.update)
        thr.start()

    def add_entity(self, entity):
        self.entities.add(entity)
        if entity.it in self.mapped_entities:
            self.mapped_entities[entity.it].append(entity)
        else:
            self.mapped_entities[entity.it] = [entity]

    def remove_entity(self, entity):
        self.entities.remove(entity)


class Entity:
    def __init__(self, game, x, y):
        self.game = game
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.radius = 0
        self.it = "entity"
        self.color = "#ffffff"
        self.game.add_entity(self)
        self.last_updated = time.time()
        self.outline = "#ffffff"

    def delete(self):
        self.game.remove_entity(self)
        del self

    def distance_to(self, entity):
        return distance(self.x, self.y, entity.x, entity.y)

    def act(self):
        now = time.time()
        self.x += self.vel_x * (now - self.last_updated) * 25
        self.y += self.vel_y * (now - self.last_updated) * 25
        self.last_updated = time.time()

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
            "vel_y": self.vel_y,
            "last_updated": self.last_updated,
            "outline": self.outline
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
        self.outline = "#aaaaaa"

class Tree(Entity):
    def __init__(self, game, x, y):
        Entity.__init__(self, game, x, y)
        self.radius = 25
        self.it = "tree"
        self.color = "#533118"
        self.outline = "#975445"


class Bullet(Entity):
    def __init__(self, game, x, y, sender, vel_x, vel_y):
        Entity.__init__(self, game, x, y)
        self.radius = 5
        self.it = "bullet"
        self.color = "#000000"
        self.outline = "#aaaaaa"
        self.sender = sender
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.birth_date = time.time()

    def act(self):
        Entity.act(self)
        entities = list(self.game.entities)
        if time.time() - self.birth_date > 5:
            self.delete()
        for entity in entities:
            if self.colliding_with(entity):
                if type(entity) == Wall or type(entity) == Tree:
                    self.delete()


class Enemy(Entity):
    def __init__(self, game, x, y, name):
        Entity.__init__(self, game, x, y)
        self.name = name
        self.radius = 20
        self.hp = 100
        self.last_fired = time.time()
        self.it = "enemy"
        self.color = "#eeeeee"
        self.direction = 0
        self.score = 0
        self.dead = False
        self.outline = "#777777"
        self.target = None  # The player the Enemy is currently attacking
        self.last_fired = time.time()
        self.last_hitter = None
        self.last_targeted = time.time()

    def find_nearest_player(self):  # Find the nearest player
        nearest_player = None
        for entity in self.game.entities:
            if entity.it == "player" or entity.it == "enemy":
                if nearest_player:
                    if self.distance_to(entity) > self.distance_to(nearest_player):
                        nearest_player = entity
                else:
                    nearest_player = entity
        return nearest_player

    def fire_bullet(self, direction):
        if self.dead:
            return
        vx = math.cos(math.radians(direction))
        vy = math.sin(math.radians(direction))
        if (time.time() - self.last_fired > 0.4):
            Bullet(self.game, self.x, self.y, self, vx*25, vy*25)
            self.last_fired = time.time()

    def act(self):
        entities = list(self.game.entities)
        Entity.act(self)
        if time.time() - self.last_targeted > 2:
            self.target = self.find_nearest_player()
        if self.hp <= 0:
            Enemy(self.game, random.randint(-self.game.radius, self.game.radius), random.randint(-self.game.radius, self.game.radius), self.name)
            if self.last_hitter:
                self.last_hitter.hp = 100
                self.last_hitter.score += self.score + 1
            self.delete()
        if self.target:
            if self.target not in self.game.entities:
                self.target = self.find_nearest_player()
            else:
                if time.time() - self.last_fired > 0.4:
                    self.fire_bullet(self.direction)
                delta_x = self.target.x - self.x
                delta_y = self.target.y - self.y
                direction = math.atan2(delta_y, delta_x)
                self.direction = math.degrees(direction)
                self.vel_x = math.cos(direction)*5
                self.vel_y = math.sin(direction)*5
        else:
            self.target = self.find_nearest_player()
        for entity in entities:
            if self.colliding_with(entity):
                if type(entity) == Bullet:
                    if entity.sender != self:
                        self.hp -= 10
                        self.last_hitter = entity.sender
                        entity.delete()
                if type(entity) == Wall or type(entity) == Tree:
                    if entity.y > self.y and self.vel_y > 0:
                        self.vel_y = -self.vel_y
                    if entity.y < self.y and self.vel_y < 0:
                        self.vel_y = -self.vel_y# - self.vel_y
                    if entity.x > self.x and self.vel_x > 0:
                        self.vel_x = -self.vel_x# - self.vel_x
                    if entity.x < self.x and self.vel_x < 0:
                        self.vel_x = -self.vel_x


    def jsonify(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "it": self.it,
            "color": self.color,
            "vel_x": self.vel_x,
            "vel_y": self.vel_y,
            "last_updated": self.last_updated,
            "outline": self.outline,
            "hp": self.hp,
            "direction": self.direction,
            "dead": self.dead,
            "name": self.name,
            "score": self.score
        }


class Player(Entity):
    def __init__(self, game, x, y, name):
        Entity.__init__(self, game, x, y)
        self.name = name
        self.radius = 20
        self.score = 0
        self.view = list()
        self.it = "player"
        self.color = "#eeeeee"
        self.outline = "#777777"
        self.ping = time.time()
        self.hp = 100
        self.velocity_queue = [0, 0]
        self.last_fired = time.time()
        self.dead = False
        self.dying_timer = time.time()
        self.direction = 0
        self.mapped_view = dict()
        self.last_hitter = None

    def set_velocity(self, vel_x, vel_y):
        if self.dead:
            return
        self.velocity_queue[0] = vel_x
        self.velocity_queue[1] = vel_y
        if self.x > self.game.radius and self.vel_x > 0:
            self.velocity_queue[0] = -self.velocity_queue[0]
        if self.y > self.game.radius and self.vel_y > 0:
            self.velocity_queue[1] = -self.velocity_queue[1]
        if self.x < -self.game.radius and self.vel_x < 0:
            self.velocity_queue[0] = -self.velocity_queue[0]
        if self.y < -self.game.radius and self.vel_y < 0:
            self.velocity_queue[1] = -self.velocity_queue[1]

    def fire_bullet(self, direction):
        if self.dead:
            return
        vx = math.cos(math.radians(direction))
        vy = math.sin(math.radians(direction))
        if (time.time() - self.last_fired > 0.2):
            Bullet(self.game, self.x, self.y, self, vx*25, vy*25)
            self.last_fired = time.time()

    def handle_collisions(self):
        self.new_view = list()
        new_mapped_view = {
            "wall": list(),
            "player": list(),
            "entity": list(),
            "bullet": list(),
            "tree": list(),
            "coin": list(),
            "enemy": list()
        }
        velocity_queue = self.velocity_queue
        for entity in list(self.game.entities):
            if abs(self.x-entity.x) < 300+entity.radius and abs(self.y-entity.y) < 300+entity.radius:
                self.new_view.append(entity.jsonify())
                new_mapped_view[entity.it].append(entity.jsonify())
            elif type(entity) == Tree and abs(self.x-entity.x) < 300+entity.radius*5 and abs(self.y-entity.y) < 300+entity.radius*5:
                self.new_view.append(entity.jsonify())
                new_mapped_view[entity.it].append(entity.jsonify())
            if self.colliding_with(entity):
                if type(entity) == Coin:
                    self.score += entity.value
                    entity.delete()
                if type(entity) == Wall or type(entity) == Tree:
                    if entity.y > self.y and velocity_queue[1] > 0:
                        velocity_queue[1] = -velocity_queue[1]
                    if entity.y < self.y and velocity_queue[1] < 0:
                        velocity_queue[1] = -velocity_queue[1]# - self.vel_y
                    if entity.x > self.x and velocity_queue[0] > 0:
                        velocity_queue[0] = -velocity_queue[0]# - self.vel_x
                    if entity.x < self.x and velocity_queue[0] < 0:
                        velocity_queue[0] = -velocity_queue[0]# - self.vel_x
                if type(entity) == Bullet:
                    if entity.sender != self:
                        self.hp -= 10;
                        entity.delete();


        self.view = self.new_view
        self.mapped_view = new_mapped_view
        if not self.dead:
            self.vel_x = velocity_queue[0]
            self.vel_y = velocity_queue[1]

    def act(self):
        ## Hardcoding game wall mechanic
        if self.x > self.game.radius:
            self.x = self.game.radius
        if self.y > self.game.radius:
            self.y = self.game.radius
        if self.x < -self.game.radius:
            self.x = -self.game.radius
        if self.y < -self.game.radius:
            self.y = -self.game.radius
        if time.time() - self.ping >= 3:
            print("Eteria: Game: Player "+self.name+" has disconnected")
            self.delete()
        if self.hp <= 0:
            self.dead = True
            self.dying_timer = time.time()
            if self.last_hitter:
                self.last_hitter.hp = 100
                self.last_hitter.score += self.score + 1
            self.vel_x = 0
            self.vel_y = 0
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
            "vel_y": self.vel_y,
            "dead": self.dead,
            "direction": self.direction,
            "last_updated": self.last_updated,
            "outline": self.outline
        }
