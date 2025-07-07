#!/usr/bin/env python3
"""
Setup script for Neon Pacman with AI
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    print("🎮 Neon Pacman with AI - Setup")
    print("=" * 40)
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  No virtual environment detected")
        print("It's recommended to use a virtual environment:")
        print("  python3 -m venv pacman_env")
        print("  source pacman_env/bin/activate  # On Linux/Mac")
        print("  pacman_env\\Scripts\\activate     # On Windows")
        print()
        
        response = input("Continue anyway? (y/N): ").lower()
        if response != 'y':
            print("Setup cancelled")
            return
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("Failed to install dependencies. Please check your Python environment.")
        return
    
    print("\n🎉 Setup completed successfully!")
    print("\nTo run the game:")
    print("  python3 pacman_neon.py")
    print("\nControls:")
    print("  Arrow Keys - Move Pacman")
    print("  SPACE - Pause/Unpause")
    print("  ESC - Quit")

if __name__ == "__main__":
    main()
