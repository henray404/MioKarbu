import pygame
from object.motor import Motor
from object.track import Track
from object.camera import create_screen, update_camera, camera

def main():
    pygame.init()
    
    # Setup screen
    screen_width = 1024
    screen_height = 768
    screen = create_screen(screen_width, screen_height, "Mio-Mber")
    clock = pygame.time.Clock()
    
    # Map size (lebih besar dari layar)
    map_width = 1920
    map_height = 1440
    
    # Load track dengan ukuran map
    track = Track("japan", map_width, map_height)
    
    # Buat motor player di tengah map
    player = Motor(map_width // 2, map_height // 2, color="pink")
    
    # Dinding pembatas map (bukan screen)
    wall_thickness = 1
    walls = [
        pygame.Rect(0, 0, map_width, wall_thickness),  # atas
        pygame.Rect(0, map_height - wall_thickness, map_width, wall_thickness),  # bawah
        pygame.Rect(0, 0, wall_thickness, map_height),  # kiri
        pygame.Rect(map_width - wall_thickness, 0, wall_thickness, map_height),  # kanan
    ]

    running = True
    while running:
        dt = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Input dan update motor
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update(walls)
        
        # Update kamera untuk mengikuti motor
        update_camera(player.x, player.y, map_width, map_height)

        # Render
        screen.fill((30, 30, 30))  # background hitam sebagai fallback
        track.draw(screen, camera)  # gambar track dengan offset kamera
        
        # Gambar dinding jika ada (dengan offset kamera)
        for wall in walls:
            screen_wall = pygame.Rect(wall.x - camera.x, wall.y - camera.y, wall.width, wall.height)
            pygame.draw.rect(screen, (200, 200, 200), screen_wall)

        player.draw(screen, camera)  # gambar motor dengan offset kamera
        pygame.display.flip()

        # Update caption dengan info kecepatan
        pygame.display.set_caption(f"Mio-Mber | Speed: {player.velocity:.2f} | FPS: {clock.get_fps():.0f}")

    pygame.quit()

if __name__ == "__main__":
    main()