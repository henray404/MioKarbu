import math
from dataclasses import dataclass

@dataclass
class CheckpointState:
    """State untuk checkpoint dan lap tracking."""
    # Lap Data
    lap_count: int = 0           
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
        self.start_x = start_x
        self.start_y = start_y
        
        # Init state bersih tanpa parameter koordinat aneh-aneh
        self.state = CheckpointState()
        
    def process_checkpoint(self, x: float, y: float, checkpoint_num: int, current_time: int) -> bool:
        """
        Dipanggil saat motor menyentuh warna checkpoint.
        
        Logic:
        - Jika urutan benar (1->2->3->4), terima.
        - Jika transisi dari 4 -> 1, HITUNG SEBAGAI LAP BARU.
        """
        # 1. Cegah spamming (motor masih nempel di warna checkpoint yg sama)
        if self.state.on_checkpoint:
            return False

        # 2. Validasi Urutan (Harus sesuai expected)
        if checkpoint_num != self.state.expected_checkpoint:
            return False

        # --- LOGIKA VALIDASI OK ---
        
        self.state.on_checkpoint = True 
        self.state.last_checkpoint_time = current_time
        
        # KASUS SPESIAL: TRANSISI LAP (Dari CP Terakhir ke CP 1)
        # Jika kita mengharapkan CP 1, dan kita sudah melewati minimal 4 checkpoint sebelumnya
        if checkpoint_num == 1 and self.state.checkpoint_count >= self.state.total_checkpoints:
            self._handle_lap_complete(current_time)
            print(f"[LAP] FINISH! New Lap Count: {self.state.lap_count}")
            return True

        # KASUS NORMAL: Checkpoint Biasa (1->2, 2->3, 3->4)
        self.state.checkpoint_count += 1
        self.state.expected_checkpoint = (self.state.expected_checkpoint % self.state.total_checkpoints) + 1
        
        print(f"[CP] Passed CP-{checkpoint_num}. Next: {self.state.expected_checkpoint}")
        return True

    def _handle_lap_complete(self, current_time: int):
        """Logic saat Lap selesai."""
        # 1. Hitung Waktu Lap
        lap_time = current_time - self.state.lap_start_time
        
        if lap_time < self.state.best_lap_time and self.state.lap_count > 0:
            self.state.best_lap_time = lap_time
            
        # 2. Update Lap Count
        self.state.lap_count += 1
        
        # 3. Reset State untuk Lap Baru
        self.state.checkpoint_count = 1  # Reset: kita baru saja lewat CP 1
        self.state.expected_checkpoint = 2 # Target berikutnya CP 2
        self.state.lap_start_time = current_time

    def clear_checkpoint_flag(self) -> None:
        """Dipanggil saat motor KELUAR dari area warna masking."""
        self.state.on_checkpoint = False

    def check_lap(self, x: float, y: float, current_time: int, 
                  invincible: bool = False, debug_name: str = "AI") -> dict:
        """
        [Dummy Function]
        Dipertahankan agar tidak error di motor.py yang memanggil fungsi ini.
        Logic lap yang asli sudah pindah ke `process_checkpoint`.
        """
        return {
            'completed': False,
            'failed': False,
            'should_die': False
        }

    def reset(self, start_x: float = None, start_y: float = None) -> None:
        if start_x: self.start_x = start_x
        if start_y: self.start_y = start_y
        self.state = CheckpointState() # Reset ke 0