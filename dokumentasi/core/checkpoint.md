# checkpoint.py - Checkpoint Tracker

> Lokasi: `src/core/checkpoint.py`

---

## Deskripsi Umum

CheckpointTracker menangani sistem lap counting dan checkpoint tracking. Sistem ini menggunakan **sequential checkpoint system** dimana motor harus melewati checkpoint secara berurutan untuk lap yang valid.

### Mengapa Sequential System?

1. **Anti-cheat**: Mencegah shortcut atau jalan pintas
2. **Fair racing**: Semua motor harus melewati rute yang sama
3. **Validation**: Memastikan lap dilakukan dengan benar

---

## Class: CheckpointState

Dataclass untuk menyimpan state checkpoint dan lap.

```python
@dataclass
class CheckpointState:
    # === LAP INFO ===
    lap_count: int = 0              # Jumlah lap yang sudah complete
    lap_cooldown: int = 0           # Cooldown untuk mencegah double count
    has_left_start: bool = False    # Apakah sudah keluar dari start area

    # === TIMING ===
    lap_start_time: int = 0         # Frame saat lap dimulai
    last_lap_time: int = 0          # Waktu lap terakhir (dalam frames)
    best_lap_time: float = inf      # Best lap time (dalam frames)

    # === SEQUENTIAL CHECKPOINTS ===
    checkpoint_count: int = 0       # Checkpoint yang sudah dilewati
    expected_checkpoint: int = 1    # Next checkpoint yang diharapkan (1-4)
    total_checkpoints: int = 4      # Total checkpoint per lap
    checkpoints_for_lap: int = 4    # Minimal CP untuk lap valid

    # === CHECKPOINT TRACKING ===
    last_checkpoint_x: float = 0    # Posisi checkpoint terakhir
    last_checkpoint_y: float = 0
    last_checkpoint_time: int = 0   # Time saat lewat checkpoint terakhir
    on_checkpoint: bool = False     # Flag untuk debounce
    min_checkpoint_distance: float = 0  # Tidak dipakai di sequential

    # === FAILED ATTEMPTS ===
    failed_lap_checks: int = 0      # Counter gagal lap
    max_failed_lap_checks: int = 5  # Max gagal sebelum AI mati
```

---

## Class: CheckpointTracker

### Constructor

```python
def __init__(self, start_x: float, start_y: float):
    """
    Args:
        start_x, start_y: Posisi start/finish line
    """
    self.start_x = start_x
    self.start_y = start_y
    self.state = CheckpointState(
        last_checkpoint_x=start_x,
        last_checkpoint_y=start_y
    )

    # Thresholds
    self.leave_start_dist = 300   # Harus keluar 300 pixel dulu
    self.return_start_dist = 200  # Kembali dalam 200 pixel = finish
```

### Penjelasan Thresholds

- **leave_start_dist (300px)**: Motor harus keluar sejauh 300 pixel dari start sebelum lap mulai dihitung. Ini mencegah lap terhitung saat spawn.
- **return_start_dist (200px)**: Motor harus kembali dalam radius 200 pixel dari start untuk finish. Radius lebih kecil dari leave untuk mencegah false positive.

---

## Sequential Checkpoint Flow

```
+------------------------------------------------------------------+
|                   SEQUENTIAL CHECKPOINT SYSTEM                    |
+------------------------------------------------------------------+
|                                                                   |
|   START/FINISH                                                    |
|       |                                                           |
|       v                                                           |
|   [Keluar area start - 300px dari start]                          |
|       |                                                           |
|       |  has_left_start = True                                    |
|       |  lap_start_time = current_time                            |
|       |                                                           |
|       v                                                           |
|   CHECKPOINT 1 (Hijau)                                            |
|       |                                                           |
|       |  expected_checkpoint == 1? YES                            |
|       |  checkpoint_count = 1                                     |
|       |  expected_checkpoint = 2                                  |
|       |                                                           |
|       v                                                           |
|   CHECKPOINT 2 (Cyan)                                             |
|       |                                                           |
|       |  expected_checkpoint == 2? YES                            |
|       |  checkpoint_count = 2                                     |
|       |  expected_checkpoint = 3                                  |
|       |                                                           |
|       v                                                           |
|   CHECKPOINT 3 (Kuning)                                           |
|       |                                                           |
|       |  expected_checkpoint == 3? YES                            |
|       |  checkpoint_count = 3                                     |
|       |  expected_checkpoint = 4                                  |
|       |                                                           |
|       v                                                           |
|   CHECKPOINT 4 (Magenta)                                          |
|       |                                                           |
|       |  expected_checkpoint == 4? YES                            |
|       |  checkpoint_count = 4                                     |
|       |  expected_checkpoint = 1 (wrap around)                    |
|       |                                                           |
|       v                                                           |
|   [Kembali ke start - dalam 200px dari start]                     |
|       |                                                           |
|       |  checkpoint_count >= 4? YES                               |
|       |  LAP COMPLETE!                                            |
|       |  lap_count += 1                                           |
|       |  checkpoint_count = 0                                     |
|       |  expected_checkpoint = 1                                  |
|       |                                                           |
|       v                                                           |
|   [Repeat untuk lap berikutnya]                                   |
|                                                                   |
+------------------------------------------------------------------+
```

