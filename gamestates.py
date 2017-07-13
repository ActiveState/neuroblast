'''The MIT License (MIT)

Copyright (c) 2017 ActiveState Software Inc.

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
    def update(self, screen, event_queue, dt, clock, joystick, netmodel):
        return self

class Play(GameState):
    def __init__(self, trainingMode):
        if utils.trainedBrain:
            self.brain = utils.trainedBrain
        else:
            self.brain = Brain()
        self.enemyspeed = 16
        self.enemyBullets = pygame.sprite.Group()
        self.userBullets = pygame.sprite.Group()
        self.userGroup = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player(self.userBullets)
        self.enemy = Enemy(self.enemyBullets, self.brain,self.enemyspeed)
        self.userGroup.add(self.player)
        self.enemies.add(self.enemy)
        self.player.lives = 3
        self.score = 0
        self.spawntimer = 0
        self.spawnbreak = 8
        self.trainingMode = trainingMode

    def update(self, screen, event_queue, dt, clock, joystick, netmodel):
        self.player.update(screen, event_queue, dt,joystick)
        self.enemies.update(screen, event_queue, dt, (self.player.x,self.player.y), (self.player.velx,self.player.vely), self.trainingMode, netmodel)

        # Spawn new enemies
        self.spawntimer += dt
        if self.spawntimer > self.spawnbreak:
            self.spawnbreak = max(2,self.spawnbreak-0.5)
            self.enemyspeed = max(0,self.enemyspeed+2)
            self.enemies.add(Enemy(self.enemyBullets, self.brain,self.enemyspeed))
            self.spawntimer = 0

        if not(self.player.blinking):
            player_hit = pygame.sprite.spritecollide(self.player,self.enemyBullets, True)
            for bullet in player_hit:
                self.brain.record_hit(bullet)
                if not (self.trainingMode):
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
            enemy.TakeDamage(10)
            for b in bullets:
                enemy.playanim("hit",(b.rect.x,b.rect.y))
            self.score += 50

        ## Update enemy animation frames
        for enemy in self.enemies:
            if enemy.anim:
                if enemy.anim.playing:
                    enemy.anim.update(screen,(enemy.x+enemy.animoffset[0],enemy.y+enemy.animoffset[1]),dt)
                else:
                    enemy.anim = None
            
        
        # Effects go here TODO make them a sprite layer
        if self.player.anim:
            if self.player.anim.playing:
                self.player.anim.update(screen,(self.player.x+self.player.animoffset[0],self.player.y+self.player.animoffset[1]),dt)
            else:
                self.player.anim = None
                
        self.brain.draw(screen)             
        
        displaytext("FPS:{:.2f}".format(clock.get_fps()) , 16, 60, 20, WHITE, screen)
        displaytext("Score: "+str(self.score), 16, 200, 20, WHITE, screen)
        displaytext("Health: "+str(self.player.health), 16, 350, 20, WHITE, screen)
        displaytext("Lives: "+str(self.player.lives) , 16, 500, 20, WHITE, screen)

        displaytext("Neural Net Visualization", 16, 960, 20, WHITE, screen)
        

        for event in event_queue:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if (self.trainingMode):
                        self.brain.learn()
                        utils.trainedBrain = self.brain
                        if (netmodel == 1):
                            self.brain.train()  # Train the tensorflow version
                    return Menu(self.brain)
                        
        if self.trainingMode:
            self.brain.learn()

        if not(self.player.alive()):
            if (self.trainingMode):
                self.brain.learn()
                utils.trainedBrain = self.brain
                return Menu(None)
            else:
                return GameOver(self.score) 

        return self

class GameOver(GameState):
    def __init__(self,score):
        self.score = score
        self.name = ""
        gameover.pressed = ""
    def update(self,screen,event_queue,dt,clock, joystick, netmodel):
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
        
    def update(self,screen,event_queue,dt,clock,joystick, netmodel):
        nextState = self
        leaderboard.DisplayLeaderBoard(screen,self.highscores,self.name)
        for event in event_queue:
            if event.type == pygame.KEYDOWN:
                nextState = Menu(None)
        
        
        return nextState

# Draws the menu on screen.
# This is a class that is just instantiated
# While that object exists, it processes stuff
# Only one "GameState" object can exist at one time
class Menu(GameState):
    def __init__(self, brain):
        self.menu_selection = 2
        self.brain = brain
        self.logo = pygame.image.load("art/neuro-blast_logo.png")
        self.intel = pygame.image.load("art/Intel-logo_blue.png")
        self.activestate = pygame.image.load("art/as-logo.png")
        self.intel = pygame.transform.smoothscale(self.intel,(self.intel.get_width()/2,self.intel.get_height()/2))
        self.activestate = pygame.transform.smoothscale(self.activestate,(self.activestate.get_width()/2,self.activestate.get_height()/2))
        
    def update(self, screen, event_queue, dt,clock,joystick, netmodel):
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
                        nextState = Play(True)
                    else:
                        nextState = None
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_x):
                    self.ExportModel()
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_d):
                    self.DumpData()
        return nextState

    def ExportModel(self):
        import keras.backend as K
        from tensorflow.python.saved_model import builder as saved_model_builder
        from tensorflow.python.saved_model import utils
        from tensorflow.python.saved_model import tag_constants, signature_constants
        from tensorflow.python.saved_model.signature_def_utils_impl import build_signature_def, predict_signature_def
        from tensorflow.contrib.session_bundle import exporter

        print "EXPORTING MODEL..."

        export_path = 'exported_brain'
        builder = saved_model_builder.SavedModelBuilder(export_path)

        signature = predict_signature_def(inputs={'inputs': self.brain.keras.input},
                                    outputs={'outputs': self.brain.keras.output})

        with K.get_session() as sess:
            builder.add_meta_graph_and_variables(sess=sess,
                                            tags=[tag_constants.TRAINING],
                                            signature_def_map={'predict': signature})
            builder.save()

        print "...done!"
    
    def DumpData(self):
        f = open('traindata.csv', 'w')
        
        for k,v in self.brain.mapShots.iteritems():
            # Convert our tuple to a numpy array
            if k in self.brain.mapHits:
                a = list(v)
                myList = ','.join(map(str, a))
                output = str(self.brain.mapHits[k])
                f.write(myList+","+output+"\n")
        
        f.close()  # you can omit in most cases as the destructor will call it
        