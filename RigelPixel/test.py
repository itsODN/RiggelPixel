import pygame
from pygame.locals import *
from pygame.math import Vector2
from math import tan, radians, degrees, copysign

class MainGame:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.myfont = pygame.font.SysFont("Comic Sans MS",30)
        self.width, self.height = 1280, 1024
        self.FPS = 60

        self.objects = list()
        self.clock = pygame.time.Clock()
        self.event_handler = EventHandler(self)
        self.collision_handler = CollisionHandler(self)
        self.level = Level(self)
        self.dt = 0

        
        self.screen = pygame.display.set_mode((self.height, self.width))

        self.running = True
    
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print("[ERROR]: {} {} {}\n Closing application".format(type, value, traceback))
        pygame.quit()

    def main_loop(self):
        
        while self.running:
            self.event_handler.update()

            for obj in self.objects: 
                obj.update()

            

                
            self.screen.fill((120, 120, 120))

            self.level.render()
            for obj in self.objects:
                obj.render()

            pygame.display.flip()
            self.dt = self.clock.tick(self.FPS)
            

    def quit(self):
        pygame.quit()

class EventHandler:
    def __init__(self, master):
        self.master = master

        self.subscriptions = dict() 
        self.sub_events = list()

    def update(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.master.running = False
            else:
                for key in self.sub_events:
                    self.subscriptions[key].events[key] = bool(pygame.key.get_pressed()[ord(key)])
                
                

    def subscribe(self, sub, event):
        self.subscriptions[event] = sub
        self.sub_events = list(self.subscriptions.keys())

class CollisionHandler:
    def __init__(self, master):
        self.master = master
        self.objects = list()

    def subscribe(self, obj):
        self.objects.append(obj)

    def check(self, obj):
        out_list = list()
        test_obj = self.objects.pop(self.objects.index(obj))
        col_indices = test_obj.rect.collidelistall(self.objects)
        for i in col_indices:
            if i < 0:
                continue
            col_obj = self.objects[i].rect
            out_list.append(col_obj)

        self.objects.append(test_obj)

        return out_list
    
    def collision_direction(self, test_obj, col_obj): 
        ax, ay = test_obj.center
        bx, by = col_obj.center
        l = bx - ax
        h = by - ay
        m = h/l
        return l, h
    

class Level:
    def __init__(self, master):
        self.master = master
        self.walls = list()
        self.w, self.h = 64,64

        self.setup()
        self.parse_level(self.level1)

    def setup(self):
        self.level1 = [
        "WWWWWWWWWWWWWWWWWWWW",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W         W        W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "W                  W",
        "WWWWWWWWWWWWWWWWWWWW"
        ]

    def parse_level(self, level):
        for i, row in enumerate(level):
            for j, col in enumerate(row):
                if col == "W":
                    self.walls.append(Wall(self, (i*self.w, j*self.h)))
    
    def render(self):
        for el in self.walls: 
            pygame.draw.rect(self.master.screen, el.color, el.rect)


class Wall:
    def __init__(self, level, pos):
        self.level = level
        self.w, self.h = level.w, level.h
        self.rect = pygame.Rect(pos[0],pos[1],self.w, self.h)
        self.color = 0,0,0

        self.level.master.collision_handler.subscribe(self)



class GameObject:
    def __init__(self, master):
        self.master = master
        self.master.objects.append(self)
        self.events = dict() 

    def subscribe_event(self, event):
        """
        Get the status of the key [event] from the event handler. [event] can be a single string or a list of strings.
        """
        if type(event) is str:
            self.master.event_handler.subscribe(self, event)
            self.events[event]=None
        else:
            for el in event:
                self.subscribe_event(el)

    def subscribe_collision(self):
        self.master.collision_handler.subscribe(self) 

    def check_collision(self):
        return self.master.collision_handler.check(self)

    def update(self):
        return 0 

class Ball(GameObject):
    def __init__(self, master):
        super().__init__(master)
        
        self.position = 100,200
        self.color    = 255,0,0
        self.radius   = 20
        self.speed    = 0.5
        self.acceleration = 0.001
        self.vx0      = 0
        self.vy0      = 0

        self.speed_x = 0
        self.speed_y = 0
        self.dx      = 0
        self.dy      = 0

        self.subscribe_event(["w", "a", "s", "d"])
        self.subscribe_collision()

        self.rect = pygame.Rect(self.position[0]-self.radius,self.position[1]-self.radius,self.radius*2,self.radius*2)

    def update(self):
        self.get_dt()
        dv = self.get_dv2()
        self.move(dv)

        self.textsurf = self.master.myfont.render(str(dv), False, (0,255,0))

    def render(self):
        pygame.draw.circle(self.master.screen, self.color, self.rect.center, self.radius)
        self.master.screen.blit(self.textsurf, (0,0))

    def get_dt(self): 
        self.dt = self.master.dt

    def get_dv(self):
        dx, dy = 0, 0
        if self.events["w"]:
            dy -= self.speed * self.master.dt
        if self.events["s"]:
            dy += self.speed * self.master.dt
        if self.events["a"]:
            dx -= self.speed * self.master.dt
        if self.events["d"]:
            dx += self.speed * self.master.dt

        return dx, dy

    def get_r(self):
        rx = 0.5 * self.a * self.dt**2 + self.v0 * self.dt * self.rect.centerx

    def get_dv2(self):
        dx, dy = 0, 0
        if self.events["w"]:
            self.speed_y -= self.acceleration * self.master.dt
        if self.events["s"]:
            self.speed_y += self.acceleration * self.master.dt
        if self.events["a"]:
            self.speed_x -= self.acceleration * self.master.dt
        if self.events["d"]:
            self.speed_x += self.acceleration * self.master.dt


        self.dx += self.speed_x
        self.dy += self.speed_y
        return self.dx, self.dy

    def move(self, dv):
        dx, dy = dv
        x, y = self.rect.center

        self.rect.x += dx

        collision = self.check_collision()
        if collision:
            if dx > 0: #moving right, hit the left side of the wall
                self.rect.right = collision[0].left
            if dx < 0: #moving left, hit the right side of the wall
                self.rect.left = collision[0].right

        self.rect.y += dy
        collision = self.check_collision()
        if collision:
            if dy > 0: #moving down, hit top of the wall
                self.rect.bottom = collision[0].top
            if dy < 0: #moving up, hit bottom of wall
                self.rect.top = collision[0].bottom

class Car(GameObject):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.position = Vector2(800,800)
        self.velocity = Vector2(0.0, 0.0)
        self.angle    = 0.0
        self.length   = 4
        self.max_acceleration =0.5 
        self.max_steering = 30

        self.acceleration = 0.0
        self.steering = 0.0

        self.color = (200,0,0)
        self.width = 2

        self.subscribe_event(["w","a","s","d"])
    
    def update(self):
        dt = self.master.dt
        self.move(dt)

    def move(self, dt):
        if self.events["w"]:
            self.acceleration += 1 * dt
        elif self.events["s"]:
            self.acceleration -= 1 * dt
        else:
            self.acceleration = 0

        self.accelerations = max(-self.max_acceleration, min(self.acceleration, self.max_acceleration))

        if self.events["a"]:
            self.steering += 30 * dt
        elif self.events["d"]:
            self.steering -= 30 * dt
        else:
            self.steering = 0
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))



        self.velocity += (self.acceleration * dt, 0)
        
        if tan(radians(self.steering)) != 0:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius

        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt

        self.rect = pygame.Rect(self.position[0], self.position[1], 10,10)

    def render(self):
        pygame.draw.rect(self.master.screen, self.color, self.rect)



if __name__ == "__main__":
    with MainGame() as game:
        car = Car(game)
        game.main_loop()
