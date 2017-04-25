from __future__ import division
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

    def update(self, dt):
        (x, y) = self.rect.center
        y += self.direction[1] * self.speed * dt
        x += self.direction[0] * self.speed * dt
        self.rect.center = (x, y)
        # TODO make the bounds constants or dynamic
        if y <= 0 or y >= 720 or x <= 0 or x >= 1280:
            self.kill()

class Killable(pygame.sprite.Sprite):
    def __init__(self):
        super(Killable, self).__init__()
        self.lives = 0
        self.health = 100
        self.blinking = False
        self.blinktime = 0.5
        self.blinkcount = 0
        self.blinkon = False
    def TakeDamage(self, damage):
        #Take damage fuc tion
        self.health -= damage
        if self.health <= 0:
            self.lives -= 1
            if (self.lives<0):
                # DEAD
                self.Die()
            else:
                # DO something
                # Trigger Particle or something
                self.blinking = True
    def Die(self):
        #print "DEAD"
        self.kill()

class Enemy(Killable):
    def __init__(self, bulletgroup):
        super(Enemy, self).__init__()
        # Enemy specific stuff here
        self.x = 320
        self.y = 0
        self.velx = 0
        self.vely = 16       # wish there was a vector class
        self.bullets = bulletgroup
        self.image = pygame.Surface((94,100))
        self.rect = self.image.get_rect()
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((380,0,94,100))
        global spritesheet
        self.image.blit(spritesheet,(0,0),ssrect)
        self.image.convert()
        self.image.set_colorkey(self.image.get_at((0, 0)))
        
    def update(self, screen, event_queue, dt, (x,y)):
        if not self.alive():
            return
            
        self.x = 300+(math.sin(self.y/45) * 80)

        self.y += self.vely * dt

        self.rect.center = (self.x, self.y)

        # x is param that is the player's x position
        if math.fabs(self.x-x) < 5:
            bul = Bullet(self.x,self.y+50,RED,(0,1),160,self.bullets)


class Player(Killable):
    def __init__(self,bulletgroup):
        super(Player, self).__init__()
        # Plauer specifc init stuff here
        self.lives = 3
        self.x = 320
        self.y = 500
        self.velx = 0
        self.vely = 0       # wish there was a vector class
        self.bullets = bulletgroup
        self.image = pygame.Surface((94,100))
        self.rect = self.image.get_rect()
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((0,0,94,100))
        global spritesheet
        self.image.blit(spritesheet,(0,0),ssrect)
        self.image.convert()
        self.image.set_colorkey(self.image.get_at((0, 0)))
 
    def update(self, screen, event_queue, dt):

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
            bul = Bullet(self.x,self.y-50,BLUE,(0,-1),320,self.bullets)

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

        self.x += self.velx * dt
        self.y += self.vely * dt
