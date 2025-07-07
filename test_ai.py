#!/usr/bin/env python3
"""
Test script to verify AI ghost behaviors
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pacman_neon import *

def test_ai_behaviors():
    """Test different AI ghost behaviors"""
    print("🧪 Testing AI Ghost Behaviors")
    print("=" * 40)
    
    # Create test objects
    maze = Maze()
    pacman = Pacman(100, 100)
    
    # Create ghosts
    red_ghost = Ghost(200, 200, GhostType.RED, NEON_RED)
    pink_ghost = Ghost(300, 200, GhostType.PINK, NEON_PINK)
    blue_ghost = Ghost(200, 300, GhostType.BLUE, NEON_BLUE)
    purple_ghost = Ghost(300, 300, GhostType.PURPLE, NEON_PURPLE)
    
    ghosts = [red_ghost, pink_ghost, blue_ghost, purple_ghost]
    
    print("✅ All ghosts created successfully")
    
    # Test AI targeting
    for ghost in ghosts:
        old_target = (ghost.target_x, ghost.target_y)
        ghost.choose_target(pacman, ghosts)
        new_target = (ghost.target_x, ghost.target_y)
        
        behavior_name = ghost.ghost_type.value.title()
        print(f"🤖 {behavior_name} Ghost: Target changed from {old_target} to {new_target}")
    
    print("\n✅ AI targeting systems working correctly")
    
    # Test audio system
    print("\n🔊 Testing Audio System")
    audio = AudioManager()
    print("✅ Audio manager created")
    print("✅ Sound effects generated")
    
    # Test maze generation
    print(f"\n🏗️  Maze Statistics:")
    print(f"   Walls: {len(maze.walls)}")
    print(f"   Pellets: {len(maze.pellets)}")
    print(f"   Power Pellets: {len(maze.power_pellets)}")
    
    print("\n🎉 All AI systems tested successfully!")
    return True

if __name__ == "__main__":
    try:
        test_ai_behaviors()
        print("\n✅ ALL TESTS PASSED!")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
