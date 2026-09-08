import pygame

class GameMap:
    def __init__(self):
        self.title_size = 40
        
        
        self.map = [
            "####################",
            "#..................#",
            "#..................#",
            "#......####........#",
            "#......#..#........#",
            "#......#..#........#",
            "#......####........#",
            "#..................#",
            "#..................#",
            "####################",
        ]
        
    def draw(self, screen):
        for y, row in enumerate(self.map):
            for x, title in enumerate(row):
                if title == "#":
                    rect = pygame.Rect(
                        x * self.title_size,
                        y * self.title_size,
                        self.title_size,
                        self,self.title_size
                    )
                        
                    pygame.draw.rect(screen, "gray", rect)
                        
                    