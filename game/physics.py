def check_collision(bird, obstacles):
    if bird.y - bird.radius <= 0 or bird.y + bird.radius >= obstacles.screen_height:
        return True
    
    for obstacle in obstacles.obstacles:
        if (bird.x + bird.radius > obstacle['x'] and 
            bird.x - bird.radius < obstacle['x'] + obstacles.width):
            
            if bird.y - bird.radius < obstacle['top_height']:
                return True
            
            bottom_obstacle_y = obstacles.screen_height - obstacle['bottom_height']
            if bird.y + bird.radius > bottom_obstacle_y:
                return True
    
    return False