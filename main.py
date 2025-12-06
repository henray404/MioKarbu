"""
Tabrak Bahlil - Main Game (Player Mode)
=======================================

Entry point untuk bermain game secara manual.
Gunakan WASD untuk mengontrol mobil.
"""

import pygame
import os

# Path setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Car:
    """Simple car untuk player control"""
    
    def __init__(self, x, y, color=(255, 165, 0)):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.color = color

        # Physics
        self.acceleration_rate = 0.8
        self.friction = 0.98
        self.steering_rate = 3
        self.max_speed = 4
        self.length = 40
        self.width = 20

        # Surface
        self.surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        self.surface.fill(color)
        
        self.steering_input = 0

    def handle_input(self, keys):
        """Handle keyboard input"""
        import math
        
        # Acceleration
        if keys[pygame.K_w]:
            self.velocity += self.acceleration_rate
        elif keys[pygame.K_s]:
            self.velocity -= self.acceleration_rate
        else:
            self.velocity *= self.friction

        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))

        # Steering
        self.steering_input = 0
        if keys[pygame.K_d]:
            self.steering_input = 1
        elif keys[pygame.K_a]:
            self.steering_input = -1

        self.angle += math.radians(self.steering_rate) * self.steering_input

    def update(self, walls):
        """Update position dan collision"""
        import math
        
        prev_x, prev_y = self.x, self.y

        # Movement dengan drift
        drift_offset = -0.3 * self.steering_input * (self.velocity / self.max_speed)
        move_angle = self.angle + drift_offset

        self.x += math.cos(move_angle) * self.velocity
        self.y += math.sin(move_angle) * self.velocity

        # Collision
        rotated = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        self.rect = rotated.get_rect(center=(self.x, self.y))
        
        for wall in walls:
            if self.rect.colliderect(wall):
                self.x, self.y = prev_x, prev_y
                self.velocity *= -0.4
                break

    def draw(self, screen):
        """Draw car"""
        import math
        
        rotated = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)

        # Direction indicator
        front_x = self.x + math.cos(self.angle) * (self.length / 2)
        front_y = self.y + math.sin(self.angle) * (self.length / 2)
        pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (front_x, front_y), 3)
        pygame.draw.circle(screen, (255, 0, 0), (int(front_x), int(front_y)), 4)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tabrak Bahlil - Player Mode")
    clock = pygame.time.Clock()

    # Create player car
    player = Car(400, 300, color=(255, 165, 0))

    # Walls (optional, bisa di-enable)
    walls = []
    # walls = [
    #     pygame.Rect(50, 50, 700, 20),
    #     pygame.Rect(50, 530, 700, 20),
    #     pygame.Rect(50, 50, 20, 500),
    #     pygame.Rect(730, 50, 20, 500),
    # ]

    running = True
    while running:
        dt = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(walls)

        # Render
        screen.fill((30, 30, 30))
        
        for wall in walls:
            pygame.draw.rect(screen, (200, 200, 200), wall)

        player.draw(screen)
        
        # Info
        font = pygame.font.Font(None, 36)
        text = font.render(f"Speed: {player.velocity:.2f} | WASD to move", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
