#!/usr/bin/env python3
"""
Quick Rapid Training Launcher
Run this alongside your main bot for accelerated learning
"""

import subprocess
import sys
import time
from learning_engine import BensonLearningEngine

def show_learning_stats():
    """Show current learning engine statistics"""
    try:
        engine = BensonLearningEngine()
        stats = engine.get_learning_stats()
        
        print("🧠 CURRENT LEARNING STATUS:")
        print("=" * 40)
        print(f"📊 Sessions Analyzed: {stats['total_sessions']}")
        print(f"🎯 Patterns Learned: {stats['learned_patterns']}")
        print(f"✅ Learning Active: {stats['learning_active']}")
        print(f"💰 Best Return: {stats['best_session_return']:.2f}%")
        print("=" * 40)
        
    except Exception as e:
        print(f"Error getting stats: {e}")

def main():
    print("🔥 BENSON BOT RAPID FIRE TRAINER")
    print("Accelerated Learning System")
    print()
    
    # Show current stats
    print("BEFORE TRAINING:")
    show_learning_stats()
    print()
    
    # Ask user for training intensity
    print("Choose training intensity:")
    print("1. Light Training (5 min, 5 trades/min)")
    print("2. Medium Training (5 min, 10 trades/min)")  
    print("3. Heavy Training (5 min, 20 trades/min)")
    print("4. Beast Mode (10 min, 30 trades/min)")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    # Configure training
    training_configs = {
        '1': {'duration': 300, 'rate': 5, 'name': 'Light'},
        '2': {'duration': 300, 'rate': 10, 'name': 'Medium'},
        '3': {'duration': 300, 'rate': 20, 'name': 'Heavy'}, 
        '4': {'duration': 600, 'rate': 30, 'name': 'Beast Mode'}
    }
    
    if choice not in training_configs:
        choice = '2'  # Default to medium
        
    config = training_configs[choice]
    
    print(f"\n🚀 Starting {config['name']} Training...")
    print(f"Duration: {config['duration']/60:.1f} minutes")
    print(f"Rate: {config['rate']} trades/minute")
    print(f"Expected Patterns: ~{config['duration'] * config['rate'] // 60}")
    print()
    
    # Modify rapid_fire_trainer.py settings on the fly
    trainer_code = f"""
from rapid_fire_trainer import RapidFireTrainer
import time

# Create trainer with custom settings
trainer = RapidFireTrainer()
trainer.rapid_fire_settings['session_duration'] = {config['duration']}
trainer.rapid_fire_settings['trades_per_minute'] = {config['rate']}

print("🔥 {config['name']} TRAINING INITIATED")
trainer.run_rapid_training_session()
"""
    
    # Write and execute
    with open('temp_rapid_training.py', 'w') as f:
        f.write(trainer_code)
    
    try:
        # Run the rapid training
        result = subprocess.run([sys.executable, 'temp_rapid_training.py'], 
                              capture_output=True, text=True, timeout=config['duration']+60)
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Training session completed (timeout)")
    except Exception as e:
        print(f"Error during training: {e}")
    
    # Clean up
    try:
        import os
        os.remove('temp_rapid_training.py')
    except:
        pass
    
    print("\n" + "="*50)
    print("AFTER TRAINING:")
    show_learning_stats()
    print()
    print("🎯 Your main bot now has MORE PATTERNS to work with!")
    print("🧠 Enhanced learning data will improve future trades!")

if __name__ == "__main__":
    main()