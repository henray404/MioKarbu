# physics.py - Physics Engine

> Lokasi: `src/core/physics.py`

---

## Deskripsi Umum

Modul physics mengandung semua konstanta dan kalkulasi fisika untuk motor. Terdiri dari tiga class:

1. **PhysicsConfig**: Dataclass yang menyimpan konstanta fisika
2. **PhysicsState**: Dataclass yang menyimpan state fisika yang berubah setiap frame
3. **PhysicsEngine**: Class utama yang melakukan kalkulasi

Pemisahan config dan state memudahkan reset tanpa kehilangan konfigurasi.

---

## Class PhysicsConfig

Dataclass untuk menyimpan konstanta fisika. Semua nilai sudah dioptimasi untuk gameplay yang fun tapi tetap realistis.

```python
@dataclass
class PhysicsConfig:
    # === SPEED & ACCELERATION ===
    acceleration_rate: float = 0.12  # Akselerasi per frame
    brake_power: float = 0.25        # Kekuatan rem (lebih besar dari akselerasi)
    friction: float = 0.985          # Gesekan natural (mendekati 1 = mulus)
    max_speed: float = 20.0          # Kecepatan maksimum

    # === STEERING ===
    base_steering_rate: float = 4.5  # Derajat per frame saat lambat/diam
    min_steering_rate: float = 1.2   # Derajat per frame saat max speed

    # === GRIP & TRACTION ===
    base_grip: float = 1.0           # Grip default (0.0 - 1.0)
    turn_grip_loss: float = 0.15     # Grip loss saat belok tajam
    speed_grip_factor: float = 0.7   # Grip di kecepatan tinggi

    # === TURN PHYSICS ===
    turn_speed_penalty: float = 0.02  # Kehilangan speed saat belok (2%)
    sharp_turn_threshold: float = 0.5 # Threshold belok tajam
    understeer_factor: float = 0.3    # Understeer di speed tinggi (30%)

    # === INERTIA ===
    lateral_friction: float = 0.92    # Gesekan lateral untuk slide

    # === DIMENSIONS ===
    length: float = 140.0
    width: float = 80.0

    # === COLLISION ===
    wall_explode_speed: float = 8.0   # Speed threshold untuk explode
```

### Penjelasan Parameter

**Speed & Acceleration**

- `acceleration_rate`: Nilai yang ditambahkan ke velocity setiap frame saat gas. Nilai 0.12 berarti butuh sekitar 1.5 detik dari diam ke max speed.
- `brake_power`: Nilai yang dikurangkan saat rem. Lebih besar dari akselerasi untuk rem yang responsif.
- `friction`: Pengali velocity saat tidak ada input. Nilai 0.985 berarti kehilangan 1.5% speed per frame.
- `max_speed`: Batas kecepatan maksimum. Velocity tidak akan melebihi nilai ini.

**Steering**

- `base_steering_rate`: Seberapa tajam bisa belok saat kecepatan rendah. 4.5 derajat per frame = sangat responsif.
- `min_steering_rate`: Seberapa tajam bisa belok saat kecepatan maksimum. 1.2 derajat per frame = lebih sulit belok.

**Grip & Traction**

- `base_grip`: Nilai grip default. Grip mempengaruhi efektivitas steering.
- `turn_grip_loss`: Seberapa banyak grip hilang saat belok tajam di speed tinggi.
- `speed_grip_factor`: Faktor pengali grip berdasarkan kecepatan.

**Turn Physics**

- `turn_speed_penalty`: Persentase speed yang hilang saat belok. 0.02 = 2% per frame.
- `understeer_factor`: Seberapa besar motor cenderung lurus di speed tinggi. 0.3 = 30% understeer.

---

## Class PhysicsState

Dataclass untuk state yang berubah setiap frame.

```python
@dataclass
class PhysicsState:
    velocity: float = 0.0           # Kecepatan saat ini
    lateral_velocity: float = 0.0   # Kecepatan samping (untuk slide)
    grip: float = 1.0               # Grip saat ini
    weight_transfer: float = 0.0    # Transfer berat saat gas/rem
    steering_rate: float = 4.5      # Steering rate saat ini (dynamic)

    # Drift
    drift_angle: float = 0.0        # Sudut drift dalam radian
    is_drifting: bool = False       # Flag mode drift
    drift_direction: int = 0        # -1 (kanan) atau 1 (kiri)
```

---

## Class PhysicsEngine

Engine utama untuk semua kalkulasi fisika.

### Constructor

```python
def __init__(self, config: PhysicsConfig = None):
    self.config = config or PhysicsConfig()
    self.state = PhysicsState(steering_rate=self.config.base_steering_rate)
```

---

### Method: calculate_steering_rate()

Menghitung steering rate berdasarkan kecepatan saat ini. Semakin cepat motor, semakin sulit untuk belok.

