import pygame
import os
import math
import sys
import neat
import pickle

screen_width = 1024
screen_height = 768
generation = 0

class Car:
    def __init__(self):
        # Load sprite
        car_path = os.path.join(os.path.dirname(__file__), "..", "assets", "motor", "pink-1.png")
        self.surface = pygame.image.load(car_path)
        self.surface = pygame.transform.scale(self.surface, (30, 60))
        # rotate surface -90 degrees to face upwards initially
        self.surface = pygame.transform.rotate(self.surface, -90)
        self.pos = [600, 240]  # Starting position
        self.angle = 0
        self.speed = 0
        self.center = [self.pos[0] + 23, self.pos[1] + 46]
        self.radars = []
        self.is_alive = True
        self.goal = False
        self.distance = 0
        self.time_spent = 0
        self.lap_count = 0
        self.start_pos = [600, 240]
        self.has_left_start = False  # Track apakah sudah keluar dari area start
        self.min_distance_to_leave = 300  # Jarak minimum dari start untuk dianggap keluar
    
    def draw(self, screen, camera):
        # Draw dengan camera offset
        screen.blit(self.rotate_surface, (self.pos[0] - camera.x, self.pos[1] - camera.y))
        self.draw_radar(screen, camera)

    def draw_radar(self, screen, camera):
        for r in self.radars:
            pos, dist = r
            # Draw dengan camera offset
            pygame.draw.line(screen, (0, 255, 0), 
                           (self.center[0] - camera.x, self.center[1] - camera.y), 
                           (pos[0] - camera.x, pos[1] - camera.y), 1)
            pygame.draw.circle(screen, (0, 255, 0), 
                             (pos[0] - camera.x, pos[1] - camera.y), 5)

    def check_collision(self, map):
        self.is_alive = True
        for p in self.four_points:
            try:
                pixel = map.get_at((int(p[0]), int(p[1])))
                r, g, b = pixel[0], pixel[1], pixel[2]
                
                # Cek jika hitam (track yang valid)
                is_black = (r < 70 and g < 70 and b < 70)
                
                # Cek jika putih/finish line (threshold lebih rendah biar lebih toleran)
                is_white = (r > 120 and g > 120 and b > 120)
                
                # Cek jika merah (finish line alternatif, lebih toleran)
                is_red = (r > 120 and g < 100 and b < 100)
                
                # Jika bukan hitam, putih, atau merah = keluar track
                if not (is_black or is_white or is_red):
                    self.is_alive = False
                    break
            except:
                self.is_alive = False
                break
    
    def check_radar(self, degree, map):
        len_radar = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len_radar)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len_radar)

        while len_radar < 300:
            try:
                pixel = map.get_at((x, y))
                r, g, b = pixel[0], pixel[1], pixel[2]
                
                # Cek jika hitam (track yang valid)
                is_black = (r < 50 and g < 50 and b < 50)
                
                # Cek jika putih/finish line (juga dianggap valid)
                is_white = (r > 180 and g > 180 and b > 180)
                
                # Cek jika merah (finish line alternatif)
                is_red = (r > 200 and g < 100 and b < 100)
                
                # Stop jika bukan hitam, putih, atau merah (ketemu batas track)
                if not (is_black or is_white or is_red):
                    break
            except:
                break
            
            len_radar += 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * len_radar)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * len_radar)

        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
    def update(self, map):
        # Check speed - lebih lambat untuk kontrol lebih baik
        self.speed = 6
        
        # Check position and rotate
        self.rotate_surface = self.rot_center(self.surface, self.angle)
        self.pos[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.pos[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        
        # Update distance and time
        self.distance += self.speed
        self.time_spent += 1
        
        # Lap detection - pakai math.sqrt untuk hitung jarak dari start
        dist_from_start = math.sqrt(math.pow(self.pos[0] - self.start_pos[0], 2) + 
                                   math.pow(self.pos[1] - self.start_pos[1], 2))
        
        # Jika sudah jauh dari start (keluar dari area start)
        if dist_from_start > self.min_distance_to_leave:
            if not self.has_left_start:
                self.has_left_start = True
        
        # Jika sudah keluar DAN kembali dekat ke start = 1 lap selesai
        elif self.has_left_start and dist_from_start < 80:
            self.lap_count += 1
            self.has_left_start = False  # Reset untuk lap berikutnya
            print(f"🏁 Lap {self.lap_count} completed! Distance: {int(self.distance)}")
        
        # Calculate 4 collision points
        self.center = [int(self.pos[0]) + 23, int(self.pos[1]) + 23]
        len_corner = 30
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * len_corner, 
                    self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * len_corner]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * len_corner, 
                     self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * len_corner]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * len_corner, 
                       self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * len_corner]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * len_corner, 
                        self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * len_corner]
        self.four_points = [left_top, right_top, left_bottom, right_bottom]
        
        # Check collision
        self.check_collision(map)
        
        # Update radars
        self.radars.clear()
        for d in range(-90, 120, 45):
            self.check_radar(d, map)
    
    def get_data(self):
        radars = self.radars
        ret = [0, 0, 0, 0, 0]
        for i, r in enumerate(radars):
            ret[i] = int(r[1] / 30)
        return ret

    def get_alive(self):
        return self.is_alive

    def get_reward(self):
        # Reward berdasarkan distance + bonus untuk lap completion
        base_reward = self.distance / 50.0
        lap_bonus = self.lap_count * 100
        return base_reward + lap_bonus

    def rot_center(self, image, angle):
        # Simple rotation without subsurface
        rot_image = pygame.transform.rotate(image, angle)
        return rot_image


