"""
Mio Karbu - Player vs AI Mode
=============================

Main bareng AI! Player pakai WASD, AI otomatis.
Semua konfigurasi diambil dari config/game_config.py
"""

import os
import sys
import pickle
import neat
import pygame
import random
from typing import List

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, os.path.join(BASE_DIR, "config"))

# Import modules
from core.game_manager import GameManager, GameConfig
from core.display_manager import DisplayManager
from screens.main_menu import MainMenuScreen
import game_config as cfg


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
    return net


def find_model(base_dir: str, model_name: str) -> str:
    """Cari file model di berbagai lokasi"""
    possible_paths = [
        os.path.join(base_dir, "models", model_name),
        os.path.join(base_dir, model_name),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    raise FileNotFoundError(f"Model tidak ditemukan: {possible_paths}")


def main():
    # ===== CONFIG =====
    # Semua setting dari game_config.py
    game_cfg = GameConfig(
        track_name=cfg.TRACK_NAME,
        track_scale=cfg.TRACK_SCALE,
        original_track_width=cfg.ORIGINAL_TRACK_WIDTH,
        original_track_height=cfg.ORIGINAL_TRACK_HEIGHT,
        spawn_x=cfg.SPAWN_X,
        spawn_y=cfg.SPAWN_Y,
        spawn_angle=cfg.SPAWN_ANGLE,
        finish_x=cfg.FINISH_X,
        finish_y=cfg.FINISH_Y,
        masking_file=cfg.MASKING_FILE,
        masking_subfolder=cfg.MASKING_SUBFOLDER,
        fullscreen=cfg.FULLSCREEN,
    )
    
    model_name = cfg.DEFAULT_MODEL
    ai_count = cfg.DEFAULT_AI_COUNT
    target_laps = cfg.DEFAULT_TARGET_LAPS
    
    # ===== PATHS =====
    config_path = os.path.join(BASE_DIR, "config.txt")
    
    try:
        model_path = find_model(BASE_DIR, model_name)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        print("\nPastikan sudah menjalankan training dulu!")
        sys.exit(1)
    
    # ===== PRINT INFO =====
    print("=" * 55)
    print("  MIO KARBU - Player vs AI")
    print("=" * 55)
    print(f"Track      : {game_cfg.track_name}")
    print(f"AI Model   : {model_path}")
    print(f"AI Count   : {ai_count}")
    print(f"Target Lap : {target_laps}")
    print("=" * 55)
    print()
    print("Controls:")
    print("  W/S   - Maju/Mundur")
    print("  A/D   - Belok Kiri/Kanan")
    print("  R     - Reset")
    print("  ESC   - Quit")
    print()
    
    # ===== SETUP GAME =====
    game = GameManager(BASE_DIR, game_cfg)
    display = DisplayManager(fullscreen=game_cfg.fullscreen)
    
    # Initialize display
    display.init(title="Mio Karbu")
    
    # Load assets
    game.load_track()
    game.load_masking()
    
    # ===== CREATE ENTITIES =====
    spawn_x, spawn_y = game.get_spawn_position()
    
    # Player
    player = game.create_motor(spawn_x, spawn_y, color="pink", invincible=True)
    
    # AI Cars
    ai_cars = []
    ai_nets = []
    
    for i in range(ai_count):
        # Grid formation: 2 kolom
        col = i % 2           # Kolom 0 atau 1
        row = (i // 2) + 1    # Baris mulai dari 1 (player di baris 0)
        offset_x = 100 * col  # Jarak antar kolom
        offset_y = 80 * row   # Jarak antar baris
        ai_car = game.create_motor(spawn_x + offset_x, spawn_y + offset_y, color="pink", invincible=True)
        ai_car.velocity = 0
        
        net = load_ai(model_path, config_path)
        
        ai_cars.append(ai_car)
        ai_nets.append(net)
    
    # ===== GAME STATE =====
    winner = None
    game_over = False
    countdown_timer = 3 * 60  # 3 seconds at 60 FPS
    countdown_active = True
    race_started = False
    
    # ===== MAIN MENU =====
    ui_dir = os.path.join(BASE_DIR, "assets", "ui")
    menu_screen = MainMenuScreen(None, (display.width, display.height), ui_dir)
    
    in_menu = True
    while in_menu:
        display.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                display.quit()
                sys.exit()
            menu_screen.handle_event(event)
        
        if menu_screen.result == "PLAY":
            in_menu = False
        elif menu_screen.result == "EXIT":
            display.quit()
            sys.exit()
        
        menu_screen.draw(display.screen)
        pygame.display.flip()
    
    # ===== GAME LOOP =====
    running = True
    while running:
        # --- EVENTS ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset
                    player.reset()
                    player.angle = 0
                    for ai_car in ai_cars:
                        ai_car.reset()
                        ai_car.angle = 0
                        ai_car.velocity = 0
                    winner = None
                    game_over = False
                    countdown_timer = 3 * 60
                    countdown_active = True
                    race_started = False
                    print("\n[GAME] Reset!")
        
        # --- COUNTDOWN ---
        if countdown_active:
            countdown_timer -= 1
            if countdown_timer <= 0:
                countdown_active = False
                race_started = True
                # Set AI velocity kecil (bukan 0, biar radar bisa baca)
                for ai_car in ai_cars:
                    ai_car.velocity = 7  # Kecil, AI tetap harus accelerate
                print("[GAME] GO!")
        
        # --- UPDATE ---
        if not game_over and race_started:
            # Player
            keys = pygame.key.get_pressed()
            if player.alive:
                player.handle_input(keys)
                player.update()
                
                if player.lap_count >= target_laps:
                    player.velocity = 0  # Stop!
                    winner = "PLAYER"
                    game_over = True
                    print("\n[GAME] PLAYER WINS!")
            
            # AI
            for i, (ai_car, net) in enumerate(zip(ai_cars, ai_nets)):
                if not ai_car.alive:
                    continue
                
                radar_data = ai_car.get_radar_data()
                output = net.activate(radar_data)
                
                steering = max(-1, min(1, output[0]))
                throttle = max(0.3, min(1, output[1]))
                
                # Tambahkan random noise untuk variasi (beda tiap AI)
                noise = random.uniform(-0.2, 0.2)
                steering = max(-1, min(1, steering + noise))
                
                ai_car.set_ai_input(steering, throttle)
                ai_car.update()
                
                if ai_car.lap_count >= target_laps:
                    ai_car.velocity = 0  # Stop!
                    winner = f"AI-{i+1}"
                    game_over = True
                    print(f"\n[GAME] AI-{i+1} WINS!")
        
        # --- CAMERA ---
        if player.alive:
            display.update_camera(player.x, player.y, game.map_width, game.map_height)
        else:
            for ai_car in ai_cars:
                if ai_car.alive:
                    display.update_camera(ai_car.x, ai_car.y, game.map_width, game.map_height)
                    break
        
        # --- RENDER ---
        display.render_track(game.track_surface)
        
        # AI cars
        for ai_car in ai_cars:
            if ai_car.alive:
                display.render_motor(ai_car)
        
        # Player
        if player.alive:
            display.render_motor(player)
        
        # Countdown
        if countdown_active:
            countdown_seconds = (countdown_timer // 60) + 1
            display.render_countdown(countdown_seconds)
        elif race_started and countdown_timer > -30:
            display.render_go()
            countdown_timer -= 1
        
        # UI - Lap counter
        display.render_lap_counter(player.lap_count, target_laps)
        
        # UI - Speedometer
        speed_kmh = player.get_speed_kmh()
        display.render_speedometer(speed_kmh)
        
        # UI - Winner
        if game_over and winner:
            display.render_winner(winner)
        
        # --- FLIP ---
        display.tick(60)
    
    display.quit()


if __name__ == "__main__":
    main()