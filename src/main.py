"""
Tabrak Bahlil - Player vs AI Mode
=================================

Main bareng AI! Player pakai WASD, AI otomatis.

Cara pakai:
    python main.py                           # Default model & track
    python main.py --model winner_genome.pkl # Pilih model AI
    python main.py --track mandalika         # Pilih track
    python main.py --ai-count 3              # Jumlah AI opponent
"""

import os
import sys
import math
import pickle
import neat
import pygame
from typing import List, Optional
from screens.main_menu import MainMenuScreen

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, os.path.join(BASE_DIR, "screens"))


from core.motor import Motor

# Constants
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
UI_DIR = os.path.join(BASE_DIR, "assets", "ui")

def load_ai(model_path: str, config_path: str):
    """Load trained genome dan buat neural network"""
    config = neat.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    
    with open(model_path, 'rb') as f:
        genome = pickle.load(f)
    
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    return net, genome, config


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Mio Karbu - Player vs AI")
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='winner_genome.pkl',
        help='Nama file model AI (default: winner_genome.pkl)'
    )
    
    parser.add_argument(
        '--track', '-t',
        type=str,
        default='new',
        help='Nama track (default: mandalika)'
    )
    
    parser.add_argument(
        '--ai-count', '-n',
        type=int,
        default=1,
        help='Jumlah AI opponent (default: 1)'
    )
    
    parser.add_argument(
        '--target-laps', '-l',
        type=int,
        default=3,
        help='Target lap untuk menang (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Paths
    config_path = os.path.join(BASE_DIR, "config.txt")
    track_path = os.path.join(ASSETS_DIR, "tracks", f"{args.track}.png")
    
    # Find model
    possible_paths = [
        os.path.join(BASE_DIR, "models", args.model),
        os.path.join(BASE_DIR, args.model),
    ]
    
    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break
    
    if model_path is None:
        print(f"ERROR: Model tidak ditemukan!")
        print(f"Coba lokasi: {possible_paths}")
        print("\nPastikan sudah menjalankan training dulu!")
        sys.exit(1)
    
    print("=" * 55)
    print("  TABRAK BAHLIL - Player vs AI")
    print("=" * 55)
    print(f"Track      : {args.track}")
    print(f"AI Model   : {model_path}")
    print(f"AI Count   : {args.ai_count}")
    print(f"Target Lap : {args.target_laps}")
    print("=" * 55)
    print()
    print("Controls:")
    print("  W/S   - Maju/Mundur")
    print("  A/D   - Belok Kiri/Kanan")
    print("  R     - Reset")
    print("  ESC   - Quit")
    print()
    
    # Initialize pygame
    pygame.init()
    screen_width, screen_height = 1280, 960
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Mio Karbu")
    clock = pygame.time.Clock()
    
    # Load track dan get actual size
    track_surface = pygame.image.load(track_path)
    
    # Scale track (perbesar)
    track_scale = 6.0  # Ubah nilai ini untuk scale yang berbeda
    original_width, original_height = track_surface.get_size()
    track_surface = pygame.transform.scale(
        track_surface, 
        (int(original_width * track_scale), int(original_height * track_scale))
    )
    
    map_width, map_height = track_surface.get_size()
    print(f"Map Size   : {map_width}x{map_height} (scaled {track_scale}x)")
    
    # Load masking untuk collision detection
    masking_path = os.path.join(ASSETS_DIR, "tracks", "masking.png")
    masking_surface = None
    if os.path.exists(masking_path):
        masking_surface = pygame.image.load(masking_path)
        masking_surface = pygame.transform.scale(
            masking_surface,
            (int(masking_surface.get_width() * track_scale), 
             int(masking_surface.get_height() * track_scale))
        )
        print(f"Masking    : Loaded ({masking_surface.get_width()}x{masking_surface.get_height()})")
    else:
        print(f"Masking    : Not found, using track for collision")
    
    # Load AI masking (terpisah untuk AI)
    ai_masking_path = os.path.join(ASSETS_DIR, "tracks", "ai_masking.png")
    ai_masking_surface = None
    if os.path.exists(ai_masking_path):
        ai_masking_surface = pygame.image.load(ai_masking_path)
        ai_masking_surface = pygame.transform.scale(
            ai_masking_surface,
            (int(ai_masking_surface.get_width() * track_scale), 
             int(ai_masking_surface.get_height() * track_scale))
        )
        print(f"AI Masking : Loaded ({ai_masking_surface.get_width()}x{ai_masking_surface.get_height()})")
    else:
        # Fallback ke masking biasa jika ai_masking tidak ada
        ai_masking_surface = masking_surface
        print(f"AI Masking : Using player masking (ai_masking.png not found)")
    
    # Font
    font_large = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 32)
    
    # Spawn positions (di-scale sesuai track)
    # Base position pada track original
    base_spawn_x, base_spawn_y = 1745, 275
    spawn_x = int(base_spawn_x * track_scale)
    spawn_y = int(base_spawn_y * track_scale)
    spawn_angle = 0  # Hadap ke kanan (0°)
    
    # Create player (spawn di depan)
    player = Motor(spawn_x, spawn_y, color="pink")
    player.angle = 0  # 0 radians = menghadap kanan (0°)
    player.start_angle = player.angle
    player.set_track_surface(track_surface)  # Untuk visual reference
    if masking_surface is not None:
        player.set_masking_surface(masking_surface)  # Untuk collision
    player.invincible = True  # Player tidak bisa mati
    
    # Create AI opponents (spawn di samping player)
    ai_cars: List[Motor] = []
    ai_nets: List[neat.nn.FeedForwardNetwork] = []
    
    for i in range(args.ai_count):
        # Spawn AI di samping player (sejajar, bukan di belakang)
        offset_x = 0  # Sejajar dengan player
        offset_y = 80 * (i + 1)  # Di bawah player
        
        # Create AI Motor (same class as player, different color)
        ai_car = Motor(spawn_x + offset_x, spawn_y + offset_y, color="pink")
        # AI menghadap kanan (0°) - sama dengan player
        ai_car.angle = 0
        ai_car.start_angle = ai_car.angle
        ai_car.set_track_surface(track_surface)
        if ai_masking_surface is not None:
            ai_car.set_masking_surface(ai_masking_surface)  # Pakai AI masking
        ai_car.invincible = True  # AI juga invincible biar tidak mati
        ai_car.velocity = 0  # Start diam dulu, nanti jalan setelah countdown
        
        net, _, _ = load_ai(model_path, config_path)
        
        ai_cars.append(ai_car)
        ai_nets.append(net)
    
    # Camera
    camera_x, camera_y = 0, 0
    
    # Game state
    winner = None
    game_over = False
    
    # Countdown state
    countdown_timer = 3 * 60  # 3 seconds at 60 FPS
    countdown_active = True
    race_started = False
    
    menu_screen = MainMenuScreen(None, (screen_width, screen_height), UI_DIR)
    
    in_menu = True
    while in_menu:
        dt = clock.tick(60) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Lempar event ke menu
            menu_screen.handle_event(event)
        
        # Cek hasil pilihan menu
        if menu_screen.result == "PLAY":
            in_menu = False # Keluar dari loop menu, LANJUT ke game
        elif menu_screen.result == "EXIT":
            pygame.quit()
            sys.exit()
            
        menu_screen.draw(screen)
        pygame.display.flip()

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset semua
                    player.reset()
                    player.angle = 0  # Reset to facing right
                    for ai_car in ai_cars:
                        ai_car.reset()
                        ai_car.angle = 0  # Reset AI to facing right
                        ai_car.velocity = 0
                    winner = None
                    game_over = False
                    countdown_timer = 3 * 60  # Reset countdown
                    countdown_active = True
                    race_started = False
                    print("\n[GAME] Reset!")
        
        # Countdown logic
        if countdown_active:
            countdown_timer -= 1
            if countdown_timer <= 0:
                countdown_active = False
                race_started = True
                print("[GAME] GO!")
        
        if not game_over and race_started:
            # Update player
            keys = pygame.key.get_pressed()
            if player.alive:
                player.handle_input(keys)
                player.update()  # Uses self.track_surface internally
                
                # Check win
                if player.lap_count >= args.target_laps:
                    winner = "PLAYER"
                    game_over = True
                    print(f"\n[GAME] PLAYER WINS!")
            
            # Update AI
            for i, (ai_car, net) in enumerate(zip(ai_cars, ai_nets)):
                if not ai_car.alive:
                    continue
                
                # Keep AI at constant speed
                ai_car.velocity = ai_car.max_speed
                
                # Get radar dan neural network decision
                radar_data = ai_car.get_radar_data()
                output = net.activate(radar_data)
                action = output.index(max(output))
                
                # Steer (original direction)
                if action == 0:
                    ai_car.steer(1)
                elif action == 2:
                    ai_car.steer(-1)
                
                ai_car.update()  # Motor.update() uses internal track_surface
                
                # Check win
                if ai_car.lap_count >= args.target_laps:
                    winner = f"AI-{i+1}"
                    game_over = True
                    print(f"\n[GAME] AI-{i+1} WINS!")
        
        # Camera follow player
        if player.alive:
            camera_x = int(player.x - screen_width / 2)
            camera_y = int(player.y - screen_height / 2)
        else:
            # Follow first alive AI
            for ai_car in ai_cars:
                if ai_car.alive:
                    camera_x = int(ai_car.x - screen_width / 2)
                    camera_y = int(ai_car.y - screen_height / 2)
                    break
        
        # Clamp camera
        camera_x = max(0, min(camera_x, map_width - screen_width))
        camera_y = max(0, min(camera_y, map_height - screen_height))
        
        # Render
        screen.blit(track_surface, (-camera_x, -camera_y))
        
        # Draw AI cars
        for ai_car in ai_cars:
            if ai_car.alive:
                ai_car.draw(screen, camera_x, camera_y)
        
        # Draw player
        if player.alive:
            player.draw(screen, camera_x, camera_y)
        
        # Draw countdown if active
        if countdown_active or (not race_started):
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))
            
            # Countdown number
            countdown_seconds = (countdown_timer // 60) + 1
            if countdown_seconds > 0:
                countdown_text = str(countdown_seconds)
                font_countdown = pygame.font.Font(None, 200)
                text_surface = font_countdown.render(countdown_text, True, (255, 255, 0))
                text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
                screen.blit(text_surface, text_rect)
        
        # "GO!" flash for first 30 frames after race starts
        elif race_started and countdown_timer > -30:
            font_go = pygame.font.Font(None, 200)
            go_surface = font_go.render("GO!", True, (0, 255, 0))
            go_rect = go_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(go_surface, go_rect)
            countdown_timer -= 1
        
        # UI - Background
        pygame.draw.rect(screen, (0, 0, 0, 180), (10, 10, 250, 150))
        
        # UI - Player info
        color_player = (0, 255, 0) if player.alive else (255, 0, 0)
        status = "ALIVE" if player.alive else "DEAD"
        text = font_small.render(f"PLAYER [{status}]", True, color_player)
        screen.blit(text, (20, 20))
        text = font_small.render(f"  Lap: {player.lap_count}/{args.target_laps}", True, (255, 255, 255))
        screen.blit(text, (20, 50))
        
        # UI - AI info
        y_offset = 90
        for i, ai_car in enumerate(ai_cars):
            color_ai = (255, 165, 0) if ai_car.alive else (100, 100, 100)
            status = "ALIVE" if ai_car.alive else "DEAD"
            text = font_small.render(f"AI-{i+1} [{status}]", True, color_ai)
            screen.blit(text, (20, y_offset))
            text = font_small.render(f"  Lap: {ai_car.lap_count}/{args.target_laps}", True, (255, 255, 255))
            screen.blit(text, (20, y_offset + 25))
            y_offset += 60
        
        # UI - Winner announcement
        if game_over and winner:
            # Semi-transparent overlay
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            # Winner text
            win_color = (0, 255, 0) if winner == "PLAYER" else (255, 165, 0)
            text = font_large.render(f"{winner} WINS!", True, win_color)
            rect = text.get_rect(center=(screen_width / 2, screen_height / 2 - 30))
            screen.blit(text, rect)
            
            text = font_small.render("Press R to restart, ESC to quit", True, (255, 255, 255))
            rect = text.get_rect(center=(screen_width / 2, screen_height / 2 + 30))
            screen.blit(text, rect)
        
        # UI - Speedometer (bottom right)
        speed_kmh = player.get_speed_kmh()
        max_display_speed = 180  # Max display speed for the bar
        
        # Speedometer background
        speedo_width, speedo_height = 200, 60
        speedo_x = screen_width - speedo_width - 20
        speedo_y = screen_height - speedo_height - 60
        
        # Draw background panel
        speedo_bg = pygame.Surface((speedo_width, speedo_height), pygame.SRCALPHA)
        speedo_bg.fill((0, 0, 0, 180))
        screen.blit(speedo_bg, (speedo_x, speedo_y))
        
        # Draw speed bar
        bar_width = int((speed_kmh / max_display_speed) * (speedo_width - 20))
        bar_width = min(bar_width, speedo_width - 20)  # Cap at max
        
        # Color gradient: green -> yellow -> red
        speed_ratio = min(speed_kmh / max_display_speed, 1.0)
        if speed_ratio < 0.5:
            bar_color = (int(speed_ratio * 2 * 255), 255, 0)  # Green to Yellow
        else:
            bar_color = (255, int((1 - speed_ratio) * 2 * 255), 0)  # Yellow to Red
        
        pygame.draw.rect(screen, bar_color, (speedo_x + 10, speedo_y + 35, bar_width, 15))
        pygame.draw.rect(screen, (255, 255, 255), (speedo_x + 10, speedo_y + 35, speedo_width - 20, 15), 1)
        
        # Draw speed text
        speed_text = font_large.render(f"{speed_kmh}", True, (255, 255, 255))
        screen.blit(speed_text, (speedo_x + 15, speedo_y + 2))
        
        kmh_text = font_small.render("km/h", True, (180, 180, 180))
        screen.blit(kmh_text, (speedo_x + 75, speedo_y + 12))
        
        # Controls hint
        text = font_small.render("WASD: Move | R: Reset | ESC: Quit", True, (200, 200, 200))
        screen.blit(text, (screen_width - 350, screen_height - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()