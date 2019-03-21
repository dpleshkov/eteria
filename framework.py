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
        self.running_time = round((t2-t1)*1000)
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
        self.x += self.vel_x * (self.game.running_time/40)
        self.y += self.vel_y * (self.game.running_time/40)

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


class Bullet(Entity):
    def __init__(self, game, x, y, sender, vel_x, vel_y):
        Entity.__init__(self, game, x, y)
        self.radius = 5
        self.it = "bullet"
        self.color = "#ff0000"
        self.sender = sender
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.birth_date = time.time()

    def act(self):
        Entity.act(self);
        if time.time() - self.birth_date > 5:
            self.delete()


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
        self.velocity_queue = [0, 0]
        self.last_fired = time.time()
        self.dead = False
        self.dying_timer = time.time()
        self.direction = 0

    def set_velocity(self, vel_x, vel_y):
        if self.dead:
            return
        self.velocity_queue[0] = vel_x
        self.velocity_queue[1] = vel_y
        if self.x > 2000 and self.vel_x > 0:
            self.velocity_queue[0] = -self.velocity_queue[0]
        if self.y > 2000 and self.vel_y > 0:
            self.velocity_queue[1] = -self.velocity_queue[1]
        if self.x < -2000 and self.vel_x < 0:
            self.velocity_queue[0] = -self.velocity_queue[0]
        if self.y < -2000 and self.vel_y < 0:
            self.velocity_queue[1] = -self.velocity_queue[1]

    def fire_bullet(self, direction):
        if self.dead:
            return
        vx = math.cos(math.radians(direction))
        vy = math.sin(math.radians(direction))
        if (time.time() - self.last_fired > 0.5):
            Bullet(self.game, self.x, self.y, self, vx*25, vy*25)
            self.last_fired = time.time()

    def handle_collisions(self):
        self.new_view = list()
        velocity_queue = self.velocity_queue
        for entity in list(self.game.entities):
            if abs(self.x-entity.x) < 300+entity.radius and abs(self.y-entity.y) < 300+entity.radius:
                self.new_view.append(entity.jsonify())
            if self.colliding_with(entity):
                if type(entity) == Coin:
                    self.score += entity.value
                    entity.delete()
                if type(entity) == Wall:
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
        if not self.dead:
            self.vel_x = velocity_queue[0]
            self.vel_y = velocity_queue[1]

    def act(self):
        if time.time() - self.ping >= 3:
            print("Player "+self.name+" has disconnected")
            self.delete()
        if self.hp <= 0:
            self.dead = True
            self.dying_timer = time.time()
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
            "direction": self.direction
        }