```python
def calculate_steering_rate(self) -> float:
    # Hitung rasio kecepatan (0.0 sampai 1.0)
    speed_ratio = abs(self.state.velocity) / self.config.max_speed

    # Interpolasi linear dari base ke min
    return self.config.base_steering_rate - (
        (self.config.base_steering_rate - self.config.min_steering_rate)
        * speed_ratio
    )
```

#### Rumus Matematika

```
steering_rate = base - (base - min) * speed_ratio

Dimana:
- base = 4.5 (derajat/frame)
- min = 1.2 (derajat/frame)
- speed_ratio = velocity / max_speed
```

#### Tabel Contoh

| Velocity | Speed Ratio | Steering Rate  | Penjelasan                           |
| -------- | ----------- | -------------- | ------------------------------------ |
| 0        | 0.0         | 4.5 deg/frame  | Saat diam, steering sangat responsif |
| 10       | 0.5         | 2.85 deg/frame | Di setengah speed, steering menengah |
| 20       | 1.0         | 1.2 deg/frame  | Di max speed, steering paling berat  |

#### Visualisasi

```
Steering Rate
     ^
 4.5 |*
     |  *
     |    *
 2.85|     *
     |       *
     |         *
 1.2 |           *
     +-------------->
     0    0.5    1.0  Speed Ratio
```

---

### Method: apply_acceleration(throttle)

Mengaplikasikan akselerasi atau rem dengan drag effect.

```python
def apply_acceleration(self, throttle: float) -> None:
    throttle = max(-1, min(1, throttle))  # Clamp ke -1 sampai 1

    if throttle > 0:
        # AKSELERASI
        # Drag effect: akselerasi berkurang di speed tinggi
        speed_ratio = abs(self.state.velocity) / self.config.max_speed
        accel_modifier = 1.0 - (speed_ratio * 0.5)

        self.state.velocity += (
            self.config.acceleration_rate * throttle * accel_modifier
        )
        self.state.weight_transfer = 0.3  # Weight ke belakang

    elif throttle < 0:
        # REM
        self.state.velocity -= self.config.brake_power
        self.state.weight_transfer = -0.5  # Weight ke depan

    else:
        # TIDAK ADA INPUT - friction
        self.state.velocity *= self.config.friction
        self.state.weight_transfer *= 0.9  # Weight decay

    # Clamp velocity ke range valid
    self.state.velocity = max(
        -self.config.max_speed * 0.5,  # Mundur max 50% dari max speed
        min(self.config.max_speed, self.state.velocity)
    )
```

#### Rumus Drag Effect

```
effective_acceleration = base_acceleration * (1 - speed_ratio * 0.5)

Contoh:
- Di 0% speed: effective = base * 1.0 = 100% akselerasi
- Di 50% speed: effective = base * 0.75 = 75% akselerasi
- Di 100% speed: effective = base * 0.5 = 50% akselerasi
```

#### Penjelasan Drag

Drag effect mensimulasikan hambatan udara. Di dunia nyata, semakin cepat kendaraan bergerak, semakin besar hambatan udara yang harus dilawan. Ini menghasilkan kurva akselerasi yang natural dimana butuh waktu lebih lama untuk menambah kecepatan di range atas.

---

### Method: apply_steering(steering_input, is_drifting)

Menghitung perubahan angle berdasarkan input steering.

```python
def apply_steering(self, steering_input: float,
                   is_drifting: bool = False) -> float:
    self.state.is_drifting = is_drifting

    # Tidak bisa belok kalau tidak bergerak
    if abs(self.state.velocity) <= 0.1:
        return 0.0

    speed_ratio = abs(self.state.velocity) / self.config.max_speed

    if is_drifting and steering_input != 0:
        # === MODE DRIFT ===
        return self._apply_drift_steering(steering_input, speed_ratio)
    else:
        # === MODE NORMAL ===
        return self._apply_normal_steering(steering_input, speed_ratio)
```

#### Normal Steering

```python
def _apply_normal_steering(self, steering_input, speed_ratio):
    # Hitung steering rate berdasarkan speed
    self.state.steering_rate = self.calculate_steering_rate()
    steer_amount = math.radians(self.state.steering_rate) * steering_input

    # UNDERSTEER
    # Di speed tinggi, motor cenderung lurus
    understeer = 1.0 - (speed_ratio * self.config.understeer_factor)
    angle_change = steer_amount * understeer

    # SPEED PENALTY
    # Kehilangan speed saat belok
    if abs(steering_input) > 0:
        turn_intensity = abs(steering_input) * speed_ratio
        speed_loss = self.config.turn_speed_penalty * turn_intensity
        self.state.velocity *= (1.0 - speed_loss)

    # GRIP RECOVERY
    self.state.grip = min(self.config.base_grip, self.state.grip + 0.02)

    # DECAY DRIFT
    self.state.drift_angle *= 0.85
    self.state.lateral_velocity *= self.config.lateral_friction

    return angle_change
```

#### Rumus Understeer

