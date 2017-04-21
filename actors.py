import pygame
import math
from utils import *

# Global Init stuff should have a proper home once not placeholder art
spritesheet = pygame.image.load("spaceship_sprite_package_by_kryptid.png")
spritesheet.set_colorkey(spritesheet.get_at((0, 0)))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, direction, speed, container):
        pygame.sprite.Sprite.__init__(self, container)
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA, 32)
        self.image = self.image.convert_alpha()
        self.col = list(color)
        for i in range(5, 0, -1):
            self.col[0] = color[0] * float(i) / 5
            self.col[1] = color[1] * float(i) / 5
            self.col[2] = color[2] * float(i) / 5
            pygame.draw.circle(self.image, tuple(self.col), (5, 5), i,
                               0)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = speed

    def update(self):
        (x, y) = self.rect.center
        y += self.direction[1] * self.speed
        x += self.direction[0] * self.speed
        self.rect.center = (x, y)
        # TODO make the bounds constants or dynamic
        if y <= 0 or y >= 720 or x <= 0 or x >= 1280:
            self.kill()

class Killable(pygame.sprite.Sprite):
    def __init__(self):
        super(Killable, self).__init__()
        self.health = 100
    def TakeDamage(self, damage):
        #Take damage fuc tion
        self.health -= damage
        if self.health <= 0:
            # DEAD
            self.Die()
    def Die(self):
        # DO something
        # Trigger Particle or something
        #print "DEAD"
        self.kill()

class Enemy(Killable):
    def __init__(self):
        super(Enemy, self).__init__()
        # Enemy specific stuff here
        self.BulletLayer = 1
        self.x = 640
        self.y = 0
        self.velx = 0
        self.vely = 1       # wish there was a vector class
        self.bullets = pygame.sprite.Group()
        self.rect = pygame.Rect((0, 0, 94, 100))
    def update(self, screen, event_queue, dt, (x,y)):
        if not self.alive():
            return

        global spritesheet

        self.x = 600+math.sin(self.y/45) * 80

        self.y += self.vely

        rect = pygame.Rect((380, 0, 94, 100))
        screen.blit(spritesheet, (self.x, self.y), rect)

        self.rect.center = (self.x, self.y)

        if math.fabs(self.x-x) < 5:
            bul = Bullet(self.x,self.y,RED,(0,1),10,self.bullets)

        self.bullets.update()
        self.bullets.draw(screen)


class Player(Killable):
    def __init__(self):
        super(Player, self).__init__()
        # Plauer specifc init stuff here
        self.BulletLayer = 2
        self.x = 500
        self.y = 500
        self.velx = 0
        self.vely = 0       # wish there was a vector class
        self.bullets = pygame.sprite.Group()
        self.rect = pygame.Rect((0, 0, 94, 100))

    def update(self, screen, event_queue, dt):
        global spritesheet

        rect = pygame.Rect((0, 0, 94, 100))
        screen.blit(spritesheet, (self.x, self.y), rect)

        self.bullets.update()
        self.bullets.draw(screen)
        self.rect.center = (self.x, self.y)

        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.velx = -SHIP_ACC
        if keys[pygame.K_RIGHT]:
            self.velx = SHIP_ACC
        if keys[pygame.K_UP]:
            self.vely = -SHIP_ACC
        if keys[pygame.K_DOWN]:
            self.vely = SHIP_ACC
        if keys[pygame.K_SPACE]:
            bul = Bullet(self.x,self.y,BLUE,(0,-1),20,self.bullets)

        '''        # Cap speed
        if self.velx > SHIP_MAX:
            self.velx = SHIP_MAX
        elif self.velx<-SHIP_MAX:
            self.velx = -SHIP_MAX
        if self.vely > SHIP_MAX:
            self.vely = SHIP_MAX
        elif self.vely<-SHIP_MAX:
            self.vely = -SHIP_MAX

        # Decelerate
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]) and self.velx != 0:
            sign = 1
            if (self.velx<0):
                sign = -1
            self.velx -= SHIP_ACC * 2 * sign
            if (sign==1 and self.velx<0):
                self.velx = 0
            elif (sign==-1 and self.velx>0):
                self.velx = 0

        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]) and self.vely != 0:
            sign = 1
            if (self.vely<0):
                sign = -1
            self.vely -= SHIP_ACC * 2 * sign
            if (sign==1 and self.vely<0):
                self.vely = 0
            elif (sign==-1 and self.vely>0):
                self.vely = 0
            
        '''
        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN]):
            self.vely = 0
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.velx = 0

        self.x += self.velx
        self.y += self.vely
