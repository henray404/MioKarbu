# collision.py - Collision Handler

> Lokasi: `src/core/collision.py`

---

## Deskripsi Umum

CollisionHandler menangani semua logic deteksi tabrakan dalam game. Sistem ini menggunakan pendekatan **masking-based collision** dimana warna pixel pada masking surface menentukan jenis zone.

Keunggulan pendekatan ini:

1. **Flexibility**: Track designer bisa membuat collision zones dengan menggambar warna
2. **Performance**: Lookup warna pixel sangat cepat
3. **Multi-zone**: Satu sistem bisa mendeteksi wall, slow zone, dan checkpoint

---

## Class: CollisionHandler

### Constructor

```python
def __init__(self, length: float = 140, width: float = 80):
    self.length = length  # Panjang motor
    self.width = width    # Lebar motor

    # Surfaces untuk collision detection
    self.track = None               # Track object (legacy)
    self.track_surface = None       # pygame.Surface untuk track
    self.masking_surface = None     # pygame.Surface untuk masking
```

---

## Sistem Masking Colors

Masking menggunakan warna pixel untuk menentukan zone. Setiap warna memiliki arti khusus:

### Tabel Warna Zone

| Zone         | Warna   | Kondisi RGB         | Penjelasan                               |
| ------------ | ------- | ------------------- | ---------------------------------------- |
| Track        | Hitam   | avg < 50            | Area jalan yang bisa dilewati            |
| Wall         | Merah   | r>150, g<100, b<100 | Dinding - motor akan bounce atau explode |
| Checkpoint 1 | Hijau   | g>150, r<150, b<150 | Checkpoint pertama dalam lap             |
| Checkpoint 2 | Cyan    | g>150, b>150, r<150 | Checkpoint kedua                         |
| Checkpoint 3 | Kuning  | r>150, g>150, b<150 | Checkpoint ketiga                        |
| Checkpoint 4 | Magenta | r>150, b>150, g<150 | Checkpoint keempat (terakhir)            |
| Slow Zone    | Lainnya | default             | Area yang memperlambat motor             |

### Diagram Visual

```
+------------------------------------------------------------------+
|                        MASKING COLORS                             |
+------------------------------------------------------------------+
|                                                                   |
|   HITAM (Track)       = Area jalan                                |
|   [RGB: 0, 0, 0]                                                  |
|                                                                   |
|   MERAH (Wall)        = Dinding, motor bounce/explode             |
|   [RGB: 200, 50, 50]                                              |
|                                                                   |
|   HIJAU (CP1)         = Checkpoint 1                              |
|   [RGB: 50, 200, 50]                                              |
|                                                                   |
|   CYAN (CP2)          = Checkpoint 2                              |
|   [RGB: 50, 200, 200]                                             |
|                                                                   |
|   KUNING (CP3)        = Checkpoint 3                              |
|   [RGB: 200, 200, 50]                                             |
|                                                                   |
|   MAGENTA (CP4)       = Checkpoint 4                              |
|   [RGB: 200, 50, 200]                                             |
|                                                                   |
|   PUTIH/ABU (Slow)    = Slow zone, speed berkurang                |
|   [RGB: 200, 200, 200]                                            |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Method: set_masking_surface(surface)

Set masking surface untuk collision detection.

```python
def set_masking_surface(self, surface: pygame.Surface) -> None:
    """
    Set masking surface untuk advanced collision.

    Args:
        surface: pygame.Surface dengan warna zone

    Note:
        Surface harus sudah di-scale sesuai dengan track.
        Koordinat motor harus sesuai dengan koordinat surface.
    """
    self.masking_surface = surface
```

---

## Method: get_collision_corners(x, y, angle)

Mendapatkan 4 titik corner dari collision box motor.

```python
def get_collision_corners(self, x: float, y: float,
                          angle: float) -> List[Tuple[float, float]]:
    """
    Get 4 corner points untuk collision detection.

    Args:
        x, y: Posisi center motor
        angle: Sudut motor dalam radian

    Returns:
        List 4 tuple (x, y) untuk setiap corner
    """
    # Gunakan hitbox yang lebih kecil (40% dari ukuran asli)
    # untuk gameplay yang lebih forgiving
    length = self.length * 0.4
    width = self.width * 0.4

    corners = []

    # 4 corner: top-left, top-right, bottom-right, bottom-left
    for dx, dy in [(-length/2, -width/2),
                   (length/2, -width/2),
                   (length/2, width/2),
                   (-length/2, width/2)]:
        # Rotasi titik menggunakan rotation matrix
        rx = dx * math.cos(angle) - dy * math.sin(angle)
        ry = dx * math.sin(angle) + dy * math.cos(angle)
        corners.append((x + rx, y + ry))

    return corners
```

### Penjelasan Rotation Matrix

Untuk merotasi titik (dx, dy) dengan sudut theta:

```
rx = dx * cos(theta) - dy * sin(theta)
ry = dx * sin(theta) + dy * cos(theta)
```

Ini adalah rotation matrix 2D:

```
[rx]   [cos(theta)  -sin(theta)] [dx]
[ry] = [sin(theta)   cos(theta)] [dy]
```

### Diagram Collision Box

```
                  angle
                    |
                    v
        +----------->-----------+
        | TL                 TR |
        |                       |
        |           C           |  <- Center (x, y)
        |                       |
        | BL                 BR |
        +-----------------------+