```
effective_steer = base_steer * (1 - speed_ratio * understeer_factor)

Dengan understeer_factor = 0.3:
- Di 0% speed: effective = base * 1.0 = 100% steering
- Di 50% speed: effective = base * 0.85 = 85% steering
- Di 100% speed: effective = base * 0.7 = 70% steering
```

#### Penjelasan Understeer

Understeer adalah fenomena dimana kendaraan tidak berbelok se-tajam yang diinginkan. Ini terjadi karena ban depan kehilangan traksi di kecepatan tinggi. Dalam game, ini membuat player harus melambat sebelum tikungan untuk berbelok efektif.

#### Drift Steering

```python
def _apply_drift_steering(self, steering_input, speed_ratio):
    self.state.drift_direction = int(steering_input)

    # Steering lebih tajam saat drift (150% dari base)
    drift_steer = self.config.base_steering_rate * 1.5
    angle_change = math.radians(drift_steer) * steering_input

    # Build up drift angle (sliding effect)
    max_drift = 0.5  # ~28 derajat maksimum
    self.state.drift_angle += steering_input * 0.08
    self.state.drift_angle = max(-max_drift,
                                  min(max_drift, self.state.drift_angle))

    # Speed penalty saat drift
    self.state.velocity *= 0.995

    # Lose grip saat drift
    self.state.grip = max(0.3, self.state.grip - 0.05)

    # Build lateral velocity (sliding)
    self.state.lateral_velocity += steering_input * 0.5

    return angle_change
```

---

### Method: calculate_movement(angle)

Menghitung delta posisi berdasarkan angle dan velocity.

```python
def calculate_movement(self, angle: float) -> Tuple[float, float]:
    # Saat drift, arah gerak berbeda dari arah hadap
    if self.state.is_drifting:
        move_angle = angle + self.state.drift_angle
    else:
        move_angle = angle

    # Hitung komponen x dan y
    dx = math.cos(move_angle) * self.state.velocity
    dy = math.sin(move_angle) * self.state.velocity

    return dx, dy
```

#### Rumus Movement

```
dx = cos(angle) * velocity
dy = sin(angle) * velocity

Dengan drift:
dx = cos(angle + drift_angle) * velocity
dy = sin(angle + drift_angle) * velocity
```

#### Penjelasan

Rumus ini mengkonversi kecepatan skalar dan sudut menjadi vektor 2D. Komponen x dan y dihitung menggunakan trigonometri dasar:

- cos(angle) memberikan komponen horizontal
- sin(angle) memberikan komponen vertikal
- Dikali velocity untuk magnitude

---

### Method: get_speed_kmh()

Mengkonversi velocity internal ke km/h untuk display speedometer.

```python
def get_speed_kmh(self) -> int:
    return int(abs(self.state.velocity) * 7.5)
```

#### Konversi

| Velocity | Speed (km/h) |
| -------- | ------------ |
| 0        | 0            |
| 10       | 75           |
| 20       | 150          |
| 30       | 225          |

---

### Method: reset()

Reset semua state ke default tanpa mengubah config.

```python
def reset(self) -> None:
    self.state = PhysicsState(
        steering_rate=self.config.base_steering_rate
    )
```

---

## Diagram Alur Physics

```
+------------------------------------------------------------------+
|                      PHYSICS ENGINE FLOW                          |
+------------------------------------------------------------------+
|                                                                   |
|  INPUT (throttle, steering)                                       |
|      |                                                            |
|      v                                                            |
|  apply_acceleration(throttle)                                     |
|      |                                                            |
|      +--> throttle > 0: Akselerasi dengan drag                    |
|      |       - Hitung speed_ratio                                 |
|      |       - Hitung accel_modifier = 1 - speed_ratio * 0.5      |
|      |       - velocity += accel * throttle * modifier            |
|      |                                                            |
|      +--> throttle < 0: Rem                                       |
|      |       - velocity -= brake_power                            |
|      |                                                            |
|      +--> throttle = 0: Friction                                  |
|              - velocity *= friction                               |
|      |                                                            |
|      v                                                            |
|  calculate_steering_rate()                                        |
|      |                                                            |
|      +--> rate = base - (base - min) * speed_ratio                |
|      |                                                            |
|      v                                                            |
|  apply_steering(steering, drift)                                  |
|      |                                                            |
|      +--> Normal mode:                                            |
|      |       - Hitung angle_change dengan steering_rate           |
|      |       - Apply understeer di speed tinggi                   |
|      |       - Apply speed penalty saat belok                     |
|      |                                                            |
|      +--> Drift mode:                                             |
|              - Steering 150% lebih tajam                          |
|              - Build drift_angle                                  |
|              - Speed penalty dan grip loss                        |
|      |                                                            |
|      v                                                            |
|  calculate_movement(angle)                                        |
|      |                                                            |
|      +--> dx = cos(angle) * velocity                              |
|      +--> dy = sin(angle) * velocity                              |
|      |                                                            |
|      v                                                            |
|  OUTPUT (dx, dy)                                                  |
|                                                                   |
+------------------------------------------------------------------+
```
