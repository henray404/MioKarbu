"""
Game Configuration
==================
Konfigurasi terpusat. 
"""

# =============================================================================
# GLOBAL SETTINGS
# =============================================================================

TRACK_SCALE = 3.0

TRACK_NAME = "new-4"

# Ukuran track original (default reference)
ORIGINAL_TRACK_WIDTH = 2624
ORIGINAL_TRACK_HEIGHT = 1632

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
FULLSCREEN = True

DEFAULT_TARGET_LAPS = 3
DEFAULT_AI_COUNT = 3
DEFAULT_MODEL = "winner_genome.pkl"
DEFAULT_MODEL_2 = "winner_map-2.pkl"
MASKING_SUBFOLDER = "masking"

# =============================================================================
# MAP CONFIGURATIONS
# =============================================================================

MAP_SETTINGS = {
    "map-2": {
        "track_file": "map-2",
        "masking_file": "ai_masking-5.png",
        "spawn_x": 1375,
        "spawn_y": 1220,
        "spawn_angle": 0,
        "model": "winner_map-2.pkl"
    },
    
    "new-4": {
        "track_file": "new-4",
        "masking_file": "ai_masking-4.png",
        "spawn_x": 1760,
        "spawn_y": 1380,
        "spawn_angle": 0,
        "model": "winner_genome.pkl"
    }
}

DEFAULT_MAP_KEY = "map-2"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_spawn_position(map_width: int, map_height: int, raw_x: int, raw_y: int) -> tuple:
    spawn_x = int(raw_x * (map_width / ORIGINAL_TRACK_WIDTH))
    spawn_y = int(raw_y * (map_height / ORIGINAL_TRACK_HEIGHT))
    return spawn_x, spawn_y