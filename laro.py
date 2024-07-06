import pygame
import sys
import random
import math

pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
RADIUS = 10
SPEED = 5
BASE_SPEED = SPEED  # Base speed of the green character
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BULLET_COLOR = (255, 0, 0)
BULLET_RADIUS = 5
BULLET_SPEED = 7
FONT_SIZE = 36

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Green Blob Game")

# Font for text
font = pygame.font.Font(None, FONT_SIZE)

pygame.mouse.set_visible(False)

# Global variables
up_pressed = False
down_pressed = False
left_pressed = False
right_pressed = False

score = 0
level = 1
bullet_interval = 1000  # Interval in milliseconds
powerup_active = False
powerup_duration = 5000  # Duration of speed boost in milliseconds
powerup_timer = 0
spawn_powerup = False
last_powerup_spawn = 0
powerup_spawn_interval = 2  # Interval in levels for power-up respawn

high_score = 0  # Initialize high score

# Bullet class
class Bullet:
    def __init__(self, target_x, target_y):
        # Randomly choose a border side and position
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.uniform(0, WIDTH)
            self.y = 0
        elif side == 'bottom':
            self.x = random.uniform(0, WIDTH)
            self.y = HEIGHT
        elif side == 'left':
            self.x = 0
            self.y = random.uniform(0, HEIGHT)
        elif side == 'right':
            self.x = WIDTH
            self.y = random.uniform(0, HEIGHT)

        # Calculate direction vector to the target (character's position)
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance = math.hypot(direction_x, direction_y)

        # Normalize and scale by bullet speed
        self.dx = BULLET_SPEED * direction_x / distance
        self.dy = BULLET_SPEED * direction_y / distance

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self):
        pygame.draw.circle(screen, BULLET_COLOR, (int(self.x), int(self.y)), BULLET_RADIUS)

    def check_collision(self, target_x, target_y, target_radius):
        distance = math.hypot(self.x - target_x, self.y - target_y)
        return distance < (BULLET_RADIUS + target_radius)

# Power-up class
class PowerUp:
    def __init__(self):
        self.x = random.randint(50, WIDTH - 50)
        self.y = random.randint(50, HEIGHT - 50)
        self.width = 30
        self.height = 30
        self.color = BLUE

    def draw(self):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def check_collision(self, target_x, target_y, target_radius):
        # Check collision with circular target (green character)
        rect_center_x = self.x + self.width // 2
        rect_center_y = self.y + self.height // 2
        distance = math.hypot(rect_center_x - target_x, rect_center_y - target_y)
        return distance < (self.width // 2 + target_radius)

def game_over():
    global score, level, high_score

    # Update high score if current score is higher
    if score > high_score:
        high_score = score

    screen.fill(BLACK)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - score_text.get_height() // 2 + 50))
    screen.blit(high_score_text, (WIDTH // 2 - high_score_text.get_width() // 2, HEIGHT // 2 - high_score_text.get_height() // 2 + 100))
    pygame.display.flip()

    # Wait for the player to press Enter to restart the game
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    score = 0
                    level = 1
                    return

def draw_game():
    global up_pressed, down_pressed, left_pressed, right_pressed, score, level, bullet_interval, powerup_active, powerup_timer, SPEED, spawn_powerup, last_powerup_spawn

    x, y = 100, 100
    bullets = []
    last_bullet_time = pygame.time.get_ticks()
    start_time = pygame.time.get_ticks()

    # Create a power-up instance
    powerup = PowerUp()

    while True:
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    up_pressed = True
                elif event.key == pygame.K_DOWN:
                    down_pressed = True
                elif event.key == pygame.K_LEFT:
                    left_pressed = True
                elif event.key == pygame.K_RIGHT:
                    right_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    up_pressed = False
                elif event.key == pygame.K_DOWN:
                    down_pressed = False
                elif event.key == pygame.K_LEFT:
                    left_pressed = False
                elif event.key == pygame.K_RIGHT:
                    right_pressed = False

        # Clear screen
        screen.fill(BLACK)

        # Handle inputs
        if up_pressed:
            y -= SPEED
        if down_pressed:
            y += SPEED
        if left_pressed:
            x -= SPEED
        if right_pressed:
            x += SPEED

        # Boundary check
        if y < RADIUS:
            y = RADIUS
        if y > HEIGHT - RADIUS:
            y = HEIGHT - RADIUS
        if x < RADIUS:
            x = RADIUS
        if x > WIDTH - RADIUS:
            x = WIDTH - RADIUS

        # Calculate score based on elapsed time
        score = int(elapsed_time / 1000)  # Score increases every second

        # Increase bullet frequency with level
        if level >= 3:
            bullet_interval = max(500 - level * 30, 100)  # Decrease interval over time

        # Shoot bullets automatically
        if current_time - last_bullet_time >= bullet_interval:
            bullets.append(Bullet(x, y))
            last_bullet_time = current_time

        # Update and draw bullets
        for bullet in bullets[:]:
            bullet.update()
            if bullet.check_collision(x, y, RADIUS):
                game_over()
                draw_game()  # Restart the game
                return
            if 0 <= bullet.x <= WIDTH and 0 <= bullet.y <= HEIGHT:
                bullet.draw()
            else:
                bullets.remove(bullet)

        # Draw green blob
        pygame.draw.circle(screen, GREEN, (x, y), RADIUS)

        # Spawn power-up
        if spawn_powerup and level >= 3:
            powerup.draw()

            # Check collision with power-up
            if not powerup_active and powerup.check_collision(x, y, RADIUS):
                powerup_active = True
                spawn_powerup = False
                last_powerup_spawn = level

                # Increase speed
                SPEED += 5

                # Reset power-up position
                powerup = PowerUp()

        # Check if power-up duration is over
        if powerup_active and current_time - powerup_timer >= powerup_duration:
            powerup_active = False
            SPEED = BASE_SPEED  # Reset speed to base speed

        # Display score and level
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        level_text = font.render(f"Level: {level}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        # Update the display
        pygame.display.flip()
        pygame.time.Clock().tick(60)

        # Randomly spawn a power-up
        if not spawn_powerup and random.random() < 0.01 * level and level - last_powerup_spawn >= powerup_spawn_interval:
            spawn_powerup = True

        # Increase level based on score
        if score >= level * 10:
            level += 1

draw_game()
