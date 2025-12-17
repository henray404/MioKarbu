"""
Mio Karbu - Player vs AI Mode (Final Fix)
=========================================
"""

import os
import sys
import pickle
import neat
import pygame
import random
import wave

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, os.path.join(BASE_DIR, "config"))

# Import modules
from core.game_manager import GameManager, GameConfig
from core.display_manager import DisplayManager
from screens.main_menu import MainMenuScreen
from screens.pick_map import PickMapScreen
from ui.hud import GameHUD
from ui.components import PausePopup
import game_config as cfg


def load_ai(model_path, config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, 
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    with open(model_path, 'rb') as f: genome = pickle.load(f)
    return neat.nn.FeedForwardNetwork.create(genome, config)

def find_model(base_dir, model_name):
    paths = [os.path.join(base_dir, "models", model_name), os.path.join(base_dir, model_name)]
    for p in paths:
        if os.path.exists(p): return p
    raise FileNotFoundError(f"Model {model_name} not found.")

def split_wav_audio(filepath, split_sec):
    try:
        if not os.path.exists(filepath):
            # print(f"[WARN] Audio file not found: {filepath}")
            dummy = pygame.mixer.Sound(buffer=bytearray(10))
            return dummy, dummy

        with wave.open(filepath, 'rb') as w:
            params = w.getparams()
            split_frame = int(split_sec * params.framerate)
            all_frames = w.readframes(params.nframes)
            width = params.sampwidth * params.nchannels
            split_byte = split_frame * width
            
            raw_rev = all_frames[:split_byte]
            raw_gas = all_frames[split_byte:]
            
            rev_snd = pygame.mixer.Sound(buffer=raw_rev)
            gas_snd = pygame.mixer.Sound(buffer=raw_gas)
            
            return rev_snd, gas_snd
    except Exception as e:
        print(f"[ERROR] Failed to split audio: {e}")
        dummy = pygame.mixer.Sound(buffer=bytearray(10))
        return dummy, dummy

def load_sound_safe(filepath):
    if os.path.exists(filepath): return pygame.mixer.Sound(filepath)
    return None

def main():
    # ===== CONFIG =====
    # Pilih spawn/finish berdasarkan track
    if cfg.TRACK_NAME == "new-4":
        spawn_x, spawn_y = cfg.SPAWN_X, cfg.SPAWN_Y
        finish_start_x = cfg.FINISH_LINE_START_X
        finish_start_y = cfg.FINISH_LINE_START_Y
        finish_end_x = cfg.FINISH_LINE_END_X
        finish_end_y = cfg.FINISH_LINE_END_Y
    elif cfg.TRACK_NAME == "map-2":
        spawn_x, spawn_y = cfg.SPAWN_X_2, cfg.SPAWN_Y_2
        finish_start_x = cfg.FINISH_LINE_START_X_2
        finish_start_y = cfg.FINISH_LINE_START_Y_2
        finish_end_x = cfg.FINISH_LINE_END_X_2
        finish_end_y = cfg.FINISH_LINE_END_Y_2
    else:
        # Default ke SPAWN_X/Y untuk track lainnya
        spawn_x, spawn_y = cfg.SPAWN_X, cfg.SPAWN_Y
        finish_start_x = cfg.FINISH_LINE_START_X
        finish_start_y = cfg.FINISH_LINE_START_Y
        finish_end_x = cfg.FINISH_LINE_END_X
        finish_end_y = cfg.FINISH_LINE_END_Y
    # 1. Setup Display & Audio
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.init()
    
    display = DisplayManager(fullscreen=cfg.FULLSCREEN)
    display.init(title="Mio Karbu Racing")
    ui_dir = os.path.join(BASE_DIR, "assets")
    
    # --- LOAD AUDIO ---
    path_motor = os.path.join(BASE_DIR, "assets", "audio", "motor.wav")
    snd_countdown_rev, snd_gas = split_wav_audio(path_motor, 4.0)
    
    # Volume rendah agar tidak berisik
    snd_countdown_rev.set_volume(0.2) 
    snd_gas.set_volume(0.1)           
    
    path_idle = os.path.join(BASE_DIR, "assets", "audio", "rev.mp3")
    snd_idle = load_sound_safe(path_idle)
    if snd_idle: snd_idle.set_volume(0.15)
    
    # =========================================================================
    # PHASE 1: MAIN MENU
    # =========================================================================
    menu = MainMenuScreen(None, (display.width, display.height), ui_dir)
    while menu.result is None:
        display.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: display.quit(); sys.exit()
            menu.handle_event(event)
        menu.draw(display.screen)
        pygame.display.flip()
        
    if menu.result == "EXIT": display.quit(); sys.exit()

    # =========================================================================
    # PHASE 2: PICK MAP
    # =========================================================================
    picker = PickMapScreen(None, (display.width, display.height), ui_dir)
    while not picker.finished:
        display.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: display.quit(); sys.exit()
            picker.handle_event(event)
        picker.draw(display.screen)
        pygame.display.flip()

    selected_map_key = picker.selected_map or cfg.DEFAULT_MAP_KEY

    # =========================================================================
    # PHASE 3: CONFIGURE GAME
    # =========================================================================
    # Ambil data map dari Config berdasarkan pilihan user
    if selected_map_key in cfg.MAP_SETTINGS:
        map_data = cfg.MAP_SETTINGS[selected_map_key]
    else:
        map_data = cfg.MAP_SETTINGS[cfg.DEFAULT_MAP_KEY]

    game_cfg = GameConfig(
        track_name=map_data["track_file"],
        track_scale=cfg.TRACK_SCALE,
        original_track_width=cfg.ORIGINAL_TRACK_WIDTH,
        original_track_height=cfg.ORIGINAL_TRACK_HEIGHT,
        
        spawn_x=map_data["spawn_x"],
        spawn_y=map_data["spawn_y"],
        spawn_angle=map_data["spawn_angle"],
        
        # [FIX] Gunakan parameter baru, HAPUS finish_x/finish_y lama
        finish_line_start_x=map_data.get("finish_line_start_x", 0),
        finish_line_start_y=map_data.get("finish_line_start_y", 0),
        finish_line_end_x=map_data.get("finish_line_end_x", 0),
        finish_line_end_y=map_data.get("finish_line_end_y", 0),
        
        masking_file=map_data["masking_file"],
        masking_subfolder=cfg.MASKING_SUBFOLDER,
        fullscreen=cfg.FULLSCREEN
    )

    # Init Resources
    model_path = find_model(BASE_DIR, cfg.DEFAULT_MODEL)
    config_path = os.path.join(BASE_DIR, "config.txt")
    
    game = GameManager(BASE_DIR, game_cfg)
    game.load_track()
    game.load_masking()
    hud = GameHUD((display.width, display.height))
    pause_popup = PausePopup((display.width, display.height))

    # =========================================================================
    # PHASE 4: SPAWN ENTITIES
    # =========================================================================
    # Gunakan spawn dari map_data yang sudah dipilih
    sx, sy = cfg.get_spawn_position(
        game.map_width, 
        game.map_height, 
        map_data["spawn_x"], 
        map_data["spawn_y"]
    )
    s_angle = map_data["spawn_angle"]

    # Player
    player = game.create_motor(sx, sy, "pink", invincible=True)
    player.angle = s_angle
    player.configure_sounds(gas_sound=snd_gas, idle_sound=snd_idle)
    player.start_engine()

    # AI
    ai_cars = []
    ai_nets = []
    colors = ["blue", "purple", "yellow"]
    
    for i in range(cfg.DEFAULT_AI_COUNT):
        col = i % 2
        row = (i // 2) + 1
        offset_x = 100 * col
        offset_y = 80 * row
        c_name = colors[i % len(colors)]
        
        ai = game.create_motor(sx - offset_x, sy + offset_y, c_name, invincible=True)
        ai.angle = s_angle
        ai.velocity = 0
        net = load_ai(model_path, config_path)
        ai_cars.append(ai)
        ai_nets.append(net)

    all_racers = [player] + ai_cars
    
    # Game State
    running = True
    is_paused = False
    game_over = False
    winner = None
    countdown = 180 
    rev_played = False
    race_started = False

    # =========================================================================
    # PHASE 5: GAME LOOP
    # =========================================================================
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            
            if is_paused:
                if pause_popup.handle_event(event):
                    act = pause_popup.action
                    if act == "RESUME": is_paused = False
                    elif act == "EXIT": running = False
                    elif act == "RETRY":
                        is_paused = False
                        game_over = False
                        winner = None
                        race_started = False
                        countdown = 180
                        rev_played = False
                        
                        snd_countdown_rev.stop()
                        
                        player.reset(sx, sy, s_angle)
                        for i, ai in enumerate(ai_cars):
                            col = i % 2; row = (i // 2) + 1
                            ai.reset(sx - (100*col), sy + (80*row), s_angle)
                            ai.velocity = 0
                continue 

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    is_paused = not is_paused
                    pause_popup.is_visible = is_paused
                    pause_popup.action = None

        if not is_paused:
            # --- COUNTDOWN ---
            if countdown > 0:
                if not rev_played:
                    snd_countdown_rev.play()
                    rev_played = True
                countdown -= 1
                if countdown <= 0:
                    race_started = True
                    for ai in ai_cars: ai.velocity = 7
            
            if race_started and not game_over:
                # Player
                if player.alive:
                    player.handle_input(pygame.key.get_pressed())
                    player.update() 
                    if player.lap_count >= cfg.DEFAULT_TARGET_LAPS:
                        player.lap_count = cfg.DEFAULT_TARGET_LAPS
                        player.velocity = 0
                        player.stop_all_sounds() 
                        winner = "YOU"
                        game_over = True
                
                # AI
                for ai, net in zip(ai_cars, ai_nets):
                    if ai.alive:
                        out = net.activate(ai.get_radar_data())
                        steering = max(-1, min(1, out[0] + random.uniform(-0.1, 0.1)))
                        throttle = max(0.3, min(1, out[1]))
                        ai.set_ai_input(steering, throttle)
                        ai.update()
                        if ai.lap_count >= cfg.DEFAULT_TARGET_LAPS:
                            ai.lap_count = cfg.DEFAULT_TARGET_LAPS
                            ai.velocity = 0
                            winner = f"AI ({ai.color.upper()})"
                            game_over = True

        # Render
        target = player if player.alive else (ai_cars[0] if ai_cars and ai_cars[0].alive else player)
        if not is_paused: display.update_camera(target.x, target.y, game.map_width, game.map_height)
        
        display.render_track(game.track_surface)
        for ai in ai_cars: 
            if ai.alive: display.render_motor(ai)
        if player.alive: display.render_motor(player)
        
        if countdown > 0: display.render_countdown((countdown // 60) + 1)
        elif race_started and countdown > -60: display.render_go(); countdown -= 1 if not is_paused else 0
            
        hud.render_leaderboard(display.screen, all_racers)
        hud.render_lap_counter(display.screen, player.lap_count, cfg.DEFAULT_TARGET_LAPS)
        hud.render_speedometer(display.screen, player.get_speed_kmh())
        
        if game_over and winner: hud.render_game_over(display.screen, winner)
        if is_paused: pause_popup.draw(display.screen)
        
        display.tick(60)

    display.quit()

if __name__ == "__main__":
    main()