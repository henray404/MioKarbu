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

from core.ai_car import AICar


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
                 map_width: int = 4096, map_height: int = 3072):
        """
        Inisialisasi trainer.
        
        Args:
            config_path: Path ke neat config file
            track_name: Nama track (tanpa .png)
            screen_width, screen_height: Ukuran window
            map_width, map_height: Ukuran map
        """
        self.config_path = config_path
        self.track_name = track_name
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height
        
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
        
        # Spawn config (untuk mandalika 4096x3072)
        self.spawn_x = 1300
        self.spawn_y = 500
        self.spawn_angle = 90  # Hadap ke bawah
        
        # Win condition
        self.target_laps = 15
    
    def setup(self):
        """Initialize pygame dan load track"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("NEAT Training - Tabrak Bahlil")
        self.clock = pygame.time.Clock()
        
        # Load track
        self.track_surface = pygame.image.load(self.track_path)
        self.track_surface = pygame.transform.scale(
            self.track_surface, (self.map_width, self.map_height)
        )
        
        # Fonts
        self.font_large = pygame.font.SysFont("Arial", 70)
        self.font_small = pygame.font.SysFont("Arial", 30)
    
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
        cars: List[AICar] = []
        nets: List[neat.nn.FeedForwardNetwork] = []
        
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            genome.fitness = 0
            
            car = AICar(self.spawn_x, self.spawn_y, self.spawn_angle)
            cars.append(car)
        
        # Camera
        camera_x, camera_y = 0, 0
        
        # Main loop
        running = True
        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
            
            # Update cars
            alive_count = 0
            
            for i, (car, net, (genome_id, genome)) in enumerate(zip(cars, nets, genomes)):
                if not car.is_alive:
                    continue
                
                alive_count += 1
                
                # Get radar data
                radar_data = car.get_radar_data()
                
                # Neural network decision
                output = net.activate(radar_data)
                action = output.index(max(output))
                
                # Steer: 0=kiri, 1=lurus, 2=kanan
                if action == 0:
                    car.steer(1)
                elif action == 2:
                    car.steer(-1)
                # action == 1: lurus
                
                # Update car
                car.update(self.track_surface)
                
                # Update fitness
                genome.fitness = car.get_fitness()
                
                # Check win condition
                if car.lap_count >= self.target_laps:
                    self._handle_winner(genome, net, car, config)
                    return
            
            # All dead?
            if alive_count == 0:
                break
            
            # Update camera (follow first alive car)
            for car in cars:
                if car.is_alive:
                    camera_x = int(car.pos[0] - self.screen_width / 2)
                    camera_y = int(car.pos[1] - self.screen_height / 2)
                    camera_x = max(0, min(camera_x, self.map_width - self.screen_width))
                    camera_y = max(0, min(camera_y, self.map_height - self.screen_height))
                    break
            
            # Render
            self._render(cars, camera_x, camera_y, alive_count, len(cars))
            
            self.clock.tick(0)  # Unlimited FPS untuk training cepat
    
    def _render(self, cars: List[AICar], camera_x: int, camera_y: int,
                alive: int, total: int):
        """Render frame"""
        # Draw track
        self.screen.blit(self.track_surface, (-camera_x, -camera_y))
        
        # Draw cars
        for car in cars:
            if car.is_alive:
                car.draw(self.screen, camera_x, camera_y)
        
        # Draw info
        text = self.font_large.render(f"Generation: {self.generation}", True, (255, 255, 0))
        rect = text.get_rect(center=(self.screen_width / 2, 100))
        self.screen.blit(text, rect)
        
        text = self.font_small.render(f"Alive: {alive}/{total}", True, (255, 255, 255))
        rect = text.get_rect(center=(self.screen_width / 2, 200))
        self.screen.blit(text, rect)
        
        # Best lap info
        best_lap = max((car.lap_count for car in cars if car.is_alive), default=0)
        text = self.font_small.render(f"Best Lap: {best_lap}/{self.target_laps}", True, (0, 255, 0))
        rect = text.get_rect(center=(self.screen_width / 2, 240))
        self.screen.blit(text, rect)
        
        pygame.display.flip()
    
    def _handle_winner(self, genome, net, car: AICar, config):
        """Handle ketika ada winner"""
        self.winner_found = True
        
        print("\n" + "=" * 60)
        print("🏆 TRAINING BERHASIL! 🏆")
        print(f"Motor menyelesaikan {self.target_laps} lap!")
        print(f"Generation: {self.generation}")
        print(f"Total distance: {int(car.distance)}")
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
