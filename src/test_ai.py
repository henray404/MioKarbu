import pygame
import pickle
import math
from object.track import Track

class Car:
    def __init__(self):
        self.surface = pygame.image.load("assets/motor/pink-1.png")
        self.surface = pygame.transform.scale(self.surface, (92, 46))
        self.rotate_surface = self.surface
        self.pos = [600, 240]
        self.angle = 0
        self.speed = 0
        self.center = [self.pos[0] + 46, self.pos[1] + 23]
        self.radars = []
        self.is_alive = True
        self.distance = 0

    def draw(self, screen):
        screen.blit(self.rotate_surface, self.pos)
        self.draw_radar(screen)

    def draw_radar(self, screen):
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, map):
        self.is_alive = True
        for point in self.four_points:
            if map.get_at((int(point[0]), int(point[1]))) == (255, 255, 255, 255):
                self.is_alive = False
                break

    def check_radar(self, degree, map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        while not map.get_at((x, y)) == (255, 255, 255, 255) and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, map):
        self.speed = 10
        self.rotate_surface = pygame.transform.rotate(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        if self.pos[0] < 20:
            self.pos[0] = 20
        elif self.pos[0] > 1920 - 120:
            self.pos[0] = 1920 - 120

        self.distance += self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        if self.pos[1] < 20:
            self.pos[1] = 20
        elif self.pos[1] > 1440 - 120:
            self.pos[1] = 1440 - 120

        self.center = [int(self.pos[0]) + 46, int(self.pos[1]) + 23]
        length = 23
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(map)
        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, map)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)
        return return_values

def run_car(network):
    pygame.init()
    screen = pygame.display.set_mode((1024, 768))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)

    # Track loading
    track_obj = Track("mandalika", screen)
    map = pygame.image.load('assets/tracks/mandalika.png').convert()
    map = pygame.transform.scale(map, (1920, 1440))

    # Camera setup
    camera_x = 0
    camera_y = 0

    car = Car()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    run_car(network)  # Restart
                    return

        if car.is_alive:
            # Get sensor data
            output = network.activate(car.get_data())
            choice = output.index(max(output))
            
            if choice == 0:
                car.angle += 10
            elif choice == 1:
                car.angle -= 10
            
            car.update(map)

            # Camera follow car
            camera_x = car.center[0] - 512
            camera_y = car.center[1] - 384

            # Camera bounds
            if camera_x < 0:
                camera_x = 0
            elif camera_x > 1920 - 1024:
                camera_x = 1920 - 1024
            if camera_y < 0:
                camera_y = 0
            elif camera_y > 1440 - 768:
                camera_y = 1440 - 768

        # Draw everything
        screen.fill((0, 0, 0))
        screen.blit(map, (0 - camera_x, 0 - camera_y))
        car.draw(screen)

        # Display info
        distance_text = font.render(f"Distance: {int(car.distance)}", True, (255, 255, 255))
        screen.blit(distance_text, (10, 10))
        
        if not car.is_alive:
            game_over_text = font.render("GAME OVER - Press R to restart", True, (255, 0, 0))
            screen.blit(game_over_text, (300, 384))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        with open('best_network.pkl', 'rb') as f:
            network = pickle.load(f)
        print("Loaded best network!")
        run_car(network)
    except FileNotFoundError:
        print("best_network.pkl not found! Train the AI first using main_rl.py")
    except Exception as e:
        print(f"Error loading network: {e}")
