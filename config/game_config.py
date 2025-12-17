"""
Game Configuration
==================
Konfigurasi terpusat. Edit koordinat map di dictionary MAP_SETTINGS di bawah.
"""

# =============================================================================
# GLOBAL SETTINGS
# =============================================================================

# Scale track (1.0 = ukuran asli, 3.0 = 3x lebih besar)
TRACK_SCALE = 3.0

TRACK_NAME = "new-4"

# Ukuran track original (default reference)
ORIGINAL_TRACK_WIDTH = 2624
ORIGINAL_TRACK_HEIGHT = 1632

# Display
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
FULLSCREEN = True

# =============================================================================
# SPAWN CONFIGURATION
# =============================================================================

# Posisi spawn pada track ORIGINAL (sebelum di-scale)
# Posisi ini akan di-scale berdasarkan rasio map
SPAWN_X = 1800
SPAWN_Y = 1380

SPAWN_X_2 = 1375
SPAWN_Y_2 = 1220

# Sudut spawn (dalam radian, 0 = menghadap kanan)
SPAWN_ANGLE = 0

# Posisi FINISH LINE (GARIS finish untuk lap counting)
# Sistem baru: garis antara 2 titik (start -> end)
# Motor dianggap finish saat melewati garis ini

# Map: new-4 (garis vertikal dari atas ke bawah)
FINISH_LINE_START_X = 1800   # X sama = garis vertikal
FINISH_LINE_START_Y = 1280   # Titik atas
FINISH_LINE_END_X = 1800     # X sama = garis vertikal
FINISH_LINE_END_Y = 1680     # Titik bawah

# Map: map-2 (garis vertikal dari atas ke bawah)
FINISH_LINE_START_X_2 = 1675   # X sama = garis vertikal
FINISH_LINE_START_Y_2 = 1120   # Titik atas
FINISH_LINE_END_X_2 = 1675     # X sama = garis vertikal
FINISH_LINE_END_Y_2 = 1820     # Titik bawah


# =============================================================================
# MASKING CONFIGURATION
# =============================================================================

# Nama file masking (di folder assets/tracks/masking/)
MASKING_FILE = "ai_masking-5.png"

# Subfolder masking (relatif ke assets/tracks/)
MASKING_SUBFOLDER = "masking"


# =============================================================================
# MAP CONFIGURATIONS (DATABASE MAP)
# =============================================================================
# Tambahkan map baru atau edit koordinat spawn di sini.

MAP_SETTINGS = {
    "map-2": {
        "track_file": "map-2",           # Nama file gambar track
        "masking_file": "ai_masking-5.png", # Nama file masking
        "spawn_x": 1375,                 # Koordinat X Spawn
        "spawn_y": 1220,                 # Koordinat Y Spawn
        "spawn_angle": 0,                # Sudut hadap (0 = Kanan)
        "finish_x": 1800,                # Garis finish X
        "finish_y": 1380                 # Garis finish Y
    },
    
    "new-4": {
        "track_file": "new-4",
        "masking_file": "ai_masking-4.png",
        
        # --- KONFIGURASI INI YANG NANTI KAMU EDIT ---
        "spawn_x": 1800,                  # <--- Ganti dengan koordinat spawn new-4
        "spawn_y": 1380,                  # <--- Ganti dengan koordinat spawn new-4
        "spawn_angle": 0,               # <--- Ganti sudut (90 = Bawah)
        "finish_x": 1800,                 # <--- Ganti finish line
        "finish_y": 1380                  # <--- Ganti finish line
        # --------------------------------------------
    }
}

# Fullscreen mode (True = pakai resolusi layar)
FULLSCREEN = True


# =============================================================================
# GAME SETTINGS
# =============================================================================

# Target lap untuk menang
DEFAULT_TARGET_LAPS = 3

# Jumlah AI default
DEFAULT_AI_COUNT = 3

# Default model AI
DEFAULT_MODEL = "winner_map-2.pkl"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_spawn_position(map_width: int, map_height: int, raw_x: int, raw_y: int) -> tuple:
    """
    Hitung posisi spawn scale berdasarkan koordinat RAW dari config.
    """
    spawn_x = int(raw_x * (map_width / ORIGINAL_TRACK_WIDTH))
    spawn_y = int(raw_y * (map_height / ORIGINAL_TRACK_HEIGHT))
    return spawn_x, spawn_y

def get_masking_path(assets_dir: str, filename: str) -> str:
    import os
    return os.path.join(assets_dir, "tracks", MASKING_SUBFOLDER, filename)