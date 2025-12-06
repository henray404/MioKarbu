import pygame
from core.motor import Motor
from core.track import Track
from core.distance_sensor import DistanceSensor
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
    track = Track("japan", map_width, map_height, road_threshold=180)
    
    # Buat motor player di tengah map
    player = Motor(map_width // 2, map_height // 2, color="pink")
    
    # Set track untuk pixel-based collision
    player.set_track(track)
    
    # Buat sensor terpisah dan attach ke motor
    sensor = DistanceSensor(num_sensors=7, fov=180, max_distance=200)
    player.set_sensor(sensor)
    
    # Toggle untuk visualisasi sensor
    show_sensors = True

    running = True
    while running:
        dt = clock.tick(60) / 1000
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Toggle sensor visibility dengan Tab
                if event.key == pygame.K_TAB:
                    show_sensors = not show_sensors
        
        # Input dan update motor
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        player.update()  # Tidak perlu walls, sudah pakai track collision
        
        # Get sensor data (untuk debug / AI)
        sensor_data = player.get_sensor_data()
        
        # Update kamera untuk mengikuti motor
        update_camera(player.x, player.y, map_width, map_height)

        # Render
        screen.fill((30, 30, 30))  # background hitam sebagai fallback
        track.draw(screen, camera)  # gambar track dengan offset kamera
        
        # Gambar sensors jika aktif (pakai method dari motor)
        if show_sensors:
            player.draw_sensors(screen, camera)

        player.draw(screen, camera)  # gambar motor dengan offset kamera
        pygame.display.flip()

        # Update caption dengan info
        sensor_str = " | ".join([f"{d:.2f}" for d in sensor_data])
        pygame.display.set_caption(
            f"Mio-Mber | Speed: {player.velocity:.2f} | "
            f"FPS: {clock.get_fps():.0f} | "
            f"Sensors: [{sensor_str}] | Tab: Toggle Sensors"
        )

    pygame.quit()

if __name__ == "__main__":
    main()