#!/usr/bin/env python3
"""
Demo script showing AI ghost behaviors
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pacman_neon import *
import time

def demo_ai_behaviors():
    """Demonstrate AI ghost behaviors"""
    print("🎮 Neon Pacman AI Behavior Demo")
    print("=" * 50)
    
    # Create game objects
    maze = Maze()
    pacman = Pacman(5 * CELL_SIZE, 5 * CELL_SIZE)
    
    # Create ghosts at different positions
    ghosts = [
        Ghost(10 * CELL_SIZE, 10 * CELL_SIZE, GhostType.RED, NEON_RED),
        Ghost(15 * CELL_SIZE, 10 * CELL_SIZE, GhostType.PINK, NEON_PINK),
        Ghost(10 * CELL_SIZE, 15 * CELL_SIZE, GhostType.BLUE, NEON_BLUE),
        Ghost(15 * CELL_SIZE, 15 * CELL_SIZE, GhostType.PURPLE, NEON_PURPLE)
    ]
    
    print("🤖 AI Ghost Behaviors:")
    print("  🔴 Red Ghost (Aggressive): Direct chase")
    print("  🩷 Pink Ghost (Ambush): Predicts movement")
    print("  🔵 Blue Ghost (Patrol): Guards corners")
    print("  🟣 Purple Ghost (Random): Unpredictable")
    print()
    
    # Simulate Pacman movement
    directions = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
    
    for step in range(8):
        print(f"📍 Step {step + 1}: Pacman at ({pacman.x//CELL_SIZE}, {pacman.y//CELL_SIZE})")
        
        # Move Pacman
        pacman.direction = directions[step % len(directions)]
        pacman.update(maze)
        
        # Update each ghost and show their behavior
        for i, ghost in enumerate(ghosts):
            ghost_names = ["Red (Aggressive)", "Pink (Ambush)", "Blue (Patrol)", "Purple (Random)"]
            old_pos = (ghost.x // CELL_SIZE, ghost.y // CELL_SIZE)
            
            ghost.update(maze, pacman, ghosts)
            
            new_pos = (ghost.x // CELL_SIZE, ghost.y // CELL_SIZE)
            target_pos = (ghost.target_x // CELL_SIZE, ghost.target_y // CELL_SIZE)
            
            print(f"  🤖 {ghost_names[i]}: {old_pos} → {new_pos} (targeting {target_pos})")
        
        print()
        time.sleep(0.5)  # Small delay for readability
    
    print("✅ AI Demo completed successfully!")
    print("\n🎯 Key AI Features Demonstrated:")
    print("  • Red Ghost directly chases Pacman")
    print("  • Pink Ghost predicts and ambushes")
    print("  • Blue Ghost patrols strategic positions")
    print("  • Purple Ghost moves unpredictably")
    print("  • All ghosts use intelligent pathfinding")

if __name__ == "__main__":
    try:
        demo_ai_behaviors()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        sys.exit(1)
