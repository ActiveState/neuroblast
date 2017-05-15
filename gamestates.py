import pygame
import utils
from utils import *
from actors import *
from brain import Brain

import math
import leaderboard
import gameover

# GameState object will return a new state object if it transitions
class GameState(object):
    def update(self, screen, event_queue, dt, clock, joystick):
        return self

class Play(GameState):
    def __init__(self, trainingMode):
        if utils.trainedBrain:
            self.brain = utils.trainedBrain
            print "ADDING A TRAINED BRAIN "+str(self.brain.id)
        else:
            self.brain = Brain()
            print "CREATING A NEW BRAIN "+str(self.brain.id)
        self.enemyBullets = pygame.sprite.Group()
        self.userBullets = pygame.sprite.Group()
        self.userGroup = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player(self.userBullets)
        self.enemy = Enemy(self.enemyBullets, self.brain)
        self.userGroup.add(self.player)
        self.enemies.add(self.enemy)
        self.player.lives = 0
        self.score = 0
        self.spawntimer = 0
        self.spawnbreak = 8
        self.trainingMode = trainingMode

    def update(self, screen, event_queue, dt, clock, joystick):
        self.player.update(screen, event_queue, dt,joystick)
        self.enemies.update(screen, event_queue, dt, (self.player.x,self.player.y), (self.player.velx,self.player.vely), self.trainingMode)

        # Spawn new enemies
        self.spawntimer += dt
        if self.spawntimer > self.spawnbreak:
            self.enemies.add(Enemy(self.enemyBullets, self.brain))
            self.spawntimer = 0

        if not(self.player.blinking):
            player_hit = pygame.sprite.spritecollide(self.player,self.enemyBullets, True)
            for bullet in player_hit:
                self.brain.record_hit(bullet)
                self.player.TakeDamage(20)
                self.player.playanim("hit",(bullet.rect.x,bullet.rect.y))
        
            
        if not(self.player.blinking and self.player.blinkon):
            self.userGroup.draw(screen)
        self.enemies.draw(screen)
        self.enemyBullets.update(dt)
        self.enemyBullets.draw(screen)
        self.userBullets.update(dt)
        self.userBullets.draw(screen)

        enemies_hit = pygame.sprite.groupcollide(self.enemies,self.userBullets,False,True)
        for enemy, bullets in enemies_hit.iteritems():
            enemy.TakeDamage(20)
            for b in bullets:
                enemy.playanim("hit",(b.rect.x,b.rect.y))
            self.score += 50

        ## Update enemy animation frames
        for enemy in self.enemies:
            if enemy.anim:
                if enemy.anim.playing:
                    #print enemy.animoffset
                    enemy.anim.update(screen,(enemy.x+enemy.animoffset[0],enemy.y+enemy.animoffset[1]),dt)
                else:
                    enemy.anim = None
            
        
        # Effects go here TODO make them a sprite layer
        if self.player.anim:
            if self.player.anim.playing:
                self.player.anim.update(screen,(self.player.x+self.player.animoffset[0],self.player.y+self.player.animoffset[1]),dt)
            else:
                self.player.anim = None
                
                        
        
        displaytext("FPS:{:.2f}".format(clock.get_fps()) , 16, 60, 20, WHITE, screen)
        displaytext("Score: "+str(self.score), 16, 200, 20, WHITE, screen)
        displaytext("Health: "+str(self.player.health), 16, 350, 20, WHITE, screen)
        displaytext("Lives: "+str(self.player.lives) , 16, 500, 20, WHITE, screen)
        
        if not(self.player.alive()):
            if (self.trainingMode):
                self.brain.learn()
                utils.trainedBrain = self.brain
                return Menu()
            else:
                return GameOver(self.score) 

        return self