---

## Method: process_checkpoint(x, y, checkpoint_num, current_time)

Memproses saat motor melewati checkpoint.

```python
def process_checkpoint(self, x: float, y: float,
                        checkpoint_num: int,
                        current_time: int) -> bool:
    """
    Process saat motor melewati checkpoint.

    Args:
        x, y: Posisi motor saat ini
        checkpoint_num: Nomor checkpoint yang dilewati (1-4)
        current_time: Frame saat ini

    Returns:
        True jika checkpoint valid (urutan benar), False jika tidak
    """
    # Debounce - jangan process kalau masih di checkpoint sama
    if self.state.on_checkpoint:
        return False

    # CHECK URUTAN
    # Checkpoint harus sesuai dengan expected
    if checkpoint_num != self.state.expected_checkpoint:
        return False  # Checkpoint salah urutan, ignore

    # CHECK JARAK (opsional)
    dist_from_last = math.sqrt(
        (x - self.state.last_checkpoint_x)**2 +
        (y - self.state.last_checkpoint_y)**2
    )

    if dist_from_last < self.state.min_checkpoint_distance:
        return False

    # === VALID CHECKPOINT! ===

    # Update counter
    self.state.checkpoint_count += 1

    # Update timing
    self.state.last_checkpoint_time = current_time

    # Update position
    self.state.last_checkpoint_x = x
    self.state.last_checkpoint_y = y

    # Set debounce flag
    self.state.on_checkpoint = True

    # Update expected (wrap around: 4 -> 1)
    self.state.expected_checkpoint = (
        (self.state.expected_checkpoint % self.state.total_checkpoints) + 1
    )

    return True
```

### Penjelasan Logic

1. **Debounce**: Mencegah checkpoint terhitung berkali-kali saat motor masih di area checkpoint
2. **Sequential Check**: Checkpoint harus sesuai urutan. CP2 hanya valid setelah CP1.
3. **Wrap Around**: Setelah CP4, expected reset ke CP1 untuk lap berikutnya

---

## Method: clear_checkpoint_flag()

Membersihkan flag debounce saat motor keluar dari area checkpoint.

```python
def clear_checkpoint_flag(self) -> None:
    """
    Clear flag on_checkpoint saat motor keluar dari checkpoint area.
    Dipanggil dari Motor.update() saat result['checkpoint'] == 0
    """
    self.state.on_checkpoint = False
```

---

## Method: check_lap(x, y, current_time, invincible, debug_name)

Check apakah lap sudah complete.

