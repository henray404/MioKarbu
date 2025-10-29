import pygame
import math

class Car:
    def __init__(self, x, y, color=(255, 165, 0)):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.color = color

        # konstanta fisika
        self.acceleration_rate = 0.8
        self.friction = 0.98
        self.steering_rate = 3  # derajat per frame
        self.max_speed = 4
        self.length = 40
        self.width = 20

        # internal
        self.surface = pygame.Surface((self.length, self.width), pygame.SRCALPHA)
        self.surface.fill(color)

    def handle_input(self, keys):
        """Kendali manual player"""
        if keys[pygame.K_UP]:
            self.velocity += self.acceleration_rate
        elif keys[pygame.K_DOWN]:
            self.velocity -= self.acceleration_rate
        else:
            self.velocity *= self.friction

        self.velocity = max(-self.max_speed, min(self.max_speed, self.velocity))

        if keys[pygame.K_LEFT]:
            self.angle -= math.radians(self.steering_rate)
        if keys[pygame.K_RIGHT]:
            self.angle += math.radians(self.steering_rate)

    def update(self, walls):
        """Update posisi + deteksi tabrakan"""
        prev_x, prev_y = self.x, self.y

        # update posisi berdasarkan kecepatan dan sudut
        self.x += math.cos(self.angle) * self.velocity
        self.y += math.sin(self.angle) * self.velocity

        rotated_car = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        self.rect = rotated_car.get_rect(center=(self.x, self.y))

        # deteksi tabrakan
        for wall in walls:
            if self.rect.colliderect(wall):
                self.x, self.y = prev_x, prev_y
                self.velocity *= -0.4
                break

    def draw(self, screen):
        """Render mobil dan indikator arah depan"""
        rotated_car = pygame.transform.rotate(self.surface, -math.degrees(self.angle))
        rect = rotated_car.get_rect(center=(self.x, self.y))
        screen.blit(rotated_car, rect)

        # garis depan mobil
        front_x = self.x + math.cos(self.angle) * (self.length / 2)
        front_y = self.y + math.sin(self.angle) * (self.length / 2)
        pygame.draw.line(screen, (0, 255, 0), (self.x, self.y), (front_x, front_y), 3)
        pygame.draw.circle(screen, (255, 0, 0), (int(front_x), int(front_y)), 4)
