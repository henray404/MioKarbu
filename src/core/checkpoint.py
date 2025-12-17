"""
Checkpoint Module untuk Motor (Fixed Logic - Start 0)
=====================================================
"""

import math
from dataclasses import dataclass

@dataclass
class CheckpointState:
    """State untuk checkpoint dan lap tracking."""
    # Lap Data
    lap_count: int = 0            # Start 0
    current_lap_time: int = 0
    
    # Checkpoint Data
    checkpoint_count: int = 0     
    expected_checkpoint: int = 1  
    total_checkpoints: int = 4    
    
    # Timing & Position
    last_checkpoint_time: int = 0
    on_checkpoint: bool = False   
    
    # Lap Timing
    lap_start_time: int = 0
    best_lap_time: float = float('inf')


class CheckpointTracker:
    def __init__(self, start_x: float, start_y: float):
        self.state = CheckpointState()
        self.start_x = start_x
        self.start_y = start_y
        
    def process_checkpoint(self, x: float, y: float, checkpoint_num: int, current_time: int) -> bool:
        """Dipanggil saat motor menyentuh warna checkpoint."""
        
        if self.state.on_checkpoint:
            return False

        if checkpoint_num != self.state.expected_checkpoint:
            return False

        # --- LOGIKA VALIDASI OK ---
        self.state.on_checkpoint = True 
        self.state.last_checkpoint_time = current_time
        
        # TRANSISI LAP (Dari CP Terakhir ke CP 1)
        if checkpoint_num == 1 and self.state.checkpoint_count >= self.state.total_checkpoints:
            self._handle_lap_complete(current_time)
            print(f"[LAP] FINISH! New Lap Count: {self.state.lap_count}")
            return True

        # Checkpoint Biasa
        self.state.checkpoint_count += 1
        self.state.expected_checkpoint = (self.state.expected_checkpoint % self.state.total_checkpoints) + 1
        
        print(f"[CP] Passed CP-{checkpoint_num}. Next: {self.state.expected_checkpoint}")
        return True

    def _handle_lap_complete(self, current_time: int):
        """Logic saat Lap selesai."""
        lap_time = current_time - self.state.lap_start_time
        
        if lap_time < self.state.best_lap_time and self.state.lap_count > 0:
            self.state.best_lap_time = lap_time
            
        # Update Lap Count
        self.state.lap_count += 1
        
        # Reset State untuk Lap Baru
        self.state.checkpoint_count = 1  
        self.state.expected_checkpoint = 2 
        self.state.lap_start_time = current_time

    def clear_checkpoint_flag(self) -> None:
        self.state.on_checkpoint = False

    def check_lap(self, x: float, y: float, current_time: int, 
                  invincible: bool = False, debug_name: str = "AI") -> dict:
        return {'completed': False, 'failed': False, 'should_die': False}

    def reset(self, start_x: float = None, start_y: float = None) -> None:
        if start_x: self.start_x = start_x
        if start_y: self.start_y = start_y
        self.state = CheckpointState()