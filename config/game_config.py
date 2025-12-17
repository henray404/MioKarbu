"""
Game Configuration
==================

Konfigurasi untuk game (main.py) dan training (train.py).
Edit nilai di sini untuk menyesuaikan game.
"""

# =============================================================================
# TRACK CONFIGURATION
# =============================================================================

# Track yang digunakan (nama file tanpa .png)
TRACK_NAME = "map-2"

# Scale track (1.0 = ukuran asli, 3.0 = 3x lebih besar)
TRACK_SCALE = 3.0

# Ukuran track original (untuk kalkulasi spawn)
ORIGINAL_TRACK_WIDTH = 2624
ORIGINAL_TRACK_HEIGHT = 1632


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
# DISPLAY CONFIGURATION
# =============================================================================

# Ukuran window (akan di-override jika fullscreen)
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960

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

def get_spawn_position(map_width: int, map_height: int) -> tuple:
    """
    Hitung posisi spawn berdasarkan ukuran map dan track yang dipilih.
    
    Args:
        map_width: Lebar map setelah di-scale
        map_height: Tinggi map setelah di-scale
        
    Returns:
        Tuple (spawn_x, spawn_y) yang sudah di-scale
    """
    # Pilih spawn berdasarkan track
    if TRACK_NAME == "new-4":
        base_x, base_y = SPAWN_X, SPAWN_Y
    elif TRACK_NAME == "map-2":
        base_x, base_y = SPAWN_X_2, SPAWN_Y_2
    else:
        # Default ke SPAWN_X/Y untuk track lainnya
        base_x, base_y = SPAWN_X, SPAWN_Y
    
    spawn_x = int(base_x * (map_width / ORIGINAL_TRACK_WIDTH))
    spawn_y = int(base_y * (map_height / ORIGINAL_TRACK_HEIGHT))
    return spawn_x, spawn_y


def get_finish_position(map_width: int, map_height: int) -> tuple:
    """
    Hitung posisi finish line berdasarkan ukuran map dan track yang dipilih.
    
    Args:
        map_width: Lebar map setelah di-scale
        map_height: Tinggi map setelah di-scale
        
    Returns:
        Tuple (finish_x, finish_y) yang sudah di-scale
    """
    # Pilih finish berdasarkan track
    if TRACK_NAME == "new-4":
        base_x, base_y = FINISH_X, FINISH_Y
    elif TRACK_NAME == "map-2":
        base_x, base_y = FINISH_X_2, FINISH_Y_2
    else:
        # Default ke FINISH_X/Y untuk track lainnya
        base_x, base_y = FINISH_X, FINISH_Y
    
    finish_x = int(base_x * (map_width / ORIGINAL_TRACK_WIDTH))
    finish_y = int(base_y * (map_height / ORIGINAL_TRACK_HEIGHT))
    return finish_x, finish_y


def get_masking_path(assets_dir: str) -> str:
    """
    Get full path ke file masking.
    
    Args:
        assets_dir: Path ke folder assets
        
    Returns:
        Full path ke masking file
    """
    import os
    return os.path.join(assets_dir, "tracks", MASKING_SUBFOLDER, MASKING_FILE)
