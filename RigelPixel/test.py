import pygame
from pygame.locals import *
from pygame.math import Vector2
from math import sin, radians, degrees, copysign, sqrt

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
                obj.update(self.dt)

            

                
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

class Boat(GameObject):
    def __init__(self, master):
        super().__init__(master)
        self.position = pygame.Vector2(100,100)
        self.color = 0,0,200
        self.dimension = 20,20

        self.velocity = 50
        self.accel_t  = 0
        self.accelerating = False

        self.subscribe_event(["w","a","s","d"])

    def update(self, dt):
        self.move(dt)

    def render(self):
        x = int(self.position[0])
        y = int(self.position[1])
        pygame.draw.circle(self.master.screen, (255,0,0), (x,y), 20)

    def move(self, dt):
        dt = dt / 1000
        x,y = 0,0

        if self.events["w"]:
            y -= 1
        if self.events["s"]:
            y += 1
        if self.events["a"]:
            x -= 1
        if self.events["d"]:
            x += 1

        self.direction = pygame.Vector2(x,y)

        if True in self.events.values():
            self.accelerating = True
        else:
            self.accelerating = False

        self.accelerate(dt)



        print(self.accelerating, self.velocity)
        new_pos = pygame.Vector2(self.velocity * self.direction * dt)
        self.position += new_pos

    def accelerate(self,dt):
        dt = dt
        if self.accelerating:
            self.accel_t += 100*dt
        else:
            self.accel_t -= 250*dt

        if self.accel_t > 250:
            self.accel_t = 250
        elif self.accel_t < 0:
            self.accel_t = 0
        
        self.velocity = 2 * self.accel_t


        

class Ball2(GameObject):
    def __init__(self, master):
        super().__init__(master)

        self.position = 100,200
        self.color = 0,0,200
        self.radius = 20
        
        self.current_speed = 20
        self.max_speed = 50
        self.acceleration = 2
        self.deacceleration = 2
        self.velocity = 10

        self.board_angles = (0,0)
        self.max_angle = 45
        self.direction = pygame.Vector2(0,0)

        self.subscribe_event(["w","a","s","d"])
        self.subscribe_collision()

    def move(self, dt):
        x, y = self.board_angles
        if self.events["w"]:
            y -= 0.1 * dt
        if self.events["s"]:
            y += 0.1 * dt
        if self.events["a"]:
            x -= 0.1 * dt
        if self.events["d"]:
            x += 0.1 * dt

        if x > self.max_angle:
            x = self.max_angle 
        elif x < self.max_angle * -1:
            x = self.max_angle * -1
        if y > self.max_angle:
            y = self.max_angle
        elif y < self.max_angle * -1:
            y = self.max_angle * -1
        
        self.board_angles = x, y

        if x == 0 and y == 0:
            self.direction = pygame.Vector2(0,0)
        else: 
            self.direction = pygame.Vector2(x,y)
            
            self.direction.scale_to_length(40)
            self.direction = pygame.Vector2(self.direction[0]+self.position[0], self.direction[1]+self.position[1])
    
    def get_translation(self, dt):
        

        dx = 0.5 * self.acceleration * dt**2 + sqrt(2*self.acceleration * sin(radians(self.board_angles[0]))*self.position[0]*dt) + self.position[0]

        dy = 0.5 * self.acceleration * dt**2 + sqrt(2*self.acceleration * sin(radians(self.board_angles[1]))*self.position[1]*dt) + self.position[1]

        return dx, dy

    def update(self, dt):
        self.move(dt)
        dx, dy = self.get_translation(dt)
        self.new_position = self.position[0]+dx, self.position[1]+dy
        self.text_surf = self.master.myfont.render("{} {}".format(self.board_angles, self.direction), False, (0,255,0))

    
    def render(self):
        pygame.draw.circle(self.master.screen, self.color, self.position, self.radius)
        pygame.draw.line(self.master.screen, (255,0,0), self.position, self.direction, 2)
        pygame.draw.line(self.master.screen, (255,255,0), self.position, self.new_position, 2)
        self.master.screen.blit(self.text_surf, (0,0))

        

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
        dv = self.get_dv()
        self.move(dv)

        self.textsurf = self.master.myfont.render(str(self.dt), False, (0,255,0))

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
        self.max_acceleration =5 
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
        boat = Boat(game)
        game.main_loop()
