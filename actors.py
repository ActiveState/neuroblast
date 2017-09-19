'''The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.

Written by Pete Garcin @rawktron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.'''

from __future__ import division
import pygame
import math
from utils import *
from random import randrange
import numpy as np


# TODO Make a proper audio management class
pygame.mixer.init()
shootsfx = pygame.mixer.Sound('audio/HeroLaser.wav')
hitsfx = pygame.mixer.Sound('audio/EnemyHit.wav')
enemyshootsfx = pygame.mixer.Sound('audio/EnemyShoot.wav')
explodesfx = pygame.mixer.Sound('audio/ShipExplode.wav')
respawnsfx = pygame.mixer.Sound('audio/Respawn.wav')

spritesheet = pygame.image.load("art/python-sprites.png")

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
                surface.blit(self.sheet,pos,(self.rect.x+self.currentcol*self.rect.w+self.currentcol*self.padding,
                                        self.rect.y+self.currentrow*self.rect.h+self.currentrow*self.padding,
                                        self.rect.w,self.rect.h))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, color, direction, speed, container, brain = None):
        pygame.sprite.Sprite.__init__(self, container)

        self.image = pygame.Surface((16,16), flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        basex = 423
        if color==RED:
            basex += 96
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((basex,710,16,16))
        global spritesheet
        self.image.blit(spritesheet,(0,0),ssrect)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = speed
        self.brain = brain

    def update(self, dt):
        (x, y) = self.rect.center
        y += self.direction[1] * self.speed * dt
        x += self.direction[0] * self.speed * dt
        self.rect.center = (x, y)
        # TODO make the bounds constants or dynamic
        if y <= 0 or y >= 720 or x <= 0 or x >= 640:
            if self.brain:
                self.brain.record_miss(self)
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
                self.health = 100 


    def Die(self):
        self.kill()

class Enemy(Killable):
    def __init__(self, bulletgroup, brain, speed):
        super(Enemy, self).__init__()
        # Enemy specific stuff here
        self.x = randrange(0,450)
        self.y = -50
        self.velx = 0
        self.vely = speed       # wish there was a vector class
        self.bullets = bulletgroup
        self.image = pygame.Surface((96,192))
        self.rect = self.image.get_rect()
        self.cooldown = 0.1
        self.canfire = True
        self.bulcount = 0
        self.brain = brain
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((96,192,96,192))
        global spritesheet
        self.image.blit(spritesheet,(0,0),ssrect)
        self.image.convert()
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect.center = (self.x, self.y)
        self.spawntime = pygame.time.get_ticks()
        self.deadcb = self.amdead
        self.idleAnim = SpriteSequence("idle",spritesheet,pygame.Rect(96,192,96,192),7,1,0,0.1,True,None)
        self.hitAnim = SpriteSequence("hit",spritesheet,pygame.Rect(96,480,96,96),8,1,0,0.1,False,None)
        self.blowAnim = SpriteSequence("blow",spritesheet,pygame.Rect(96,384,96,96),8,1,0,0.1,False,self.onAnimComplete)
        self.idleAnim.play()



    def onAnimComplete(self,name):
        if name == "blow":
            self.Die()
 
    def amdead(self):
        self.playanim("blow",(self.x-48,self.y-24))
 
      
    def playanim(self,name,offset):
        if self.anim != self.blowAnim and name=="hit":
            hitsfx.play()
            self.anim = self.hitAnim
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()
        if self.anim != self.blowAnim and name=="blow":
            explodesfx.play()
            self.anim = self.blowAnim            
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()
          
        
    def update(self, screen, event_queue, dt, ppos, pvel, trainingMode, netmodel):
        if not self.alive():
            return
        
        player_x, player_y = ppos
        player_velx, player_vely = pvel
    
        self.velx = math.sin((pygame.time.get_ticks()-self.spawntime)/1800) * 40 
        self.x += self.velx * dt
        self.y += self.vely * dt

        self.rect.center = (self.x, self.y)

        self.image.fill((0,0,0))
        self.idleAnim.update(self.image,(0,0),dt)
        
        if not(self.canfire):
            self.bulcount += dt
            if self.bulcount>self.cooldown:
                self.canfire = True
                self.bulcount = 0

        # Normalized values
        dx = (self.x - player_x) / 640
        dy = (self.y - player_y) / 720
        du = (self.velx - player_velx) / 60
        dv = (self.vely - player_vely) / 60


        self.brain.currentState = np.array([list((dx,dy,du,dv))])
            
        if self.canfire:
             if (trainingMode and randrange(0,100)<10) or ((netmodel == 1 and not trainingMode and self.brain.keras.predict(np.array([list((dx,dy,du,dv))]))>=0.5) or (netmodel == 0 and not trainingMode and self.brain.model.think([dx,dy,du,dv])>=0.5)):
                # Cheat to do parallel visualization, sort of performance intensive
                if (not trainingMode and netmodel == 1):
                    self.brain.model.think([dx,dy,du,dv])
                bul = Bullet(self.x,self.y+96,RED,(0,1),160,self.bullets,self.brain)
                self.brain.add_shot(bul, dx, dy, du, dv)
                self.canfire = False

class Player(Killable):
    def __init__(self,bulletgroup):
        super(Player, self).__init__()
        global spritesheet
        spritesheet.convert_alpha()
        self.cooldown = 0.5
        self.canfire = True
        self.bulcount = 0
        self.x = 320
        self.y = 500
        self.velx = 0
        self.vely = 0       # wish there was a vector class
        self.deadcb = self.amdead
        self.bullets = bulletgroup
        self.image = pygame.Surface((96,96))
        self.rect = self.image.get_rect()
        ## Generate the sprite image from spritesheet
        ssrect = pygame.Rect((96,96,96,96))
        self.image.blit(spritesheet,(0,0),ssrect)
        self.image.convert()
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.hitAnim = SpriteSequence("hit",spritesheet,pygame.Rect(96,480,96,96),8,1,0,0.1,False,None)
        self.blowAnim = SpriteSequence("blow",spritesheet,pygame.Rect(96,384,96,96),8,1,0,0.1,False,self.onAnimComplete)
        self.idleAnim = SpriteSequence("idle",spritesheet,pygame.Rect(96,576,96,192),8,1,0,0.1,True,None)
        self.idleAnim.play()

    def onAnimComplete(self,name):
        if name == "blow":
            respawnsfx.play()
            if self.lives<0:
                self.Die()
 
    
    def amdead(self):
        self.playanim("blow",(self.x-48,self.y-48))
    
    def playanim(self,name,offset):
        if self.anim != self.blowAnim and name=="hit":
            hitsfx.play()
            self.anim = self.hitAnim
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()
        if self.anim != self.blowAnim and name=="blow":
            explodesfx.play()
            self.anim = self.blowAnim            
            self.animoffset = (offset[0]-self.x,offset[1]-self.y)
            self.anim.play()


 
    def update(self, screen, event_queue, dt, joystick):
        
        self.rect.center = (self.x, self.y)

        self.image.fill((0,0,0))
        self.idleAnim.update(self.image,(0,0),dt)

        if self.blinking:
            self.blinkcount += dt

            if self.blinkcount >= self.blinktime:
                self.blinkon =  not self.blinkon
                self.blinkcount = 0
                self.blinks +=1
                if (self.blinks == self.blinkcycles):
                    self.blinking = False

        if not(self.canfire):
            self.bulcount += dt
            if self.bulcount>self.cooldown:
                self.canfire = True
                self.bulcount = 0
     
        keys=pygame.key.get_pressed()

        if keys[pygame.K_LEFT] or (joystick and (joystick.get_axis(0)<-DEADZONE or joystick.get_button(2))):
            self.velx = -SHIP_ACC
        if keys[pygame.K_RIGHT] or (joystick and (joystick.get_axis(0)>DEADZONE or joystick.get_button(3))):
            self.velx = SHIP_ACC
        if keys[pygame.K_UP] or (joystick and (joystick.get_axis(1)<-DEADZONE or joystick.get_button(0))):
            self.vely = -SHIP_ACC
        if keys[pygame.K_DOWN] or (joystick and (joystick.get_axis(1)>DEADZONE or joystick.get_button(1))):
            self.vely = SHIP_ACC
        if self.canfire and (keys[pygame.K_SPACE] or (joystick and joystick.get_button(0))):
            bul = Bullet(self.x,self.y-42,BLUE,(0,-1),320,self.bullets)
            self.canfire = False
            shootsfx.play()

        self.velx = min(self.velx, self.health*2)
        self.velx = max(self.velx, -self.health*2)
        self.vely = min(self.vely, self.health)
        self.vely = max(self.vely, -self.health)

        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN] or (joystick and (math.fabs(joystick.get_axis(1))>DEADZONE or joystick.get_button(0) or joystick.get_button(1)))):
            self.vely = 0
        if not (keys[pygame.K_LEFT] or keys[pygame.K_RIGHT] or (joystick and (math.fabs(joystick.get_axis(0))>DEADZONE or joystick.get_button(2) or joystick.get_button(3)))):
            self.velx = 0
            
        if self.x+(self.velx*dt)>640-48 or self.x+(self.velx*dt)<48:
            self.velx = 0
        if self.y+(self.vely*dt)>720-48 or self.y+(self.vely*dt)<48:
            self.vely = 0
            
        self.x += self.velx * dt
        self.y += self.vely * dt