```python
def check_lap(self, x: float, y: float, current_time: int,
              invincible: bool = False,
              debug_name: str = "AI") -> dict:
    """
    Check lap completion.

    Args:
        x, y: Posisi motor
        current_time: Frame saat ini
        invincible: True jika player (tidak mati walau gagal)
        debug_name: Nama untuk debug print

    Returns:
        dict:
        - 'completed': bool - True jika lap berhasil
        - 'failed': bool - True jika lap gagal (kurang checkpoint)
        - 'should_die': bool - True jika AI harus mati
        - 'lap_time': int - Waktu lap dalam frames
    """
    result = {
        'completed': False,
        'failed': False,
        'should_die': False,
        'lap_time': 0
    }

    # Cooldown untuk mencegah double count
    if self.state.lap_cooldown > 0:
        self.state.lap_cooldown -= 1
        return result

    # Hitung jarak dari start/finish
    dist_from_start = math.sqrt(
        (x - self.start_x)**2 +
        (y - self.start_y)**2
    )

    # CHECK: Apakah sudah keluar dari start area?
    if dist_from_start > self.leave_start_dist:  # 300px
        self.state.has_left_start = True

        # Mulai timer lap jika belum
        if self.state.lap_start_time == 0:
            self.state.lap_start_time = current_time

        return result  # Belum kembali ke start

    # CHECK: Apakah kembali ke start setelah keluar?
    if self.state.has_left_start and dist_from_start < self.return_start_dist:
        # Debug print
        who = "PLAYER" if invincible else debug_name
        print(f"[LAP CHECK] {who}: checkpoints="
              f"{self.state.checkpoint_count}/{self.state.checkpoints_for_lap}")

        # === CHECK CHECKPOINT REQUIREMENT ===
        if self.state.checkpoint_count >= self.state.checkpoints_for_lap:
            # LAP COMPLETE!
            lap_time = current_time - self.state.lap_start_time
            self.state.last_lap_time = lap_time

            # Update best lap
            if lap_time < self.state.best_lap_time:
                self.state.best_lap_time = lap_time

            # Increment lap count
            self.state.lap_count += 1

            # Debug print
            lap_time_seconds = lap_time / 60.0
            print(f"[LAP] {who} Lap {self.state.lap_count} completed! "
                  f"Time: {lap_time_seconds:.2f}s")

            # Cooldown dan reset untuk lap berikutnya
            self.state.lap_cooldown = 60  # 1 detik cooldown
            self._reset_for_next_lap(current_time)

            result['completed'] = True
            result['lap_time'] = lap_time

        else:
            # LAP FAILED - kurang checkpoint
            print(f"[LAP CHECK] {who} FAILED - "
                  f"need {self.state.checkpoints_for_lap} checkpoints, "
                  f"got {self.state.checkpoint_count}")

            self.state.failed_lap_checks += 1
            result['failed'] = True

            # AI mati setelah 5x gagal
            if (not invincible and
                self.state.failed_lap_checks >= self.state.max_failed_lap_checks):
                print(f"[AI KILLED] Too many failed lap attempts "
                      f"({self.state.failed_lap_checks})")
                result['should_die'] = True

        # Reset flag
        self.state.has_left_start = False

    return result
```

### Penjelasan Alur

1. **Cooldown Check**: Mencegah double count setelah lap complete
2. **Leave Check**: Motor harus keluar 300px dari start dulu
3. **Return Check**: Jika sudah keluar dan kembali dalam 200px
4. **Checkpoint Validation**: Minimal 4 checkpoint untuk valid
5. **Success/Fail**: Update counter dan reset untuk lap berikutnya

---

## Method: check_checkpoint_timeout(current_time, timeout_frames)

Check apakah motor stuck (terlalu lama tanpa checkpoint).

```python
def check_checkpoint_timeout(self, current_time: int,
                              timeout_frames: int = 3600) -> bool:
    """
    Check apakah timeout menunggu checkpoint berikutnya.

    Args:
        current_time: Frame saat ini
        timeout_frames: Max frames tanpa checkpoint
                       Default 3600 = 60 detik (60fps)

    Returns:
        True jika timeout (motor stuck), False jika OK
    """
    time_since_checkpoint = current_time - self.state.last_checkpoint_time
    return time_since_checkpoint > timeout_frames
```

---

## Method: reset(start_x, start_y)

Reset semua state untuk restart game.

```python
def reset(self, start_x: float = None, start_y: float = None) -> None:
    """
    Reset semua state.

    Args:
        start_x, start_y: Posisi start baru (optional)
    """
    if start_x is not None:
        self.start_x = start_x
    if start_y is not None:
        self.start_y = start_y

    # Reset state ke default
    self.state = CheckpointState(
        last_checkpoint_x=self.start_x,
        last_checkpoint_y=self.start_y
    )
```

---

## Penggunaan

```python
# Setup
checkpoint = CheckpointTracker(start_x=1000, start_y=500)

# Di game loop
# 1. Process checkpoint dari collision result
if collision_result['checkpoint'] > 0:
    valid = checkpoint.process_checkpoint(
        x, y,
        collision_result['checkpoint'],
        current_time
    )
    if valid:
        print(f"Checkpoint {collision_result['checkpoint']} OK!")
else:
    checkpoint.clear_checkpoint_flag()

# 2. Check lap status
lap_result = checkpoint.check_lap(x, y, current_time, invincible=True)

if lap_result['completed']:
    print(f"Lap complete! Time: {lap_result['lap_time']/60:.2f}s")
elif lap_result['failed']:
    print("Lap failed - tidak cukup checkpoint!")
elif lap_result['should_die']:
    motor.alive = False

# 3. Check timeout (untuk AI)
if checkpoint.check_checkpoint_timeout(current_time):
    print("Motor stuck - terlalu lama tanpa checkpoint!")
    motor.alive = False
```
