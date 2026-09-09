import pygame 
from game.doom_engine import DoomEngine

pygame.init()

doom = DoomEngine(
    "assets/freedoom1.wad"
)



screen = pygame.display.set_mode(
    (0, 0),
    pygame.FULLSCREEN  
)

pygame.display.set_caption("Totally real not fake doom")



clock = pygame.time.Clock()
running = True

while running:
    
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            running = False
            
        doom.handle_event(event)
            
        
    doom.tick()
        
    framebuffer = bytearray(doom.get_framebuffer())
    
    framebuffer[3::4] = b'\xff' * (doom.width * doom.height)
        
    doom_surface = pygame.image.frombuffer(
        framebuffer,
        (doom.width, doom.height),
        "BGRA"
    )
    
    window_width, window_height = screen.get_size()
    
    maxScale = 3
    
    scale = min(
        window_width / doom.width,
        window_height / doom.height,
        maxScale
    )
    
    scaledWidth = int(doom.width * scale)
    scaledheight = int(doom.height * scale)
        
    scaled_surface = pygame.transform.scale(
        doom_surface,
        (scaledWidth, scaledheight)
    )
    
    x = (window_width - scaledWidth) // 2
    y = (window_height - scaledheight) // 2
    
    screen.fill((0, 0, 0))
        
    screen.blit(scaled_surface, (x, y))
        
    pygame.display.flip()
    
    clock.tick(60)
    
pygame.quit