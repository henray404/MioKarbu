"""
Class ini menghandle semua logic training NEAT:
- Load config
- Evaluasi fitness setiap genome
- Visualisasi training (optional)
- Save/load best genome
"""

import os
import sys
import math
import pickle
import neat
import pygame

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from core.motor import Motor
from core.track import Track
from core.distance_sensor import DistanceSensor


class NEATTrainer:
    """
    Trainer untuk evolusi AI motor menggunakan NEAT algorithm.
    
    Attributes:
        config_path: Path ke file konfigurasi NEAT
        track: Track object untuk racing
        generation: Generasi saat ini
        best_fitness: Fitness terbaik yang pernah dicapai
        visualize: Apakah menampilkan visualisasi training
    """
    
    def __init__(self, config_path: str, track_name: str = "map-2", visualize: bool = True):
        """
        Inisialisasi trainer.
        
        Args:
            config_path: Path ke neat-config.txt
            track_name: Nama track untuk training
            visualize: Tampilkan pygame window saat training
        """
        self.config_path = config_path
        self.track_name = track_name
        self.visualize = visualize
        
        # Training state
        self.generation = 0
        self.best_fitness = 0
        self.best_genome = None
        
        # Pygame setup (kalau visualize)
        self.screen = None
        self.clock = None
        self.font = None
        
        # Track setup
        self.map_width = 1920
        self.map_height = 1440
        self.track = None
        
        # Training parameters
        self.max_frames = 1000        # Max frame per motor per generasi
        self.spawn_x = 960            # Posisi spawn X
        self.spawn_y = 720            # Posisi spawn Y
        self.spawn_angle = 0          # Sudut awal (radian)
        
        # Sensor config
        self.num_sensors = 7
        self.sensor_fov = 180
        self.sensor_max_dist = 200
        
        # Camera untuk visualisasi
        self.camera_x = 0
        self.camera_y = 0
        
        # Stats
        self.generation_stats = []
    
    def setup_pygame(self):
        """Initialize pygame untuk visualisasi"""
        if not self.visualize:
            return
            
        pygame.init()
        self.screen = pygame.display.set_mode((1024, 768))
        pygame.display.set_caption("NEAT Training - Tabrak Bahlil")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
    
    def setup_track(self):
        """Load track untuk training"""
        self.track = Track(self.track_name, self.map_width, self.map_height, road_threshold=180)
    
    def create_motor(self, genome, config) -> tuple:
        """
        Buat motor dengan neural network dari genome.
        
        Args:
            genome: NEAT genome
            config: NEAT config
            
        Returns:
            tuple (motor, neural_network)
        """
        # Buat neural network dari genome
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        
        # Buat motor
        motor = Motor(self.spawn_x, self.spawn_y, color="pink")
        motor.angle = self.spawn_angle
        motor.set_track(self.track)
        motor.create_sensor(self.num_sensors, self.sensor_fov, self.sensor_max_dist)
        
        return motor, net
    
    def calculate_fitness(self, motor: Motor, frames_alive: int) -> float:
        """
        Hitung fitness score untuk motor.
        
        Fitness components:
        - distance_traveled: Jarak yang ditempuh (utama)
        - avg_speed: Rata-rata kecepatan (bonus)
        - frames_alive: Berapa lama bertahan (bonus kecil)
        
        Args:
            motor: Motor object
            frames_alive: Jumlah frame motor hidup
            
        Returns:
            Fitness score
        """
        fitness = 0.0
        
        # 1. Jarak tempuh (komponen utama)
        # Semakin jauh = semakin bagus
        fitness += motor.distance_traveled * 1.0
        
        # 2. Bonus kecepatan rata-rata
        # Mencegah motor yang jalan pelan-pelan
        if frames_alive > 0:
            avg_speed = motor.distance_traveled / frames_alive
            fitness += avg_speed * 50
         
        # 3. Bonus survival time (kecil)
        # Supaya motor yang bertahan lama sedikit lebih baik
        fitness += frames_alive * 0.1
        
        # 4. Penalty kalau stuck (tidak jalan)
        if motor.distance_traveled < 10:
            fitness *= 0.1  # Penalti besar kalau hampir tidak gerak
        
        return fitness
    
    def eval_genome(self, genome, config) -> float:
        """
        Evaluasi satu genome (tanpa visualisasi).
        
        Args:
            genome: NEAT genome
            config: NEAT config
            
        Returns:
            Fitness score
        """
        motor, net = self.create_motor(genome, config)
        
        frames_alive = 0
        
        for frame in range(self.max_frames):
            if not motor.alive:
                break
            
            # Get sensor data
            sensor_data = motor.get_sensor_data()
            
            # Neural network decision
            output = net.activate(sensor_data)
            steering = output[0]  # -1 to 1
            throttle = output[1]  # -1 to 1
            
            # Apply AI input
            motor.set_ai_input(steering, throttle)
            motor.update()
            
            frames_alive += 1
            
            # Early stop kalau stuck
            if frame > 100 and motor.distance_traveled < 5:
                break
        
        return self.calculate_fitness(motor, frames_alive)
    
    def eval_genomes(self, genomes, config):
        """
        Evaluasi semua genome dalam satu generasi.
        Ini adalah callback yang dipanggil NEAT setiap generasi.
        
        Args:
            genomes: List of (genome_id, genome) tuples
            config: NEAT config
        """
        self.generation += 1
        
        if self.visualize:
            self._eval_genomes_visual(genomes, config)
        else:
            self._eval_genomes_headless(genomes, config)
        
        # Update best genome
        for genome_id, genome in genomes:
            if genome.fitness > self.best_fitness:
                self.best_fitness = genome.fitness
                self.best_genome = genome
        
        # Print stats
        fitnesses = [g.fitness for _, g in genomes]
        avg_fitness = sum(fitnesses) / len(fitnesses)
        max_fitness = max(fitnesses)
        
        print(f"Gen {self.generation:3d} | Avg: {avg_fitness:8.2f} | Max: {max_fitness:8.2f} | Best Ever: {self.best_fitness:8.2f}")
        
        self.generation_stats.append({
            'generation': self.generation,
            'avg_fitness': avg_fitness,
            'max_fitness': max_fitness,
            'best_ever': self.best_fitness
        })
    
    def _eval_genomes_headless(self, genomes, config):
        """Evaluasi tanpa visualisasi (cepat)"""
        for genome_id, genome in genomes:
            genome.fitness = self.eval_genome(genome, config)
    
    def _eval_genomes_visual(self, genomes, config):
        """Evaluasi dengan visualisasi pygame"""
        # Buat semua motor sekaligus
        motors = []
        nets = []
        genome_list = []
        
        for genome_id, genome in genomes:
            motor, net = self.create_motor(genome, config)
            motors.append(motor)
            nets.append(net)
            genome_list.append(genome)
            genome.fitness = 0
        
        # Simulasi semua motor bareng
        frame = 0
        running = True
        
        while running and frame < self.max_frames:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            
            # Update semua motor
            alive_count = 0
            best_motor = None
            best_distance = 0
            
            for i, (motor, net, genome) in enumerate(zip(motors, nets, genome_list)):
                if not motor.alive:
                    continue
                
                alive_count += 1
                
                # Get sensor data
                sensor_data = motor.get_sensor_data()
                
                # Neural network decision
                output = net.activate(sensor_data)
                steering = output[0]
                throttle = output[1]
                
                # Apply AI input
                motor.set_ai_input(steering, throttle)
                motor.update()
                
                # Track best motor
                if motor.distance_traveled > best_distance:
                    best_distance = motor.distance_traveled
                    best_motor = motor
            
            # Stop kalau semua mati
            if alive_count == 0:
                break
            
            # Update camera ke motor terbaik
            if best_motor:
                self.camera_x = best_motor.x - 512
                self.camera_y = best_motor.y - 384
                self.camera_x = max(0, min(self.camera_x, self.map_width - 1024))
                self.camera_y = max(0, min(self.camera_y, self.map_height - 768))
            
            # Render
            self.screen.fill((30, 30, 30))
            
            # Draw track
            self.screen.blit(self.track.image, (-self.camera_x, -self.camera_y))
            
            # Draw all motors
            for motor in motors:
                if motor.alive:
                    self._draw_motor(motor)
            
            # Draw sensors dari motor terbaik
            if best_motor and best_motor.sensor:
                best_motor.sensor.draw(self.screen, self._camera_obj(), 
                                       best_motor.x, best_motor.y, best_motor.angle)
            
            # Draw info
            self._draw_info(frame, alive_count, len(motors), best_distance)
            
            pygame.display.flip()
            self.clock.tick(60)  # Bisa dinaikkan untuk training lebih cepat
            
            frame += 1
        
        # Set fitness untuk semua genome
        for motor, genome in zip(motors, genome_list):
            genome.fitness = self.calculate_fitness(motor, frame)
    
    def _camera_obj(self):
        """Return camera-like object untuk compatibility"""
        class Camera:
            pass
        cam = Camera()
        cam.x = self.camera_x
        cam.y = self.camera_y
        return cam
    
    def _draw_motor(self, motor: Motor):
        """Draw single motor"""
        if motor.use_sprite:
            current_surface = motor.frames[motor.current_frame]
        else:
            current_surface = motor.surface
        
        rotated = pygame.transform.rotate(current_surface, -math.degrees(motor.angle))
        rect = rotated.get_rect(center=(motor.x - self.camera_x, motor.y - self.camera_y))
        
        # Warna berbeda untuk motor mati
        if not motor.alive:
            rotated.set_alpha(100)
        
        self.screen.blit(rotated, rect)
    
    def _draw_info(self, frame: int, alive: int, total: int, best_dist: float):
        """Draw training info overlay"""
        info_lines = [
            f"Generation: {self.generation}",
            f"Frame: {frame}/{self.max_frames}",
            f"Alive: {alive}/{total}",
            f"Best Distance: {best_dist:.1f}",
            f"Best Ever Fitness: {self.best_fitness:.1f}",
            "",
            "ESC to quit"
        ]
        
        y = 10
        for line in info_lines:
            text = self.font.render(line, True, (255, 255, 255))
            # Background box
            pygame.draw.rect(self.screen, (0, 0, 0, 128), 
                           (5, y - 2, text.get_width() + 10, text.get_height() + 4))
            self.screen.blit(text, (10, y))
            y += 30
    
    def run(self, generations: int = 100):
        """
        Jalankan training NEAT.
        
        Args:
            generations: Jumlah generasi maksimum
        """
        # Setup
        self.setup_track()
        if self.visualize:
            self.setup_pygame()
        
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
        
        # Run evolution
        winner = population.run(self.eval_genomes, generations)
        
        print("\n" + "="*50)
        print("Training Complete!")
        print(f"Best Fitness: {winner.fitness:.2f}")
        print("="*50)
        
        # Save best genome
        self.save_best_genome(winner)
        
        if self.visualize:
            pygame.quit()
        
        return winner
    
    def save_best_genome(self, genome, filename: str = "best_genome.pkl"):
        """Save genome terbaik ke file"""
        save_path = os.path.join(BASE_DIR, "models", filename)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            pickle.dump(genome, f)
        
        print(f"Best genome saved to: {save_path}")
    
    @staticmethod
    def load_genome(filename: str = "best_genome.pkl"):
        """Load genome dari file"""
        load_path = os.path.join(BASE_DIR, "models", filename)
        
        with open(load_path, 'rb') as f:
            genome = pickle.load(f)
        
        return genome


# Entry point untuk testing
if __name__ == "__main__":
    config_path = os.path.join(BASE_DIR, "config", "neat-config.txt")
    
    trainer = NEATTrainer(
        config_path=config_path,
        track_name="japan",
        visualize=True
    )
    
    trainer.run(generations=50)
