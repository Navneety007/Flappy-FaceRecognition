import pygame
import random

class Obstacles:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.obstacles = []
        self.gap_size = 180
        self.width = 50
        self.color = (0, 128, 0)
        self.speed = 12
        self.spawn_timer = 0
        self.spawn_interval = 35
    
    def update(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_obstacle()
        
        for obstacle in self.obstacles:
            obstacle['x'] -= self.speed
        
        self.obstacles = [obs for obs in self.obstacles if obs['x'] + self.width >= 0]
    
    def spawn_obstacle(self):
        gap_y = random.randint(100, self.screen_height - 100 - self.gap_size)
        self.obstacles.append({
            'x': self.screen_width,
            'top_height': gap_y,
            'bottom_height': self.screen_height - gap_y - self.gap_size,
            'passed': False
        })
    
    def draw(self, screen):
        for obstacle in self.obstacles:
            pygame.draw.rect(
                screen, 
                self.color,
                (obstacle['x'], 0, self.width, obstacle['top_height'])
            )
            pygame.draw.rect(
                screen, 
                self.color,
                (
                    obstacle['x'], 
                    self.screen_height - obstacle['bottom_height'], 
                    self.width, 
                    obstacle['bottom_height']
                )
            )