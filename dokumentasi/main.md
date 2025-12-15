# 📁 main.py

> Path: `src/main.py`

## Deskripsi

Entry point utama game - mode **Player vs AI Racing**.

---

## Konstanta

```python
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
MAP_SCALE = 6.0
MAP_WIDTH = int(2752 * MAP_SCALE)   # 16512
MAP_HEIGHT = int(1536 * MAP_SCALE)  # 9216
FPS = 60
```

---

## Game Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      MAIN.PY FLOW                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. INITIALIZATION                                           │
│     ├── pygame.init()                                        │
│     ├── Load track surface                                   │
│     ├── Load masking surface                                 │
│     ├── Load AI masking                                      │
│     └── Print game info                                      │
│                                                              │
│  2. SPAWN ENTITIES                                           │
│     ├── Player motor (hijau)                                 │
│     │   └── invincible = True                                │
│     └── AI motors (dari model pkl)                           │
│         └── Load neural network                              │
│                                                              │
│  3. GAME LOOP                                                │
│     ├── Handle events (quit, reset)                          │
│     ├── Player input (handle_input)                          │
│     ├── AI decision (neural network)                         │
│     ├── Update physics                                       │
│     ├── Check win condition                                  │
│     └── Render                                               │
│                                                              │
│  4. WIN/LOSE                                                 │
│     └── First to target_laps wins                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Player Setup

```python
# Spawn position (sama dengan training)
spawn_ratio_x = 0.634
spawn_ratio_y = 0.179
spawn_x = int(MAP_WIDTH * spawn_ratio_x)
spawn_y = int(MAP_HEIGHT * spawn_ratio_y)

# Create player
player = Motor(spawn_x, spawn_y, color="hijau")
player.invincible = True  # Tidak mati kalau keluar track
player.set_track_surface(track_surface)
player.set_masking_surface(masking_surface)
```

---

## AI Setup

```python
# Load trained model
model_path = os.path.join(BASE_DIR, "models", "winner_genome.pkl")
with open(model_path, 'rb') as f:
    genome = pickle.load(f)

# Create neural network
config = neat.Config(...)
net = neat.nn.FeedForwardNetwork.create(genome, config)

# Create AI motor
ai = Motor(spawn_x, spawn_y, color="pink")
ai.invincible = False  # AI bisa mati
```

---

## Game Loop

### Event Handling

```python
for event in pygame.event.get():
    if event.type == pygame.QUIT:
        running = False
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_r:
            # Reset game
            player.reset()
            for ai in ai_motors:
                ai.reset()
        if event.key == pygame.K_ESCAPE:
            running = False
```

### Player Update

```python
keys = pygame.key.get_pressed()
player.handle_input(keys)
player.update()
```

### AI Update

```python
for ai, net in zip(ai_motors, ai_nets):
    if ai.alive:
        # Get sensor data
        radar_data = ai.get_radar_data()

        # Neural network decision
        output = net.activate(radar_data)
        action = output.index(max(output))

        # Steer: 0=kiri, 1=lurus, 2=kanan
        if action == 0:
            ai.steer(1)
        elif action == 2:
            ai.steer(-1)

        ai.update()
```

---

## Rendering

### Layer Order

1. Track surface (background)
2. AI motors
3. Player motor
4. UI elements (speedometer, lap counter, etc.)

### Camera

```python
# Follow player
camera_x = int(player.x - SCREEN_WIDTH / 2)
camera_y = int(player.y - SCREEN_HEIGHT / 2)

# Clamp to bounds
camera_x = max(0, min(camera_x, MAP_WIDTH - SCREEN_WIDTH))
camera_y = max(0, min(camera_y, MAP_HEIGHT - SCREEN_HEIGHT))
```

---

## UI Elements

### Speedometer (bottom right)

```python
speed_kmh = player.get_speed_kmh()
# Render circular speedometer dengan angka km/h
```

### Lap Counter

```python
# Player lap / Target lap
text = f"Lap {player.lap_count}/{target_laps}"
```

### Position

```python
# P1 atau P2 berdasarkan lap count
if player.lap_count > ai.lap_count:
    position = "P1"
else:
    position = "P2"
```

---

## Win Condition

```python
target_laps = 3

if player.lap_count >= target_laps:
    # Player wins!
    show_win_screen("PLAYER WINS!")

if ai.lap_count >= target_laps:
    # AI wins
    show_win_screen("AI WINS!")
```

---

## Kontrol

| Key         | Action       |
| ----------- | ------------ |
| W           | Gas maju     |
| S           | Rem/mundur   |
| A           | Belok kiri   |
| D           | Belok kanan  |
| Space/Shift | Drift        |
| R           | Reset posisi |
| ESC         | Quit game    |
