import pygame
import sys
import os

# Add the project's root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import numpy as np
from game.bird import Bird
from game.obstacles import Obstacles
from game.physics import check_collision
from game.face_detect import FaceDetector
from utils.helpers import load_sound

def choose_camera():
    available_cameras = []
    for i in range(5):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()
    
    if not available_cameras:
        print("No webcams found. Exiting.")
        sys.exit()

    if len(available_cameras) == 1:
        return available_cameras[0]

    print("Available webcams:")
    for i, cam_index in enumerate(available_cameras):
        print(f"  {i}: Camera {cam_index}")
    
    while True:
        try:
            choice = int(input(f"Choose a webcam (0 to {len(available_cameras) - 1}): "))
            if 0 <= choice < len(available_cameras):
                return available_cameras[choice]
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")

selected_camera_index = choose_camera()

pygame.init()
pygame.font.init()
face_detector = FaceDetector(camera_index=selected_camera_index)

GAME_WIDTH, GAME_HEIGHT = 800, 600
PREVIEW_WIDTH = 600
WIDTH, HEIGHT = GAME_WIDTH + PREVIEW_WIDTH, GAME_HEIGHT
FPS = 120

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Face")

font = pygame.font.SysFont(None, 54)
small_font = pygame.font.SysFont(None, 32)

base_dir = os.path.dirname(os.path.abspath(__file__))
sound_dir = os.path.join(base_dir, 'assets', 'sounds')
point_sound = load_sound(os.path.join(sound_dir, 'point.mp3'))
hit_sound = load_sound(os.path.join(sound_dir, 'hit.mp3'))

def init_game():
    bird = Bird(x=150, y=GAME_HEIGHT // 2)
    obstacles = Obstacles(GAME_WIDTH, GAME_HEIGHT)
    score = 0
    game_state = "COUNTDOWN"
    countdown_start = pygame.time.get_ticks()
    return bird, obstacles, game_state, score, countdown_start

bird, obstacles, game_state, score, countdown_start = init_game()

clock = pygame.time.Clock()
running = True
frame_count = 0
frame, face_y, face_rect_data = None, None, None
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == "GAME_OVER":
                    bird, obstacles, game_state, score, countdown_start = init_game()

    screen.fill((0, 0, 0))

    # Perform face detection continuously to keep preview active
    frame_count += 1
    if frame_count % 3 == 0:
        new_frame, new_face_y, new_face_rect_data = face_detector.get_frame_and_face_y(GAME_HEIGHT)
        if new_frame is not None:
            frame, face_y, face_rect_data = new_frame, new_face_y, new_face_rect_data

    if game_state == "COUNTDOWN":
        game_surface = screen.subsurface(pygame.Rect(0, 0, GAME_WIDTH, GAME_HEIGHT))
        game_surface.fill((135, 206, 235))
        bird.draw(game_surface)
        
        elapsed_time = (pygame.time.get_ticks() - countdown_start) / 1000
        countdown_number = 3 - int(elapsed_time)

        if countdown_number > 0:
            countdown_text = font.render(str(countdown_number), True, (255, 255, 255))
            text_rect = countdown_text.get_rect(center=(GAME_WIDTH // 2, GAME_HEIGHT // 2))
            game_surface.blit(countdown_text, text_rect)
        else:
            game_state = "PLAYING"

    elif game_state == "PLAYING":
        # Update bird position only when the game is active
        if face_y is not None:
            bird.set_position(face_y)

        bird.update()
        obstacles.update()
        
        if check_collision(bird, obstacles):
            hit_sound.play()
            game_state = "GAME_OVER"
        
        for obstacle in obstacles.obstacles:
            if obstacle['x'] + obstacles.width < bird.x and not obstacle.get('passed', False):
                obstacle['passed'] = True
                score += 1
                point_sound.play()

        game_surface = screen.subsurface(pygame.Rect(0, 0, GAME_WIDTH, GAME_HEIGHT))
        game_surface.fill((135, 206, 235))
        bird.draw(game_surface)
        obstacles.draw(game_surface)
        
        score_text = small_font.render(f"Score: {score}", True, (0, 0, 0))
        game_surface.blit(score_text, (10, 10))

    elif game_state == "GAME_OVER":
        game_surface = screen.subsurface(pygame.Rect(0, 0, GAME_WIDTH, GAME_HEIGHT))
        game_surface.fill((0, 0, 0))
        
        game_over_text = font.render("Game Over!", True, (255, 0, 0))
        game_surface.blit(game_over_text, (GAME_WIDTH//2 - game_over_text.get_width()//2, GAME_HEIGHT//2 - 50))
        
        final_score_text = small_font.render(f"Final Score: {score}", True, (255, 255, 255))
        game_surface.blit(final_score_text, (GAME_WIDTH//2 - final_score_text.get_width()//2, GAME_HEIGHT//2))
        
        play_again_text = small_font.render("Press SPACE to Play Again", True, (255, 255, 255))
        game_surface.blit(play_again_text, (GAME_WIDTH//2 - play_again_text.get_width()//2, GAME_HEIGHT//2 + 50))

    if frame is not None:
        # Create a copy of the frame to draw on, to avoid visual glitches
        draw_frame = frame.copy()

        # Add title text to the preview with a larger font
        title_text = "Flappy Bird Gym Edition"
        cv2.putText(draw_frame, title_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 0), 2)

        if face_rect_data is not None:
            (x, y, w, h) = face_rect_data
            face_center_x = x + w // 2
            face_center_y = y + h // 2

            # Draw bounding box
            cv2.rectangle(draw_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Draw only the vertical crosshair line
            cv2.line(draw_frame, (face_center_x, 0), (face_center_x, draw_frame.shape[0]), (0, 255, 255), 1)
            
            # Draw center circle
            cv2.circle(draw_frame, (face_center_x, face_center_y), 5, (0, 0, 255), -1)

            # Display X-coordinate with a larger font
            coord_text = f"X: {face_center_x}"
            cv2.putText(draw_frame, coord_text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)

        preview_surface = screen.subsurface(pygame.Rect(GAME_WIDTH, 0, PREVIEW_WIDTH, HEIGHT))
        frame_rgb = cv2.cvtColor(draw_frame, cv2.COLOR_BGR2RGB)
        frame_pygame = pygame.image.frombuffer(frame_rgb.tobytes(), frame_rgb.shape[1::-1], "RGB")
        
        frame_rect = frame_pygame.get_rect()
        scale = min(PREVIEW_WIDTH / frame_rect.width, HEIGHT / frame_rect.height)
        scaled_size = (int(frame_rect.width * scale), int(frame_rect.height * scale))
        scaled_frame = pygame.transform.scale(frame_pygame, scaled_size)
        
        preview_rect = scaled_frame.get_rect(center=preview_surface.get_rect().center)
        preview_surface.blit(scaled_frame, preview_rect)

    pygame.display.flip()
    
    clock.tick(FPS)

face_detector.release()
pygame.quit()
sys.exit()