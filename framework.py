import time


class Game:
    def __init__(self):
        self.entities = set()

    def update(self):
        for entity in list(self.entities):
            entity.act()

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
        self.color = "#000000"

    def delete(self):
        self.game.remove_entity(self)
        del self

    def act(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def jsonify(self):
        return {
            "x": self.x,
            "y": self.y,
            "radius": self.radius,
            "it": self.it,
            "color": self.color
        }


class Coin(Entity):
    def __init__(self, game, x, y, value):
        Entity.__init__(self, game, x, y)
        self.value = value
        self.radius = 10
        self.it = "coin"
        self.color = "#ffff00"


class Player(Entity):
    def __init__(self, game, x, y, name):
        Entity.__init__(self, game, x, y)
        self.name = name
        self.radius = 20
        self.score = 0
        self.view = list()
        self.it = "player"
        self.ping = time.time()

    def set_velocity(self, vel_x, vel_y):
        self.vel_x = vel_x
        self.vel_y = vel_y

    def handle_collisions(self):
        self.view = list()
        for entity in list(self.game.entities):
            if abs(self.x-entity.x) < 300 and abs(self.y-entity.y) < 300:
                self.view.append(entity.jsonify())
            e_pos = [entity.x-entity.radius, entity.y-entity.radius, entity.x+entity.radius, entity.y+entity.radius]
            m_pos = [self.x-self.radius, self.y-self.radius, self.x+self.radius, self.y+self.radius]
            if m_pos[0] < e_pos[2] and m_pos[2] > e_pos[0]:
                if m_pos[1] < e_pos[3] and m_pos[3] > e_pos[1]:
                    if type(entity) == Coin:
                        self.score += entity.value
                        entity.delete()

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
            "score": self.score
        }
