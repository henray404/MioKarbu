"""
Training Entry Point untuk Tabrak Bahlil AI
============================================

Cara pakai:
    python train.py                    # Training default (dengan visualisasi)
    python train.py --generations 100  # Set jumlah generasi
    python train.py --track mandalika  # Pilih track
    python train.py --laps 10          # Target lap untuk menang
    
Mode cepat (tanpa visualisasi):
    python train.py --headless         # Training tanpa visualisasi (3-5x lebih cepat)
    python train.py --render-interval 10  # Render setiap 10 frame (lebih cepat)
    
Contoh kombinasi:
    python train.py -g 100 --headless  # 100 generasi, tanpa visualisasi
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
        default='map-2',
        help='Nama track untuk training (default: mandalika)'
    )
    
    parser.add_argument(
        '--laps', '-l',
        type=int,
        default=15,
        help='Target lap untuk menang (default: 15)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Training tanpa visualisasi (lebih cepat 3-5x)'
    )
    
    parser.add_argument(
        '--render-interval', '-r',
        type=int,
        default=1,
        help='Render setiap N frame, misal 10 = render setiap 10 frame (default: 1)'
    )
    
    parser.add_argument(
        '--checkpoint', '-c',
        type=str,
        default=None,
        help='Path ke checkpoint untuk resume training (contoh: neat_checkpoints/neat-checkpoint-94)'
    )
    
    args = parser.parse_args()
    
    # Config path (di root project)
    config_path = os.path.join(BASE_DIR, "config.txt")
    
    # Cek config exists
    if not os.path.exists(config_path):
        print(f"ERROR: Config tidak ditemukan: {config_path}")
        sys.exit(1)
    
    mode_str = "HEADLESS" if args.headless else f"Visual (render every {args.render_interval} frame)"
    
    print("=" * 60)
    print("  TABRAK BAHLIL - NEAT AI Training")
    print("=" * 60)
    print(f"Track       : {args.track}")
    print(f"Generations : {args.generations}")
    print(f"Target Laps : {args.laps}")
    print(f"Mode        : {mode_str}")
    print(f"Config      : {config_path}")
    if args.checkpoint:
        print(f"Checkpoint  : {args.checkpoint} (RESUME)")
    print("=" * 60)
    print()
    
    # Create trainer
    trainer = NEATTrainer(
        config_path=config_path,
        track_name=args.track,
        headless=args.headless,
        render_interval=args.render_interval,
        map_name=args.track
    )
    trainer.target_laps = args.laps
    
    # Run training (dengan checkpoint jika ada)
    try:
        winner = trainer.run(generations=args.generations, checkpoint_path=args.checkpoint)
        
        print("\nTraining selesai!")
        if winner:
            print(f"Best fitness: {winner.fitness:.2f}")
            print(f"Model tersimpan di: models/")
        
    except KeyboardInterrupt:
        print("\n\n" + "="*50)
        print("Training dihentikan oleh user")
        print("="*50)
        
        # Save best model sebelum exit
        import pickle
        import neat
        models_dir = os.path.join(BASE_DIR, "models")
        os.makedirs(models_dir, exist_ok=True)
        
        # Cari checkpoint terakhir untuk get best genome
        checkpoint_dir = os.path.join(BASE_DIR, "neat_checkpoints")
        checkpoints = [f for f in os.listdir(checkpoint_dir) if f.startswith("neat-checkpoint-")]
        
        if checkpoints:
            # Sort by generation number
            checkpoints.sort(key=lambda x: int(x.split("-")[-1]))
            latest = os.path.join(checkpoint_dir, checkpoints[-1])
            print(f"Loading latest checkpoint: {latest}")
            
            try:
                pop = neat.Checkpointer.restore_checkpoint(latest)
                best = pop.best_genome
                if best:
                    with open(os.path.join(models_dir, 'interrupted_genome.pkl'), 'wb') as f:
                        pickle.dump(best, f)
                    print(f"✅ Best genome saved to: models/interrupted_genome.pkl")
                    print(f"   Fitness: {best.fitness:.2f}")
            except Exception as e:
                print(f"Could not save genome: {e}")
        else:
            print("No checkpoints found to save")


if __name__ == "__main__":
    main()
