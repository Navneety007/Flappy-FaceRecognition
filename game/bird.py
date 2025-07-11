import pygame

class Bird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 20
        self.velocity = 0
        self.flap_strength = -10
        self.color = (255, 0, 0)
    
    def update(self):
        pass
    
    def flap(self):
        self.velocity = self.flap_strength
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.radius)
        
    def set_position(self, y):
        self.y = y