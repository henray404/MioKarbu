"""
NEAT Trainer untuk Tabrak Bahlil
================================

Modular trainer untuk training AI dengan NEAT algorithm.
"""

import os
import sys
import pickle
import neat
import pygame
from typing import List, Tuple, Optional, Callable

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from core.motor import Motor


class NEATTrainer:
    """
    Trainer untuk NEAT evolution.
    
    Attributes:
        config_path: Path ke NEAT config
        track_path: Path ke track image
        generation: Generasi saat ini
    """
    
    def __init__(self, config_path: str, track_name: str = "mandalika",
                 screen_width: int = 1280, screen_height: int = 960,
                 map_width: int = 16512, map_height: int = 9216,
                 headless: bool = False, render_interval: int = 1):  # Sama dengan main.py (6x scale)
        """
        Inisialisasi trainer.
        
        Args:
            config_path: Path ke neat config file
            track_name: Nama track (tanpa .png)
            screen_width, screen_height: Ukuran window
            map_width, map_height: Ukuran map
            headless: Jika True, training tanpa visualisasi (lebih cepat)
            render_interval: Render setiap N frame (1=setiap frame, 10=setiap 10 frame)
        """
        self.config_path = config_path
        self.track_name = track_name
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        self.headless = headless
        self.render_interval = max(1, render_interval)  # Minimal 1
        
        # Track path
        self.track_path = os.path.join(BASE_DIR, "assets", "tracks", f"{track_name}.png")
        
        # Training state
        self.generation = 0
        self.best_fitness = 0
        self.winner_found = False
        
        # Pygame
        self.screen = None
        self.clock = None
        self.track_surface = None
        
        # Spawn config - dihitung berdasarkan rasio dari track original
        # Track original ~2752x1536, base spawn = 1745, 275
        # Rasio: x = 0.634, y = 0.179
        spawn_ratio_x = 0.634  # 1745 / 2752
        spawn_ratio_y = 0.179  # 275 / 1536
        self.spawn_x = int(map_width * spawn_ratio_x)
        self.spawn_y = int(map_height * spawn_ratio_y)
        self.spawn_angle = 0  # Hadap ke kanan (sama dengan player)
        
        # Win condition
        self.target_laps = 15
    
    def setup(self):
        """Initialize pygame dan load track"""
        if self.headless:
            # Set dummy video driver untuk headless mode
            # Ini memungkinkan convert_alpha() bisa dipanggil
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
        
        pygame.init()
        
        if self.headless:
            # Headless mode: buat dummy display agar convert_alpha() bisa jalan
            self.screen = pygame.display.set_mode((1, 1))
            print("[HEADLESS MODE] Training tanpa visualisasi - lebih cepat!")
        else:
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption("NEAT Training - Tabrak Bahlil")
            if self.render_interval > 1:
                print(f"[REDUCED RENDER] Render setiap {self.render_interval} frame")
        
        self.clock = pygame.time.Clock()
        
        # Load track
        self.track_surface = pygame.image.load(self.track_path)
        self.track_surface = pygame.transform.scale(
            self.track_surface, (self.map_width, self.map_height)
        )
        
        # Load AI masking untuk training (bukan masking.png biasa)
        ai_masking_path = os.path.join(BASE_DIR, "assets", "tracks", "ai_masking.png")
        self.masking_surface = None
        if os.path.exists(ai_masking_path):
            self.masking_surface = pygame.image.load(ai_masking_path)
            self.masking_surface = pygame.transform.scale(
                self.masking_surface, (self.map_width, self.map_height)
            )
            print(f"AI Masking loaded: {self.map_width}x{self.map_height}")
        else:
            print(f"WARNING: ai_masking.png not found, using track for collision")
        
        # Fonts (hanya jika tidak headless)
        if not self.headless:
            self.font_large = pygame.font.SysFont("Arial", 70)
            self.font_small = pygame.font.SysFont("Arial", 30)
        else:
            self.font_large = None
            self.font_small = None
    
    def eval_genomes(self, genomes, config):
        """
        Evaluate semua genome dalam satu generasi.
        Callback untuk NEAT.
        
        Args:
            genomes: List of (genome_id, genome) tuples
            config: NEAT config
        """
        self.generation += 1
        
        # Create cars dan networks
        cars: List[Motor] = []
        nets: List[neat.nn.FeedForwardNetwork] = []
        
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            genome.fitness = 0
            
            # Pakai Motor class (sama dengan player)
            car = Motor(self.spawn_x, self.spawn_y, color="pink")
            car.angle = self.spawn_angle  # 0 = hadap kanan
            car.start_angle = car.angle
            car.set_track_surface(self.track_surface)
            if self.masking_surface is not None:
                car.set_masking_surface(self.masking_surface)
            car.velocity = car.max_speed  # AI selalu jalan
            cars.append(car)
        
        # Camera
        camera_x, camera_y = 0, 0
        
        # Max time per generation (seconds)
        import time
        max_gen_time = 60  # 60 detik per generasi
        gen_start_time = time.time()
        best_lap_count = 0  # Track best lap untuk reset timer
        
        # Main loop
        running = True
        frame_count = 0
        while running:
            frame_count += 1
            
            # Check max time
            if time.time() - gen_start_time > max_gen_time:
                break
            
            # Event handling (hanya jika tidak headless)
            if not self.headless:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit(0)
            
            # Update cars
            alive_count = 0
            
            for i, (car, net, (genome_id, genome)) in enumerate(zip(cars, nets, genomes)):
                if not car.alive:
                    continue
                
                alive_count += 1
                
                # Get radar data
                radar_data = car.get_radar_data()
                
                # Neural network decision
                output = net.activate(radar_data)
                action = output.index(max(output))
                
                # Steer: 0=kiri, 1=lurus, 2=kanan (sama dengan player)
                if action == 0:
                    car.steer(1)  # Belok kiri
                elif action == 2:
                    car.steer(-1)  # Belok kanan
                # action == 1: lurus
                
                # Update car
                car.update()
                
                # Keep AI at max speed (setelah update untuk override slow zone)
                car.velocity = car.max_speed
                
                # Update fitness (sequential checkpoint system)
                # Prioritas: distance > checkpoint progress > lap
                
                fitness = car.distance_traveled  # Base fitness = jarak tempuh
                
                # Checkpoint bonus (sequential checkpoint lebih bernilai)
                # checkpoint_count = jumlah checkpoint yang sudah dilalui dalam urutan benar
                fitness += car.checkpoint_count * 200  # 200 per checkpoint (lebih bernilai karena sequential)
                
                # Lap bonus (besar - berhasil complete semua checkpoint)
                if car.lap_count > 0:
                    fitness += car.lap_count * 2000  # 2000 per lap
                
                # Kill car jika tidak mencapai checkpoint berikutnya dalam 60 detik
                max_time_between_checkpoints = 60 * 60  # 60 detik * 60 FPS
                time_since_last_checkpoint = car.time_spent - car.last_checkpoint_time
                if time_since_last_checkpoint > max_time_between_checkpoints:
                    car.alive = False
                    car.is_alive = False
                
                genome.fitness = fitness
                
                # Reset timer jika ada lap baru (reward for progress)
                if car.lap_count > best_lap_count:
                    best_lap_count = car.lap_count
                    gen_start_time = time.time()  # Reset timer!
                    print(f"[TIMER RESET] Lap {best_lap_count} completed! Timer reset to 60s")
                
                # Check win condition
                if car.lap_count >= self.target_laps:
                    self._handle_winner(genome, net, car, config)
                    return
            
            # All dead?
            if alive_count == 0:
                break
            
            # Update camera (follow best car by fitness)
            best_car = None
            best_fitness = -1
            for i, (car, net, (genome_id, genome)) in enumerate(zip(cars, nets, genomes)):
                if car.alive and genome.fitness > best_fitness:
                    best_fitness = genome.fitness
                    best_car = car
            
            if best_car:
                camera_x = int(best_car.x - self.screen_width / 2)
                camera_y = int(best_car.y - self.screen_height / 2)
                camera_x = max(0, min(camera_x, self.map_width - self.screen_width))
                camera_y = max(0, min(camera_y, self.map_height - self.screen_height))
            
            # Render (skip jika headless atau berdasarkan interval)
            if not self.headless and frame_count % self.render_interval == 0:
                self._render(cars, camera_x, camera_y, alive_count, len(cars))
                pygame.display.flip()
            
            self.clock.tick(0)  # Unlimited FPS untuk training cepat
    
    def _render(self, cars: List[Motor], camera_x: int, camera_y: int,
                alive: int, total: int):
        """Render frame"""
        # Draw track
        self.screen.blit(self.track_surface, (-camera_x, -camera_y))
        
        # Draw cars
        for car in cars:
            if car.alive:
                car.draw(self.screen, camera_x, camera_y)
        
        # Draw info
        text = self.font_large.render(f"Generation: {self.generation}", True, (255, 255, 0))
        rect = text.get_rect(center=(self.screen_width / 2, 100))
        self.screen.blit(text, rect)
        
        text = self.font_small.render(f"Alive: {alive}/{total}", True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen_width / 2, 200))
        self.screen.blit(text, rect)
        
        # Best lap info
        best_lap = max((car.lap_count for car in cars if car.alive), default=0)
        text = self.font_small.render(f"Best Lap: {best_lap}/{self.target_laps}", True, (0, 255, 0))
        rect = text.get_rect(center=(self.screen_width / 2, 240))
        self.screen.blit(text, rect)
        
        # pygame.display.flip() dipindah ke eval_genomes untuk kontrol render_interval
    
    def _handle_winner(self, genome, net, car: Motor, config):
        """Handle ketika ada winner"""
        self.winner_found = True
        
        print("\n" + "=" * 60)
        print("🏆 TRAINING BERHASIL! 🏆")
        print(f"Motor menyelesaikan {self.target_laps} lap!")
        print(f"Generation: {self.generation}")
        print(f"Total distance: {int(car.distance_traveled)}")
        print(f"Time: {car.time_spent} frames")
        print("=" * 60)
        
        # Save models
        models_dir = os.path.join(BASE_DIR, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        with open(os.path.join(models_dir, 'winner_genome.pkl'), 'wb') as f:
            pickle.dump(genome, f)
        with open(os.path.join(models_dir, 'winner_network.pkl'), 'wb') as f:
            pickle.dump(net, f)
        
        print(f"Model tersimpan di: {models_dir}")
    
    def run(self, generations: int = 50) -> Optional[neat.DefaultGenome]:
        """
        Run NEAT training.
        
        Args:
            generations: Max generations
            
        Returns:
            Best genome atau None
        """
        self.setup()
        
        # Load NEAT config
        config = neat.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.config_path
        )
        
        # Create population
        population = neat.Population(config)
        
        # Add reporters
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)
        
        # Add checkpointer
        checkpoint_dir = os.path.join(BASE_DIR, "neat_checkpoints")
        os.makedirs(checkpoint_dir, exist_ok=True)
        population.add_reporter(
            neat.Checkpointer(5, filename_prefix=f'{checkpoint_dir}/neat-checkpoint-')
        )
        
        # Run evolution
        winner = population.run(self.eval_genomes, generations)
        
        # Save best genome
        if winner and not self.winner_found:
            models_dir = os.path.join(BASE_DIR, "models")
            os.makedirs(models_dir, exist_ok=True)
            
            with open(os.path.join(models_dir, 'best_genome.pkl'), 'wb') as f:
                pickle.dump(winner, f)
            
            winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
            with open(os.path.join(models_dir, 'best_network.pkl'), 'wb') as f:
                pickle.dump(winner_net, f)
            
            print(f"\nBest genome saved to: {models_dir}")
        
        pygame.quit()
        return winner


def main():
    """Entry point untuk training"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Train AI Motor dengan NEAT")
    parser.add_argument('--generations', '-g', type=int, default=50,
                       help='Jumlah generasi (default: 50)')
    parser.add_argument('--track', '-t', type=str, default='mandalika',
                       help='Nama track (default: mandalika)')
    parser.add_argument('--laps', '-l', type=int, default=15,
                       help='Target lap untuk menang (default: 15)')
    
    args = parser.parse_args()
    
    # Config path
    config_path = os.path.join(BASE_DIR, "config.txt")
    
    if not os.path.exists(config_path):
        print(f"ERROR: Config tidak ditemukan: {config_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("  TABRAK BAHLIL - NEAT AI Training")
    print("=" * 60)
    print(f"Track       : {args.track}")
    print(f"Generations : {args.generations}")
    print(f"Target Laps : {args.laps}")
    print("=" * 60)
    
    trainer = NEATTrainer(
        config_path=config_path,
        track_name=args.track
    )
    trainer.target_laps = args.laps
    
    trainer.run(generations=args.generations)


if __name__ == "__main__":
    main()
