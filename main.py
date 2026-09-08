import pygame

from src.player import Player
from src.map import GameMap

pygame.init()


width = 800
height = 600


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Totally real not fake doom")


clock = pygame.time.Clock()

player = Player(400, 300)
gameMap = GameMap()

running = True

while running:
    dt = clock.tick(60) / 1000
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    player.update(dt)
    
    screen.fill("black")
    
    gameMap.draw(screen)
    player.draw(screen)
    
    pygame.display.flip()
    
    

pygame.quit()
    
