import pygame
from utils import *
from actors import *

# GameState object will return a new state object if it transitions
class GameState(object):
    def update(self, screen, event_queue, dt):
        return self

class Play(GameState):
    def __init__(self):
        self.player = Player()
        self.enemy = Enemy()
        self.userGroup = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.userGroup.add(self.player)
        self.enemies.add(self.enemy)

    def update(self, screen, event_queue, dt):
        self.player.update(screen, event_queue, dt)
        self.enemy.update(screen, event_queue, dt, (self.player.x,self.player.y))

        player_hit = pygame.sprite.spritecollideany(self.player,self.enemy.bullets)
        if player_hit:
            return Menu()
        
        enemy_hit = pygame.sprite.spritecollideany(self.enemy,self.player.bullets)
        if enemy_hit:
            self.enemy.TakeDamage(20)
            enemy_hit.kill()

        return self

# Draws the menu on screen.
# This is a class that is just instantiated
# While that object exists, it processes stuff
# Only one "GameState" object can exist at one time
class Menu(GameState):
    def __init__(self):
        self.menu_selection = 1
    def update(self, screen, event_queue, dt):
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
