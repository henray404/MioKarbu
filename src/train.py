"""
Training Entry Point untuk Tabrak Bahlil AI
============================================

Cara pakai:
    python train.py                    # Training default
    python train.py --generations 100  # Set jumlah generasi
    python train.py --track mandalika  # Pilih track
    python train.py --laps 10          # Target lap untuk menang
"""

import os
import sys

# Setup path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "src"))

from ai.trainer import NEATTrainer


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Train AI Motor dengan NEAT")
    
    parser.add_argument(
        '--generations', '-g',
        type=int,
        default=50,
        help='Jumlah generasi training (default: 50)'
    )
    
    parser.add_argument(
        '--track', '-t',
        type=str,
        default='mandalika',
        help='Nama track untuk training (default: mandalika)'
    )
    
    parser.add_argument(
        '--laps', '-l',
        type=int,
        default=15,
        help='Target lap untuk menang (default: 15)'
    )
    
    args = parser.parse_args()
    
    # Config path (di root project)
    config_path = os.path.join(BASE_DIR, "config.txt")
    
    # Cek config exists
    if not os.path.exists(config_path):
        print(f"ERROR: Config tidak ditemukan: {config_path}")
        sys.exit(1)
    
    print("=" * 60)
    print("  TABRAK BAHLIL - NEAT AI Training")
    print("=" * 60)
    print(f"Track       : {args.track}")
    print(f"Generations : {args.generations}")
    print(f"Target Laps : {args.laps}")
    print(f"Config      : {config_path}")
    print("=" * 60)
    print()
    
    # Create trainer
    trainer = NEATTrainer(
        config_path=config_path,
        track_name=args.track
    )
    trainer.target_laps = args.laps
    
    # Run training
    try:
        winner = trainer.run(generations=args.generations)
        
        print("\nTraining selesai!")
        if winner:
            print(f"Best fitness: {winner.fitness:.2f}")
            print(f"Model tersimpan di: models/")
        
    except KeyboardInterrupt:
        print("\n\nTraining dihentikan oleh user")


if __name__ == "__main__":
    main()
