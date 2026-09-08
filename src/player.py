import pygame


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
        
        self.speed = 200
        self.size = 10
        
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
            
        if keys[pygame.K_w]:
            self.y -= self.speed * dt
            
        if keys[pygame.K_s]:
            self.y += self.speed * dt
                
        if keys[pygame.K_a]:
            self.x -= self.speed * dt
                
        if keys[pygame.K_d]:
            self.x += self.speed * dt
                
    def draw(self, screen):
        pygame.draw.circle(
            screen,
            "red",
            (int(self.x), int(self.y)),
            self.size
        )