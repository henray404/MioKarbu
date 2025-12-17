"""
NEAT Trainer untuk Mio Karbu
============================

Modular trainer untuk training AI dengan NEAT algorithm.
Menggunakan GameManager untuk asset loading.
"""

import os
import sys
import time
import pickle
import neat
import pygame
from typing import List, Optional

# Path setup
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))
sys.path.insert(0, os.path.join(BASE_DIR, "config"))

# Import modules
from core.game_manager import GameManager, GameConfig
from core.display_manager import DisplayManager
from core.motor import Motor
import game_config as cfg


class NEATTrainer:
    """
    Trainer untuk NEAT evolution.
    
    Menggunakan GameManager untuk loading track dan masking.
    """
    
    def __init__(self, config_path: str, track_name: str = None,
                 headless: bool = False, render_interval: int = 1, map_name: str = ""):
        """
        Inisialisasi trainer.
        
        Args:
            config_path: Path ke neat config file
            track_name: Nama track (tanpa .png), None = pakai config
            headless: Training tanpa visualisasi (lebih cepat)
            render_interval: Render setiap N frame
        """
        self.config_path = config_path
        self.headless = headless
        self.render_interval = max(1, render_interval)
        
        # Game config - pakai dari game_config.py
        # Pilih spawn/finish berdasarkan track
        used_track = track_name or cfg.TRACK_NAME
        if used_track == "new-4":
            spawn_x, spawn_y = cfg.SPAWN_X, cfg.SPAWN_Y
            finish_start_x = cfg.FINISH_LINE_START_X
            finish_start_y = cfg.FINISH_LINE_START_Y
            finish_end_x = cfg.FINISH_LINE_END_X
            finish_end_y = cfg.FINISH_LINE_END_Y
        elif used_track == "map-2":
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
        
        self.game_cfg = GameConfig(
            track_name=track_name or cfg.TRACK_NAME,
            track_scale=cfg.TRACK_SCALE,
            original_track_width=cfg.ORIGINAL_TRACK_WIDTH,
            original_track_height=cfg.ORIGINAL_TRACK_HEIGHT,
            spawn_x=cfg.SPAWN_X,
            spawn_y=cfg.SPAWN_Y,
            spawn_angle=cfg.SPAWN_ANGLE,
            finish_line_start_x=finish_start_x,
            finish_line_start_y=finish_start_y,
            finish_line_end_x=finish_end_x,
            finish_line_end_y=finish_end_y,
            masking_file=cfg.MASKING_FILE,
            masking_subfolder=cfg.MASKING_SUBFOLDER,
        )
        
        # Managers
        self.game: Optional[GameManager] = None
        self.display: Optional[DisplayManager] = None
        
        # Training state
        self.generation = 0
        self.best_fitness = 0
        self.winner_found = False
        
        # Win condition
        self.target_laps = 15
    
    def setup(self):
        """Initialize pygame, display, dan load assets"""
        # Create managers
        self.game = GameManager(BASE_DIR, self.game_cfg)
        self.display = DisplayManager(fullscreen=False, width=1280, height=960)
        
        # Initialize display
        self.display.init(title="NEAT Training - Mio Karbu", headless=self.headless)
        
        if self.headless:
            print("[HEADLESS MODE] Training tanpa visualisasi - lebih cepat!")
        elif self.render_interval > 1:
            print(f"[REDUCED RENDER] Render setiap {self.render_interval} frame")
        
        # Load assets via GameManager
        self.game.load_track()
        self.game.load_masking()
    
    def create_car(self) -> Motor:
        """Create a Motor for training"""
        spawn_x, spawn_y = self.game.get_spawn_position()
        car = self.game.create_motor(spawn_x, spawn_y, color="pink", invincible=False)
        car.velocity = car.max_speed
        return car
    
    def eval_genomes(self, genomes, config):
        """
        Evaluate semua genome dalam satu generasi.
        Callback untuk NEAT.
        """
        self.generation += 1
        
        # Create cars dan networks
        cars: List[Motor] = []
        nets: List[neat.nn.FeedForwardNetwork] = []
        
        for genome_id, genome in genomes:
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            genome.fitness = 0
            
            car = self.create_car()
            cars.append(car)
        
        # Timing
        max_gen_time = 90  # 60 detik per generasi
        gen_start_time = time.time()
        best_lap_count = 0
        
        # Main loop
        frame_count = 0
        running = True
        
        while running:
            frame_count += 1
            
            # Check max time
            if time.time() - gen_start_time > max_gen_time:
                break
            
            # Event handling (jika tidak headless)
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
                
                # Neural network decision
                radar_data = car.get_radar_data()
                output = net.activate(radar_data)
                
                # Continuous control
                steering = max(-1, min(1, output[0]))
                throttle = max(0.3, min(1, output[1]))
                
                car.set_ai_input(steering, throttle)
                car.update()
                
                # Calculate fitness
                fitness = car.distance_traveled
                fitness += car.checkpoint_count * 200
                if car.lap_count > 0:
                    fitness += car.lap_count * 2000
                
                # Kill jika stuck
                max_time_between_checkpoints = 20 * 60
                time_since_last_checkpoint = car.time_spent - car.last_checkpoint_time
                if time_since_last_checkpoint > max_time_between_checkpoints:
                    car.alive = False
                
                genome.fitness = fitness
                
                # Reset timer jika lap baru
                if car.lap_count > best_lap_count:
                    best_lap_count = car.lap_count
                    gen_start_time = time.time()
                    print(f"[TIMER RESET] Lap {best_lap_count} completed!")
                
                # Check win
                if car.lap_count >= self.target_laps:
                    self._handle_winner(genome, net, car, config)
                    return
            
            # All dead?
            if alive_count == 0:
                break
            
            # Camera follow best car
            best_car = self._get_best_car(cars, genomes)
            if best_car:
                self.display.update_camera(
                    best_car.x, best_car.y,
                    self.game.map_width, self.game.map_height
                )
            
            # Render
            if not self.headless and frame_count % self.render_interval == 0:
                self._render(cars, alive_count, len(cars))
            
            self.display.clock.tick(0)  # Unlimited FPS
    
    def _get_best_car(self, cars: List[Motor], genomes) -> Optional[Motor]:
        """Get car with highest fitness"""
        best_car = None
        best_fitness = -1
        
        for car, (genome_id, genome) in zip(cars, genomes):
            if car.alive and genome.fitness > best_fitness:
                best_fitness = genome.fitness
                best_car = car
        
        return best_car
    
    def _render(self, cars: List[Motor], alive: int, total: int):
        """Render frame"""
        self.display.render_track(self.game.track_surface)
        
        # Draw alive cars
        for car in cars:
            if car.alive:
                self.display.render_motor(car)
        
        # Draw info
        if self.display.font_large:
            # Generation
            text = self.display.font_large.render(
                f"Generation: {self.generation}", True, (255, 255, 0)
            )
            rect = text.get_rect(center=(self.display.width // 2, 100))
            self.display.screen.blit(text, rect)
            
            # Alive count
            text = self.display.font_small.render(
                f"Alive: {alive}/{total}", True, (255, 255, 255)
            )
            rect = text.get_rect(center=(self.display.width // 2, 200))
            self.display.screen.blit(text, rect)
            
            # Best lap
            best_lap = max((car.lap_count for car in cars if car.alive), default=0)
            text = self.display.font_small.render(
                f"Best Lap: {best_lap}/{self.target_laps}", True, (0, 255, 0)
            )
            rect = text.get_rect(center=(self.display.width // 2, 240))
            self.display.screen.blit(text, rect)
        
        pygame.display.flip()
    
    def _handle_winner(self, genome, net, car: Motor, config):
        """Handle ketika ada winner"""
        self.winner_found = True
        
        print("\n" + "=" * 60)
        print("TRAINING BERHASIL!")
        print(f"Motor menyelesaikan {self.target_laps} lap!")
        print(f"Generation: {self.generation}")
        print(f"Distance: {int(car.distance_traveled)}")
        print("=" * 60)
        
        # Save models
        self._save_model(genome, net, 'winner')
    
    def _save_model(self, genome, net, prefix: str):
        """Save genome dan network ke file"""
        models_dir = os.path.join(BASE_DIR, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        with open(os.path.join(models_dir, f'{prefix}_{map_name}.pkl'), 'wb') as f:
            pickle.dump(genome, f)
        with open(os.path.join(models_dir, f'{prefix}_network.pkl'), 'wb') as f:
            pickle.dump(net, f)
        
        print(f"Model tersimpan di: {models_dir}")
    
    def run(self, generations: int = 50, checkpoint_path: str = None) -> Optional[neat.DefaultGenome]:
        """
        Run NEAT training.
        
        Args:
            generations: Max generations
            checkpoint_path: Path ke checkpoint untuk resume
            
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
        
        # Create or restore population
        if checkpoint_path and os.path.exists(checkpoint_path):
            print(f"Resuming from checkpoint: {checkpoint_path}")
            population = neat.Checkpointer.restore_checkpoint(checkpoint_path)
        else:
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
        
        # Save best genome jika belum ada winner
        if winner and not self.winner_found:
            winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
            self._save_model(winner, winner_net, 'best')
        
        self.display.quit()
        return winner
