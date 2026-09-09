import pygame 
from game.doom_engine import DoomEngine

pygame.init()

doom = DoomEngine(
    "assets/freedoom1.wad"
)

# doomWidth = 320
# doomHeight = 200

scale = 3

screen = pygame.display.set_mode(
    (
        doom.width * scale,
        doom.height * scale

    )
)

pygame.display.set_caption("Totally real not fake doom")



clock = pygame.time.Clock()
running = True

while running:
    
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
            
        
    doom.tick()
        
    framebuffer = bytearray(doom.get_framebuffer())
    
    framebuffer[3::4] = b'\xff' * (doom.width * doom.height)
        
    doom_surface = pygame.image.frombuffer(
        framebuffer,
        (doom.width, doom.height),
        "BGRA"
    )
        
    scaled_surface = pygame.transform.scale(
        doom_surface,
        (doom.width * scale, doom.height * scale)
    )
        
    screen.blit(scaled_surface, (0, 0))
        
    pygame.display.flip()
    
    clock.tick(60)
    
pygame.quit