def run_car(genomes, config):
    # Init NEAT
    nets = []
    cars = []

    for id, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0
        # Init cars
        cars.append(Car())

    # Init game
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 70)
    font = pygame.font.SysFont("Arial", 30)
    
    # Load track
    map_width = 1920
    map_height = 1440
    track_path = os.path.join(os.path.dirname(__file__), "..", "assets", "tracks", "mandalika.png")
    map = pygame.image.load(track_path)
    map = pygame.transform.scale(map, (map_width, map_height))
    
    # Camera
    camera = pygame.Rect(0, 0, map_width, map_height)
    
    # Main loop
    global generation
    generation += 1
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # Input data and get result from network
        for index, car in enumerate(cars):
            output = nets[index].activate(car.get_data())
            i = output.index(max(output))
            if i == 0:
                car.angle += 7  # Belok kiri (lebih smooth)
            elif i == 1:
                pass  # Jalan lurus (gak belok)
            else:
                car.angle -= 7  # Belok kanan (lebih smooth)

        # Update car and fitness
        remain_cars = 0
        winner_found = False
        
        for i, car in enumerate(cars):
            if car.get_alive():
                remain_cars += 1
                car.update(map)
                genomes[i][1].fitness += car.get_reward()
                
                # Check jika sudah 15 lap berturut-turut tanpa collision
                if car.lap_count >= 15:
                    winner_found = True
                    print(f"\n" + "="*60)
                    print(f"🏆 TRAINING BERHASIL! 🏆")
                    print(f"Motor menyelesaikan 15 lap tanpa tabrakan!")
                    print(f"Generation: {generation}")
                    print(f"Total distance: {int(car.distance)}")
                    print(f"Time: {car.time_spent} frames ({car.time_spent/60:.1f} detik)")
                    print("="*60)
                    
                    # Save winning model
                    winner_genome = genomes[i][1]
                    winner_net = neat.nn.FeedForwardNetwork.create(winner_genome, config)
                    
                    with open('winner_15laps_genome.pkl', 'wb') as f:
                        pickle.dump(winner_genome, f)
                    with open('winner_15laps_network.pkl', 'wb') as f:
                        pickle.dump(winner_net, f)
                    
                    print("✅ Model tersimpan: winner_15laps_genome.pkl")
                    print("✅ Network tersimpan: winner_15laps_network.pkl")
                    break
        
        # Jika ada winner, stop training
        if winner_found:
            pygame.quit()
            return

        # Check jika semua mobil mati
        if remain_cars == 0:
            break
        
        # Update camera (follow first alive car)
        for car in cars:
            if car.get_alive():
                camera.x = int(car.pos[0] - screen_width / 2)
                camera.y = int(car.pos[1] - screen_height / 2)
                camera.x = max(0, min(camera.x, map_width - screen_width))
                camera.y = max(0, min(camera.y, map_height - screen_height))
                break
        
        # Drawing
        screen.blit(map, (0 - camera.x, 0 - camera.y))
        for car in cars:
            if car.get_alive():
                car.draw(screen, camera)

        text = generation_font.render("Generation : " + str(generation), True, (255, 255, 0))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 100)
        screen.blit(text, text_rect)

        text = font.render("remain cars : " + str(remain_cars), True, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (screen_width/2, 200)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(0)


if __name__ == "__main__":
    import pickle
    import os
    
    # Load NEAT config
    config_path = "config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )
    
    # Create population
    p = neat.Population(config)
    
    # Add reporters
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    
    # Add checkpointer untuk save progress
    checkpoint_dir = "neat_checkpoints"
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
    p.add_reporter(neat.Checkpointer(5, filename_prefix=f'{checkpoint_dir}/neat-checkpoint-'))
    
    # Run NEAT (akan memanggil run_car untuk setiap generasi)
    winner = p.run(run_car, 1000)
    
    # Save best genome
    print(f"\n\nBest genome:\n{winner}")
    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)
    print("\nBest genome saved to 'best_genome.pkl'")
    
    # Save best genome as neural network
    winner_net = neat.nn.FeedForwardNetwork.create(winner, config)
    with open('best_network.pkl', 'wb') as f:
        pickle.dump(winner_net, f)
    print("Best network saved to 'best_network.pkl'")
