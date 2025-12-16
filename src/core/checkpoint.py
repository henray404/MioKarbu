"""
Checkpoint Module untuk Motor
=============================

Mengandung logic untuk lap counting dan checkpoint tracking.
Digunakan dengan composition pattern oleh Motor class.
"""

import math
from dataclasses import dataclass, field


@dataclass
class CheckpointState:
    """
    State untuk checkpoint dan lap tracking.
    """
    # Lap
    lap_count: int = 0
    lap_cooldown: int = 0
    has_left_start: bool = False
    
    # Timing
    lap_start_time: int = 0       # Frame saat lap dimulai
    last_lap_time: int = 0        # Waktu lap terakhir (frames)
    best_lap_time: float = float('inf')
    
    # Sequential checkpoints
    checkpoint_count: int = 0     # Checkpoints passed dalam lap ini
    expected_checkpoint: int = 1  # Next expected checkpoint (1-4)
    total_checkpoints: int = 4    # Total per lap
    checkpoints_for_lap: int = 4  # Harus lewat semua untuk valid
    
    # Checkpoint position tracking
    last_checkpoint_x: float = 0
    last_checkpoint_y: float = 0
    last_checkpoint_time: int = 0
    on_checkpoint: bool = False
    min_checkpoint_distance: float = 0  # Sequential = tidak perlu jarak
    
    # Failed attempts
    failed_lap_checks: int = 0
    max_failed_lap_checks: int = 5


class CheckpointTracker:
    """
    Tracker untuk checkpoint dan lap counting.
    
    Features:
    - Sequential checkpoint system (harus urut)
    - Lap timing
    - Failed lap detection
    """
    
    def __init__(self, start_x: float, start_y: float):
        """
        Args:
            start_x, start_y: Posisi start/finish
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
    
    def process_checkpoint(self, x: float, y: float, checkpoint_num: int, 
                          current_time: int) -> bool:
        """
        Process saat motor melewati checkpoint.
        
        Args:
            x, y: Posisi motor
            checkpoint_num: Nomor checkpoint (1-4)
            current_time: Frame saat ini
            
        Returns:
            True jika checkpoint valid (urutan benar)
        """
        if self.state.on_checkpoint:
            return False
        
        if checkpoint_num != self.state.expected_checkpoint:
            return False
        
        # Check jarak dari checkpoint terakhir
        dist_from_last = math.sqrt(
            (x - self.state.last_checkpoint_x)**2 +
            (y - self.state.last_checkpoint_y)**2
        )
        
        if dist_from_last < self.state.min_checkpoint_distance:
            return False
        
        # Valid checkpoint!
        self.state.checkpoint_count += 1
        self.state.last_checkpoint_time = current_time
        self.state.last_checkpoint_x = x
        self.state.last_checkpoint_y = y
        self.state.on_checkpoint = True
        
        # Update expected (wrap around 4 -> 1)
        self.state.expected_checkpoint = (self.state.expected_checkpoint % self.state.total_checkpoints) + 1
        
        return True
    
    def clear_checkpoint_flag(self) -> None:
        """Clear flag on_checkpoint saat keluar dari area checkpoint."""
        self.state.on_checkpoint = False
    
    def check_lap(self, x: float, y: float, current_time: int, 
                  invincible: bool = False, debug_name: str = "AI") -> dict:
        """
        Check lap completion.
        
        Args:
            x, y: Posisi motor
            current_time: Frame saat ini
            invincible: True jika player (tidak mati)
            debug_name: Nama untuk debug print
            
        Returns:
            dict dengan 'completed', 'failed', 'should_die'
        """
        result = {
            'completed': False,
            'failed': False,
            'should_die': False,
            'lap_time': 0
        }
        
        if self.state.lap_cooldown > 0:
            self.state.lap_cooldown -= 1
            return result
        
        dist_from_start = math.sqrt(
            (x - self.start_x)**2 + 
            (y - self.start_y)**2
        )
        
        # Check if left start area
        if dist_from_start > self.leave_start_dist:
            self.state.has_left_start = True
            if self.state.lap_start_time == 0:
                self.state.lap_start_time = current_time
            return result
        
        # Check if returned to start
        if self.state.has_left_start and dist_from_start < self.return_start_dist:
            who = "PLAYER" if invincible else debug_name
            print(f"[LAP CHECK] {who}: checkpoints={self.state.checkpoint_count}/{self.state.checkpoints_for_lap}")
            
            if self.state.checkpoint_count >= self.state.checkpoints_for_lap:
                # Lap completed!
                lap_time = current_time - self.state.lap_start_time
                self.state.last_lap_time = lap_time
                if lap_time < self.state.best_lap_time:
                    self.state.best_lap_time = lap_time
                
                self.state.lap_count += 1
                lap_time_seconds = lap_time / 60.0
                print(f"[LAP] {who} Lap {self.state.lap_count} completed! Time: {lap_time_seconds:.2f}s")
                
                self.state.lap_cooldown = 60
                self._reset_for_next_lap(current_time)
                
                result['completed'] = True
                result['lap_time'] = lap_time
            else:
                print(f"[LAP CHECK] {who} FAILED - need {self.state.checkpoints_for_lap} checkpoints, got {self.state.checkpoint_count}")
                self.state.failed_lap_checks += 1
                result['failed'] = True
                
                if not invincible and self.state.failed_lap_checks >= self.state.max_failed_lap_checks:
                    print(f"[AI KILLED] Too many failed lap attempts ({self.state.failed_lap_checks})")
                    result['should_die'] = True
            
            self.state.has_left_start = False
        
        return result
    
    def _reset_for_next_lap(self, current_time: int) -> None:
        """Reset state untuk lap berikutnya."""
        self.state.checkpoint_count = 0
        self.state.expected_checkpoint = 1
        self.state.lap_start_time = current_time
        self.state.failed_lap_checks = 0
    
    def check_checkpoint_timeout(self, current_time: int, timeout_frames: int = 3600) -> bool:
        """
        Check apakah timeout menunggu checkpoint berikutnya.
        
        Args:
            current_time: Frame saat ini
            timeout_frames: Max frames tanpa checkpoint (default 60s * 60fps)
            
        Returns:
            True jika timeout
        """
        time_since_checkpoint = current_time - self.state.last_checkpoint_time
        return time_since_checkpoint > timeout_frames
    
    def reset(self, start_x: float = None, start_y: float = None) -> None:
        """Reset semua state."""
        if start_x is not None:
            self.start_x = start_x
        if start_y is not None:
            self.start_y = start_y
        
        self.state = CheckpointState(
            last_checkpoint_x=self.start_x,
            last_checkpoint_y=self.start_y
        )