class GameOver(GameState):
    def __init__(self,score):
        print "Creating gameover state with score "+str(score)
        self.score = score
        self.name = ""
        gameover.pressed = ""
    def update(self,screen,event_queue,dt,clock, joystick):
        nextState = self        
        self.name = gameover.enter_text(event_queue,screen, 8)
        for event in event_queue:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN:
                    self.name = gameover.pressed
                    leaderboard.StoreScore(self.name,self.score)
                    nextState = Leaderboard(self.name)                    
        return nextState

class Leaderboard(GameState):
    def __init__(self,name):
        self.name = name
        self.highscores = leaderboard.GetScores()
        #print "init gameover state"
        
    def update(self,screen,event_queue,dt,clock,joystick):
        nextState = self
        #print "in gameover state"
        #print self.highscores
        leaderboard.DisplayLeaderBoard(screen,self.highscores,self.name)
        for event in event_queue:
            if event.type == pygame.KEYDOWN:
                nextState = Menu()
        
        
        return nextState

# Draws the menu on screen.
# This is a class that is just instantiated
# While that object exists, it processes stuff
# Only one "GameState" object can exist at one time
class Menu(GameState):
    def __init__(self):
        self.menu_selection = 2
        self.logo = pygame.image.load("neuro-blast_logo.png")
        self.intel = pygame.image.load("Intel-logo_blue.png")
        self.activestate = pygame.image.load("as-logo.png")
        self.intel = pygame.transform.smoothscale(self.intel,(self.intel.get_width()/2,self.intel.get_height()/2))
        self.activestate = pygame.transform.smoothscale(self.activestate,(self.activestate.get_width()/2,self.activestate.get_height()/2))
        
    def update(self, screen, event_queue, dt,clock,joystick):
        # Logos/titles
        screen.blit(self.logo,(screen.get_width() / 4 - 265,screen.get_height() * 3 / 4-500))
        screen.blit(self.intel,(screen.get_width() / 4 - 300,screen.get_height()-130))
        screen.blit(self.activestate,(screen.get_width() - 980,screen.get_height() - 130))

        nextState = self
        displaytext('Play', 32, screen.get_width() / 4 - 20, screen.get_height() * 3 / 4
                    - 80, WHITE, screen)
        displaytext('Train', 32, screen.get_width() / 4 - 20, screen.get_height() * 3 / 4
                    - 40, WHITE, screen)
        displaytext('Exit', 32, screen.get_width() / 4 - 20, screen.get_height() * 3 / 4,
                    WHITE, screen)
        #displaytext('Neuro/Blast v1.0', 12, screen.get_width() - 80, screen.get_height() - 20,
 #                   WHITE, screen)
        #displaytext('Copyright (C) 2017 ActiveState Software Inc.', 12, screen.get_width() - 80, screen.get_height() - 10,
 #                   WHITE, screen)
        displaytext(u'\u00bb', 32, screen.get_width() / 4 - 60, screen.get_height() * 3 / 4
                    - 40*self.menu_selection, WHITE, screen)

        # Each game state processes its own input queue in its own way to avoid messy input logic
        for event in event_queue:
            if event.type == pygame.KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                if (event.type == pygame.KEYDOWN and (event.key == pygame.K_DOWN)) or (event.type == pygame.JOYBUTTONDOWN and (event.button == 1)) or (event.type == pygame.JOYAXISMOTION and (event.axis == 1 or event.value >= DEADZONE)):
                    self.menu_selection -= 1
                    if self.menu_selection == -1:
                        self.menu_selection = 2
                if (event.type == pygame.KEYDOWN and (event.key == pygame.K_UP)) or (event.type == pygame.JOYBUTTONDOWN and (event.button == 0)) or (event.type == pygame.JOYAXISMOTION and (event.axis == 1 or event.value <= -DEADZONE)):
                    self.menu_selection += 1
                    if self.menu_selection == 3:
                        self.menu_selection = 0
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (event.type == pygame.JOYBUTTONDOWN and event.button == 11):
                    if self.menu_selection == 2:
                        nextState = Play(False)
                    elif self.menu_selection == 1:
                        print "TRAINING MODE"
                        nextState = Play(True)
                    else:
                        nextState = None
        return nextState
