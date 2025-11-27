import pygame
from car import Car

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

# buat mobil player
player = Car(400, 300, color=(255, 165, 0))

# # dinding
# walls = [
#     pygame.Rect(50, 50, 700, 20),
#     pygame.Rect(50, 530, 700, 20),
#     pygame.Rect(50, 50, 20, 500),
#     pygame.Rect(730, 50, 20, 500),
#     pygame.Rect(300, 200, 200, 20),
# ]

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.update([])

    # render
    screen.fill((30, 30, 30))
    for wall in []:
        pygame.draw.rect(screen, (200, 200, 200), wall)

    player.draw(screen)
    pygame.display.flip()

    pygame.display.set_caption(f"Speed: {player.velocity:.2f}")

pygame.quit()
