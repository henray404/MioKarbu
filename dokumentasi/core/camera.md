# 📁 camera.py

> Path: `src/core/camera.py`

## Deskripsi

Sistem kamera yang mengikuti target (motor player) dengan **smooth interpolation**.

---

## Global Variables

```python
camera = pygame.Rect(0, 0, 0, 0)  # Posisi dan ukuran kamera
camera_target_x = 0               # Target X untuk lerp
camera_target_y = 0               # Target Y untuk lerp
```

---

## Functions

### `create_screen(width, height, title)`

Buat window pygame dan set ukuran kamera.

```python
def create_screen(width, height, title="Mio-Mber"):
    pygame.display.set_caption(title)
    screen = pygame.display.set_mode((width, height))
    camera.width = width
    camera.height = height
    return screen
```

---

### `update_camera(target_x, target_y, map_width, map_height)`

Update posisi kamera untuk mengikuti target.

```python
def update_camera(target_x, target_y, map_width, map_height):
    global camera_target_x, camera_target_y

    zoom_offset = 50  # Zoom adjustment

    # Target = center motor pada layar
    camera_target_x = target_x - (camera.width // 2) + zoom_offset
    camera_target_y = target_y - (camera.height // 2) + zoom_offset

    # Smooth camera follow (LERP)
    smoothness = 0.15
    camera.x += (camera_target_x - camera.x) * smoothness
    camera.y += (camera_target_y - camera.y) * smoothness

    # Clamp ke bounds
    camera.x = clamp(camera.x, 0, map_width - camera.width)
    camera.y = clamp(camera.y, 0, map_height - camera.height)
```

---

## 📐 Matematika: Linear Interpolation (Lerp)

### Rumus

```
new_position = current_position + (target_position - current_position) × t
```

Dimana:

- `t` = smoothness (0.0 - 1.0)
- `t = 0.15` = 15% menuju target per frame

### Visualisasi

```
Frame 1: pos = 0, target = 100
         new = 0 + (100 - 0) × 0.15 = 15

Frame 2: pos = 15, target = 100
         new = 15 + (100 - 15) × 0.15 = 27.75

Frame 3: pos = 27.75, target = 100
         new = 27.75 + (100 - 27.75) × 0.15 = 38.59

... converges to target over time
```

### Karakteristik

| smoothness | Efek                          |
| ---------- | ----------------------------- |
| 0.05       | Sangat smooth, lambat respond |
| 0.15       | Balance (default)             |
| 0.3        | Responsif, sedikit jerky      |
| 1.0        | Instant (no smoothing)        |

---

## Boundary Clamping

Kamera tidak boleh keluar dari batas map:

```python
camera.x = max(0, min(camera.x, map_width - camera.width))
camera.y = max(0, min(camera.y, map_height - camera.height))
```

**Diagram:**

```
┌──────────────────────────────────────┐
│                MAP                    │
│   ┌────────────┐                      │
│   │  CAMERA    │  ← camera.x, camera.y│
│   │  VIEWPORT  │                      │
│   └────────────┘                      │
│                                       │
│                  ← map_width          │
└──────────────────────────────────────┘
                   ↑
            map_height

Constraint:
- camera.x ∈ [0, map_width - camera.width]
- camera.y ∈ [0, map_height - camera.height]
```

---

## Penggunaan

```python
# Di main.py game loop
update_camera(player.x, player.y, MAP_WIDTH, MAP_HEIGHT)

# Render dengan offset kamera
track.blit(screen, (-camera.x, -camera.y))
player.draw(screen, camera.x, camera.y)
```
