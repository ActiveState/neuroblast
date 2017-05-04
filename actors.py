from __future__ import division
import pygame
import math
from utils import *
from random import randrange

# Global Init stuff should have a proper home once not placeholder art
spritesheet = pygame.image.load("spaceship_sprite_package_by_kryptid.png")
spritesheet.set_colorkey(spritesheet.get_at((0, 0)))

class SpriteSequence(object):
    def __init__(self,name,sheet,rect,cols, rows, padding,interval, loop, cb):
        self.name = name
        self.sheet = sheet
        self.rect = rect
        self.cols = cols
        self.rows = rows
        self.padding = padding
        self.interval = interval
        self.loop = loop
        self.currentcol = 0
        self.currentrow = 0
        self.playing = False
        self.counter = 0
        self.cb = cb
    def play(self):
        self.counter = 0
        self.currentcol = 0
        self.currentrow = 0
        self.playing = True

    def stop(self):
        self.counter = 0
        self.currentcol = 0
        self.currentrow = 0
        self.playing = False
        
    def update(self, surface, pos, dt):
        if self.playing:
            self.counter += dt
            if self.counter>=self.interval:
                self.counter = 0
                self.currentcol += 1
                if self.currentcol >= self.cols:
                    self.currentcol = 0
                    self.currentrow += 1
                    if self.currentrow >= self.rows:
                        if self.loop:
                            self.currentcol=0
                            self.currentrow=0
                        else:
                            if (self.cb):
                                self.cb(self.name)
                            self.playing=False
            
            if self.playing:
                print pos
                surface.blit(self.sheet,pos,(self.rect.x+self.currentcol*self.rect.w+self.currentcol*self.padding,
                                        self.rect.y+self.currentrow*self.rect.h+self.currentrow*self.padding,
                                        self.rect.w,self.rect.h))
                                        
        
        


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
        self.blinkcycles = 6
        self.blinks = 0
        self.blinkcount = 0
        self.blinkon = False
        self.deadcb = None
        self.anim = None
        self.animoffset = (0,0)
        
        
    def TakeDamage(self, damage):
        #Take damage fuc tion
        # Already dead!
        if self.health<=0:
            return
        
        self.health -= damage
        if self.health <= 0:
            self.lives -= 1
            if self.deadcb:
                self.deadcb()
            if (self.lives>=0):
                # DO something
                # Trigger Particle or something
                self.blinking = True
                self.blinks = 0
    def Die(self):
        self.kill()

class Enemy(Killable):
    def __init__(self, bulletgroup):
        super(Enemy, self).__init__()
        # Enemy specific stuff here
        self.x = 320
        self.xbase = randrange(200,400)
        self.y = -50
        self.velx = 0
        self.vely = 16       # wish there was a vector class
        self.bullets = bulletgroup
        self.image = pygame.Surface((94,100))
        self.rect = self.image.get_rect()
        self.cooldown = 0.1
        self.canfire = True
        self.bulcount = 0
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((380,0,94,100))
        global spritesheet
        self.image.blit(spritesheet,(0,0),ssrect)
        self.image.convert()
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect.center = (self.x, self.y)
        self.spawntime = pygame.time.get_ticks()
        self.deadcb = self.amdead
        self.hitAnim = SpriteSequence("hit",spritesheet,pygame.Rect(96,765,31,31),4,2,1,0.1,False,None)
        self.blowAnim = SpriteSequence("blow",spritesheet,pygame.Rect(0,202,94,100),4,2,1,0.1,False,self.onAnimComplete)
 
    def onAnimComplete(self,name):
        if name == "blow":
            print "BLOW ANIM COMPLETE, DYING"
            self.Die()
 
    def amdead(self):
        print self
        print "ENEMY POS: "+str(self.x)+","+str(self.y)
        print "OFFSET" + str(self.animoffset)
        self.playanim("blow",(self.x-47,self.y-50))
 
      
    def playanim(self,name,offset):
        if self.anim != self.blowAnim and name=="hit":
            print "HIT ANIM"
            self.anim = self.hitAnim
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()
        if self.anim != self.blowAnim and name=="blow":
            print "BLOW ANIM"
            self.anim = self.blowAnim            
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()
          
        
    def update(self, screen, event_queue, dt, (player_x,player_y),(player_velx,player_vely)):
        if not self.alive():
            return
            
        self.velx = math.sin((pygame.time.get_ticks()-self.spawntime)/1800) * 40
            
        self.x = self.xbase + self.velx # velx is already time based so doesn't need deltatime

        self.y += self.vely * dt

        self.rect.center = (self.x, self.y)
        
        if not(self.canfire):
            self.bulcount += dt
            if self.bulcount>self.cooldown:
                self.canfire = True
                self.bulcount = 0

        # x is param that is the player's x position
        if math.fabs(self.x-player_x) < 5 and self.canfire:
            bul = Bullet(self.x,self.y+50,RED,(0,1),160,self.bullets)
            self.canfire = False


class Player(Killable):
    def __init__(self,bulletgroup):
        super(Player, self).__init__()
        # Player specifc init stuff here
        self.x = 320
        self.y = 500
        self.velx = 0
        self.vely = 0       # wish there was a vector class
        self.deadcb = self.amdead
        self.bullets = bulletgroup
        self.image = pygame.Surface((94,100))
        self.rect = self.image.get_rect()
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((0,0,94,100))
        global spritesheet
        self.image.blit(spritesheet,(0,0),ssrect)
        self.image.convert()
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.hitAnim = SpriteSequence("hit",spritesheet,pygame.Rect(96,765,31,31),4,2,1,0.1,False,None)
        self.blowAnim = SpriteSequence("blow",spritesheet,pygame.Rect(0,202,94,100),4,2,1,0.1,False,self.onAnimComplete)
 
    def onAnimComplete(self,name):
        if name == "blow":
            print "BLOW ANIM COMPLETE, DYING"
            if self.lives<0:
                self.Die()
 
    
    def amdead(self):
        print str(self.x)+","+str(self.y)
        self.playanim("blow",(self.x-47,self.y-50))
    
    def playanim(self,name,offset):
        if self.anim != self.blowAnim and name=="hit":
            print "HIT ANIM"
            self.anim = self.hitAnim
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()
        if self.anim != self.blowAnim and name=="blow":
            print "BLOW ANIM"
            self.anim = self.blowAnim            
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()


 
    def update(self, screen, event_queue, dt):
        
        self.rect.center = (self.x, self.y)

        if self.blinking:
            self.blinkcount += dt

            if self.blinkcount >= self.blinktime:
                #print "TOGGLE BLINK"
                self.blinkon =  not self.blinkon
                self.blinkcount = 0
                self.blinks +=1
                if (self.blinks == self.blinkcycles):
                    self.blinking = False
                    self.health = 100      

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
            
        if self.x+(self.velx*dt)>640-47 or self.x+(self.velx*dt)<47:
            self.velx = 0
        if self.y+(self.vely*dt)>720-50 or self.y+(self.vely*dt)<50:
            self.vely = 0
            
            
        self.x += self.velx * dt
        self.y += self.vely * dt
