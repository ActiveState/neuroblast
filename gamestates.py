import pygame
from utils import *
from actors import *
import leaderboard
import gameover

# GameState object will return a new state object if it transitions
class GameState(object):
    def update(self, screen, event_queue, dt, clock):
        return self

class Play(GameState):
    def __init__(self):
        self.enemyBullets = pygame.sprite.Group()
        self.userBullets = pygame.sprite.Group()
        self.userGroup = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.player = Player(self.userBullets)
        self.enemy = Enemy(self.enemyBullets)
        self.userGroup.add(self.player)
        self.enemies.add(self.enemy)
        self.player.lives = 9
        self.score = 0
        self.spawntimer = 0
        self.spawnbreak = 8

    def update(self, screen, event_queue, dt, clock):
        self.player.update(screen, event_queue, dt)
        self.enemies.update(screen, event_queue, dt, (self.player.x,self.player.y), (self.player.velx,self.player.vely))

        # Spawn new enemies
        self.spawntimer += dt
        if self.spawntimer > self.spawnbreak:
            self.enemies.add(Enemy(self.enemyBullets))
            self.spawntimer = 0

        if not(self.player.blinking):
            player_hit = pygame.sprite.spritecollideany(self.player,self.enemyBullets)
            if player_hit:
                self.player.TakeDamage(20)
                self.player.playanim("hit",(player_hit.rect.x,player_hit.rect.y))
                player_hit.kill()
        
            
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
                    print enemy.animoffset
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
            return GameOver() 

        return self

class GameOver(GameState):
    def __init__(self):
        self.name = ""
        gameover.pressed = ""
    def update(self,screen,event_queue,dt,clock):
        nextState = self
        if self.name == "":
            self.name = gameover.enter_text(event_queue,screen, 8)
        for event in event_queue:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN and self.name == "":
                    self.name = gameover.pressed
                elif event.key == pygame.K_RETURN and self.name != "":
                    nextState = Leaderboard()       
        
        
        return nextState

class Leaderboard(GameState):
    def __init__(self):
        self.highscores = leaderboard.GetScores()
        #print "init gameover state"
        
    def update(self,screen,event_queue,dt,clock):
        nextState = self
        #print "in gameover state"
        print self.highscores
        leaderboard.DisplayLeaderBoard(screen,self.highscores,"Bob")
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
        self.menu_selection = 1
    def update(self, screen, event_queue, dt,clock):
        nextState = self
        displaytext('Play', 32, screen.get_width() / 4 - 20, screen.get_height() * 3 / 4
                    - 40, WHITE, screen)
        displaytext('Exit', 32, screen.get_width() / 4 - 20, screen.get_height() * 3 / 4,
                    WHITE, screen)
        displaytext('Bit Blaster v1.0', 12, screen.get_width() - 80, screen.get_height() - 20,
                    WHITE, screen)
        displaytext('Copyright (C) 2017 ActiveState Software Inc.', 12, screen.get_width() - 80, screen.get_height() - 10,
                    WHITE, screen)
        displaytext(u'\u00bb', 32, screen.get_width() / 4 - 60, screen.get_height() * 3 / 4
                    - 40*self.menu_selection, WHITE, screen)

        # Each game state processes its own input queue in its own way to avoid messy input logic
        for event in event_queue:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    if self.menu_selection == 0:
                        self.menu_selection = 1
                    else:
                        self.menu_selection = 0
                if event.key == pygame.K_RETURN:
                    if self.menu_selection == 1:
                        nextState = Play()
                    else:
                        nextState = None
        return nextState
