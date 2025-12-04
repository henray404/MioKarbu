"""
Main - Entry point untuk game
Menggunakan refactored system dengan PlayerCar dan AICar
"""
import pygame

from entities.player_car import PlayerCar
from entities.ai_car import AICar
from core import GameManager

class WallsDrawable:
    """Static walls drawable"""

    def __init__(self, walls: list[pygame.Rect], color=(200, 200, 200)):
        self.walls = walls
        self.color = color

    def update(self, *args, **kwargs):
        # Static, no update needed
        pass

    def draw(self, screen: pygame.Surface):
        for wall in self.walls:
            pygame.draw.rect(screen, self.color, wall)

# # dinding
# walls = [
#     pygame.Rect(50, 50, 700, 20),
#     pygame.Rect(50, 530, 700, 20),
#     pygame.Rect(50, 50, 20, 500),
#     pygame.Rect(730, 50, 20, 500),
#     pygame.Rect(300, 200, 200, 20),
# ]

# running = True
# while running:
#     dt = clock.tick(60) / 1000
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#     keys = pygame.key.get_pressed()
#     player.handle_input(keys)
#     player.update([])

#     # render
#     screen.fill((30, 30, 30))
#     for wall in []:
#         pygame.draw.rect(screen, (200, 200, 200), wall)


def main():
    # Initialize game manager
    gm = GameManager(
        width=800, height=600, fps=60, bg_color=(50, 50, 50), show_fps=True
    )

    # Load car sprite
    car_sprites = pygame.image.load("asset/car_sprite.png").convert_alpha()
    car_sprites = pygame.transform.scale(
        car_sprites,
        (car_sprites.get_width() // 8, car_sprites.get_height() // 8),
    )

    # Create walls
    walls = [
        pygame.Rect(50, 50, 700, 20),  # top
        pygame.Rect(50, 530, 700, 20),  # bottom
        pygame.Rect(50, 50, 20, 500),  # left
        pygame.Rect(730, 50, 20, 500),  # right
        pygame.Rect(300, 200, 200, 20),  # center obstacle
    ]

    # Create player car (WASD controls)
    player = PlayerCar(
        x=400,
        y=300,
        color=(255, 165, 0),
        enable_sensors=False,  # Player doesn't need sensors
    )
    player.set_debug_mode(True)  # Show player debug info

    # Create AI car with sensors
    ai_car = AICar(
        x=200,
        y=150,
        color=(0, 255, 0),
        image=car_sprites,
        num_sensors=5,
        sensor_range=200.0,
    )
    ai_car.set_debug_mode(True)  # Show sensor visualization
    ai_car.ai_mode = "simple"  # Use simple AI behavior
    

    # Add entities to game manager
    gm.add_entity(player)
    gm.add_entity(ai_car)
    gm.add_static(WallsDrawable(walls))

    # Custom update wrapper to pass walls to entities
    original_update = gm.update

    def update_wrapper(*args, **kwargs):
        # Handle special keys for debug toggle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_p]:
            player.set_debug_mode(not player.debug_mode)
        if keys[pygame.K_l]:
            ai_car.set_debug_mode(not ai_car.debug_mode)

        # Update entities with walls
        return original_update(walls)

    gm.update = update_wrapper  # type: ignore

    print("=" * 60)
    print("🚗 TABRAK BAHLIL - Refactored Version")
    print("=" * 60)
    print("Controls:")
    print("  WASD     - Control player car (orange)")
    print("  F1       - Toggle player debug mode")
    print("  F2       - Toggle AI debug mode (sensors)")
    print("  ESC/X    - Quit game")
    print("=" * 60)
    print("Features:")
    print("  ✓ Modular architecture (Physics, Controller, Sensors)")
    print("  ✓ Player car with keyboard control")
    print("  ✓ AI car with distance sensors")
    print("  ✓ Simple AI behavior (drive & avoid)")
    print("  ✓ Ready for RL agent integration")
    print("=" * 60)

    # Run game
    gm.run()


if __name__ == "__main__":
    main()
