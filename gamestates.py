import pygame
from utils import *
from actors import *

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
        self.player.lives = 333
        self.score = 0
        self.spawntimer = 0
        self.spawnbreak = 8

    def update(self, screen, event_queue, dt, clock):
        self.player.update(screen, event_queue, dt)
        self.enemies.update(screen, event_queue, dt, (self.player.x,self.player.y))

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
        
        enemies_hit = pygame.sprite.groupcollide(self.enemies,self.userBullets,False,True)
        for enemy, bullet in enemies_hit.iteritems():
            enemy.TakeDamage(20)
            self.score += 50
            
        if not(self.player.blinking and self.player.blinkon):
            self.userGroup.draw(screen)
        self.enemies.draw(screen)
        self.enemyBullets.update(dt)
        self.enemyBullets.draw(screen)
        self.userBullets.update(dt)
        self.userBullets.draw(screen)
        
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
            return Menu() 

        return self

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
