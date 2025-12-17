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
    """
    Tracker untuk checkpoint dan lap counting.
    
    Features:
    - Sequential checkpoint system (harus urut)
    - Line-based finish detection
    - Lap timing
    - Failed lap detection
    """
    
    def __init__(self, start_x: float, start_y: float,
                 finish_line_start: tuple = None, finish_line_end: tuple = None):
        """
        Args:
            start_x, start_y: Posisi spawn (untuk leave detection)
            finish_line_start: (x, y) titik awal garis finish
            finish_line_end: (x, y) titik akhir garis finish
        """
        self.start_x = start_x
        self.start_y = start_y
        
        # Finish line coordinates
        if finish_line_start and finish_line_end:
            self.finish_line_start = finish_line_start
            self.finish_line_end = finish_line_end
        else:
            # Default: garis horizontal di spawn
            self.finish_line_start = (start_x - 100, start_y)
            self.finish_line_end = (start_x + 100, start_y)
        
        self.state = CheckpointState(
            last_checkpoint_x=start_x,
            last_checkpoint_y=start_y
        )
        
        # Thresholds
        self.leave_start_dist = 300   # Harus keluar 300 pixel dulu
        
        # Previous position for line crossing detection
        self.prev_x = start_x
        self.prev_y = start_y
    
    def _line_segments_intersect(self, p1, p2, p3, p4) -> bool:
        """
        Check if line segment p1-p2 intersects with line segment p3-p4.
        Uses cross product method.
        """
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        
        return (ccw(p1, p3, p4) != ccw(p2, p3, p4)) and (ccw(p1, p2, p3) != ccw(p1, p2, p4))
    
    def crossed_finish_line(self, x: float, y: float) -> bool:
        """
        Check if motor crossed the finish line since last position.
        """
        crossed = self._line_segments_intersect(
            (self.prev_x, self.prev_y),
            (x, y),
            self.finish_line_start,
            self.finish_line_end
        )
        # Update previous position
        self.prev_x = x
        self.prev_y = y
        return crossed
    
    def process_checkpoint(self, x: float, y: float, checkpoint_num: int, 
                          current_time: int) -> bool:
        """
        Process saat motor melewati checkpoint.
        """
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
        """
        Check lap completion using line crossing.
        
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
            # Still update prev position
            self.prev_x = x
            self.prev_y = y
            return result
        
        dist_from_start = math.sqrt(
            (x - self.start_x)**2 + 
            (y - self.start_y)**2
        )
        
        # Check if left start area
        if not self.state.has_left_start:
            if dist_from_start > self.leave_start_dist:
                self.state.has_left_start = True
                if self.state.lap_start_time == 0:
                    self.state.lap_start_time = current_time
            # Update prev position
            self.prev_x = x
            self.prev_y = y
            return result
        
        # Check if crossed finish line
        if self.crossed_finish_line(x, y):
            who = "PLAYER" if invincible else debug_name
            print(f"[FINISH LINE] {who}: checkpoints={self.state.checkpoint_count}/{self.state.checkpoints_for_lap}")
            
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
                print(f"[FINISH LINE] {who} FAILED - need {self.state.checkpoints_for_lap} checkpoints, got {self.state.checkpoint_count}")
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
        if start_x: self.start_x = start_x
        if start_y: self.start_y = start_y
        self.state = CheckpointState()