Hitbox = 40% dari ukuran asli
- Lebih kecil untuk gameplay forgiving
- Motor terlihat nabrak tapi tidak langsung mati
```

---

## Method: check_masking_collision(x, y, angle)

Method utama untuk check collision menggunakan masking.

```python
def check_masking_collision(self, x: float, y: float,
                             angle: float) -> dict:
    """
    Check collision menggunakan masking surface.

    Args:
        x, y: Posisi center motor
        angle: Sudut motor dalam radian

    Returns:
        dict dengan informasi collision:
        - 'collided': bool - True jika nabrak wall
        - 'out_of_bounds': bool - True jika keluar map
        - 'slow_zone': bool - True jika di slow zone
        - 'checkpoint': int - Nomor checkpoint (0-4, 0 = bukan CP)
        - 'on_track': bool - True jika di track hitam
    """
    result = {
        'collided': False,
        'out_of_bounds': False,
        'slow_zone': False,
        'checkpoint': 0,
        'on_track': True
    }

    if self.masking_surface is None:
        return result

    # Get 4 corner points
    corners = self.get_collision_corners(x, y, angle)

    # Check setiap corner
    for corner in corners:
        cx, cy = int(corner[0]), int(corner[1])

        # BOUNDARY CHECK
        if (cx < 0 or cx >= self.masking_surface.get_width() or
            cy < 0 or cy >= self.masking_surface.get_height()):
            result['out_of_bounds'] = True
            result['collided'] = True
            return result

        # GET PIXEL COLOR
        color = self.masking_surface.get_at((cx, cy))
        r, g, b = color[0], color[1], color[2]

        # CLASSIFY ZONE
        zone = self._classify_color(r, g, b)

        if zone == 'wall':
            result['collided'] = True
            return result  # Early exit, sudah pasti collision
        elif zone == 'slow':
            result['slow_zone'] = True
        elif zone.startswith('cp'):
            # Extract checkpoint number dari "cp1", "cp2", dll
            result['checkpoint'] = int(zone[2])

    return result
```

### Penjelasan Alur

1. **Initialize result dict** dengan semua flag False/0
2. **Get corners** dari collision box yang sudah di-rotasi
3. **Untuk setiap corner**:
   - Check apakah di dalam bounds map
   - Get warna pixel di posisi tersebut
   - Classify warna ke zone
   - Update result berdasarkan zone
4. **Wall = early exit** karena sudah pasti collision
5. **Return result** untuk diproses oleh Motor

---

## Method: \_classify_color(r, g, b)

Klasifikasi warna RGB ke zone type.

```python
def _classify_color(self, r: int, g: int, b: int) -> str:
    """
    Klasifikasi warna dari masking pixel.

    Args:
        r, g, b: Nilai RGB (0-255)

    Returns:
        String zone type: 'track', 'wall', 'slow',
                          'cp1', 'cp2', 'cp3', 'cp4'
    """
    avg = (r + g + b) / 3

    # TRACK (hitam)
    if avg < 50:
        return 'track'

    # WALL (merah)
    # Merah dominan, hijau dan biru rendah
    if r > 150 and g < 100 and b < 100:
        return 'wall'

    # CHECKPOINT 1 (hijau)
    # Hijau dominan, merah dan biru rendah
    if g > 150 and r < 150 and b < 150 and g > r and g > b:
        return 'cp1'

    # CHECKPOINT 2 (cyan)
    # Hijau dan biru tinggi, merah rendah
    if g > 150 and b > 150 and r < 150:
        return 'cp2'

    # CHECKPOINT 3 (kuning)
    # Merah dan hijau tinggi, biru rendah
    if r > 150 and g > 150 and b < 150:
        return 'cp3'

    # CHECKPOINT 4 (magenta)
    # Merah dan biru tinggi, hijau rendah
    if r > 150 and b > 150 and g < 150:
        return 'cp4'

    # DEFAULT: slow zone
    # Termasuk putih, abu, atau warna lain
    return 'slow'
```

### Penjelasan Logic

Warna dicheck secara berurutan dengan priority:

1. **Track (hitam)** - Check pertama karena paling umum
2. **Wall (merah)** - Check kedua karena paling kritis
3. **Checkpoints** - Check berdasarkan kombinasi RGB
4. **Slow zone** - Default fallback

Threshold nilai 150 dan 100 dipilih untuk tolerance terhadap variasi warna.

---

## Method: get_surface_for_radar()

Mendapatkan surface yang digunakan untuk radar AI.

```python
def get_surface_for_radar(self) -> Optional[pygame.Surface]:
    """
    Get surface untuk radar raycast.

    Returns:
        masking_surface jika ada, otherwise track_surface

    Note:
        Radar prefer masking karena bisa mendeteksi wall
        dengan lebih akurat (hanya stop di merah).
    """
    return self.masking_surface or self.track_surface
```

---

## Penggunaan

```python
# Setup
collision = CollisionHandler(length=140, width=80)
collision.set_masking_surface(masking_surface)

# Check collision di posisi baru
result = collision.check_masking_collision(new_x, new_y, angle)

# Handle hasil
if result['collided']:
    # Wall collision
    if velocity > wall_explode_speed:
        # Motor meledak
        alive = False
    else:
        # Bounce back
        velocity = -velocity * 0.4
        x, y = prev_x, prev_y

elif result['slow_zone']:
    # Slow zone - kurangi speed
    velocity *= 0.99
    x, y = new_x, new_y

elif result['checkpoint'] > 0:
    # Checkpoint detected
    checkpoint_tracker.process_checkpoint(
        x, y,
        result['checkpoint'],
        current_time
    )
    x, y = new_x, new_y

else:
    # Track OK
    x, y = new_x, new_y
```
