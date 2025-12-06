"""
Play dengan AI yang sudah di-training
=====================================

Cara pakai:
    python play_ai.py                           # Pakai model default
    python play_ai.py --model winner_genome.pkl # Pakai model tertentu
    python play_ai.py --track mandalika         # Pilih track
"""

import os
import sys
import pickle
import neat
import pygame

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from core.ai_car import AICar


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
    
    parser = argparse.ArgumentParser(description="Play dengan AI Motor")
    
    parser.add_argument(
        '--model', '-m',
        type=str,
        default='winner_genome.pkl',
        help='Nama file model (default: winner_genome.pkl)'
    )
    
    parser.add_argument(
        '--track', '-t',
        type=str,
        default='mandalika',
        help='Nama track (default: mandalika)'
    )
    
    args = parser.parse_args()
    
    # Paths
    config_path = os.path.join(BASE_DIR, "config.txt")
    
    # Cek model di beberapa lokasi
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
    
    print("=" * 50)
    print("  TABRAK BAHLIL - AI Demo")
    print("=" * 50)
    print(f"Model: {model_path}")
    print(f"Track: {args.track}")
    print("=" * 50)
    print()
    print("Controls:")
    print("  R     - Reset posisi")
    print("  ESC   - Quit")
    print()
    
    # Initialize pygame
    pygame.init()
    screen_width, screen_height = 1024, 768
    map_width, map_height = 1920, 1440
    
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tabrak Bahlil - AI Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)
    
    # Load track
    track_path = os.path.join(BASE_DIR, "assets", "tracks", f"{args.track}.png")
    if not os.path.exists(track_path):
        print(f"ERROR: Track tidak ditemukan: {track_path}")
        sys.exit(1)
    
    track_surface = pygame.image.load(track_path)
    track_surface = pygame.transform.scale(track_surface, (map_width, map_height))
    
    # Load AI
    net, genome, config = load_ai(model_path, config_path)
    fitness = getattr(genome, 'fitness', 0) or 0
    print(f"AI loaded! Fitness: {fitness:.2f}")
    
    # Create car
    spawn_x, spawn_y = 600, 240
    car = AICar(spawn_x, spawn_y)
    
    # Camera
    camera_x, camera_y = 0, 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    car.reset()
                    print("🔄 Reset!")
        
        # AI Decision
        if car.is_alive:
            radar_data = car.get_radar_data()
            output = net.activate(radar_data)
            action = output.index(max(output))
            
            if action == 0:
                car.steer(1)  # Kiri
            elif action == 2:
                car.steer(-1)  # Kanan
            
            car.update(track_surface)
        
        # Update camera
        camera_x = int(car.pos[0] - screen_width / 2)
        camera_y = int(car.pos[1] - screen_height / 2)
        camera_x = max(0, min(camera_x, map_width - screen_width))
        camera_y = max(0, min(camera_y, map_height - screen_height))
        
        # Render
        screen.blit(track_surface, (-camera_x, -camera_y))
        car.draw(screen, camera_x, camera_y)
        
        # Draw info
        info_lines = [
            f"Lap: {car.lap_count}",
            f"Distance: {car.distance:.0f}",
            f"Alive: {'Yes' if car.is_alive else 'No (Press R)'}",
            f"Fitness: {fitness:.1f}",
            "",
            "R=Reset  ESC=Quit"
        ]
        
        y = 10
        for line in info_lines:
            text = font.render(line, True, (255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 0), 
                           (5, y - 2, text.get_width() + 10, text.get_height() + 4))
            screen.blit(text, (10, y))
            y += 35
        
        pygame.display.flip()
    
    pygame.quit()
    print("Bye! 👋")


if __name__ == "__main__":
    main()
