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
# SPAWN_X = 1800
# SPAWN_Y = 1380

SPAWN_X = 1375
SPAWN_Y = 1220

# Sudut spawn (dalam radian, 0 = menghadap kanan)
SPAWN_ANGLE = 0

# Posisi FINISH LINE (garis finish untuk lap counting)
# Jika sama dengan spawn, lap dihitung saat kembali ke spawn
# Jika berbeda, lap dihitung saat melewati titik ini
FINISH_X = 1800   # Ubah ini untuk finish line berbeda dari spawn
FINISH_Y = 1380   # Ubah ini untuk finish line berbeda dari spawn


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
DEFAULT_MODEL = "winner_genome.pkl"


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_spawn_position(map_width: int, map_height: int) -> tuple:
    """
    Hitung posisi spawn berdasarkan ukuran map.
    
    Args:
        map_width: Lebar map setelah di-scale
        map_height: Tinggi map setelah di-scale
        
    Returns:
        Tuple (spawn_x, spawn_y) yang sudah di-scale
    """
    spawn_x = int(SPAWN_X * (map_width / ORIGINAL_TRACK_WIDTH))
    spawn_y = int(SPAWN_Y * (map_height / ORIGINAL_TRACK_HEIGHT))
    return spawn_x, spawn_y


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
