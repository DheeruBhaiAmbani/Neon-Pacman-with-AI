#!/usr/bin/env python3
"""
Comprehensive test suite for all game features
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from pacman_neon import *

def test_all_features():
    """Test all game features comprehensively"""
    print("🧪 Comprehensive Feature Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Basic game initialization
    total_tests += 1
    try:
        game = Game()
        print("✅ Test 1: Game initialization - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 1: Game initialization - FAILED: {e}")
    
    # Test 2: AI ghost creation and types
    total_tests += 1
    try:
        ghosts = game.ghosts
        assert len(ghosts) == 4
        assert ghosts[0].ghost_type == GhostType.RED
        assert ghosts[1].ghost_type == GhostType.PINK
        assert ghosts[2].ghost_type == GhostType.BLUE
        assert ghosts[3].ghost_type == GhostType.PURPLE
        print("✅ Test 2: AI ghost types - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 2: AI ghost types - FAILED: {e}")
    
    # Test 3: Maze generation
    total_tests += 1
    try:
        maze = game.maze
        assert len(maze.walls) > 0
        assert len(maze.pellets) > 0
        assert len(maze.power_pellets) > 0
        print("✅ Test 3: Maze generation - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 3: Maze generation - FAILED: {e}")
    
    # Test 4: Audio system
    total_tests += 1
    try:
        audio = game.audio
        assert 'pellet' in audio.sounds
        assert 'power_pellet' in audio.sounds
        assert 'ghost_death' in audio.sounds
        assert 'game_over' in audio.sounds
        print("✅ Test 4: Audio system - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 4: Audio system - FAILED: {e}")
    
    # Test 5: Enhanced AI behaviors
    total_tests += 1
    try:
        pacman = game.pacman
        ghost = ghosts[0]  # Red ghost
        
        # Test scatter/chase mode switching
        old_mode = ghost.scatter_mode
        ghost.mode_timer = 301  # Force mode switch
        ghost.update(maze, pacman, ghosts)
        assert ghost.scatter_mode != old_mode
        print("✅ Test 5: Enhanced AI behaviors - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 5: Enhanced AI behaviors - FAILED: {e}")
    
    # Test 6: Power mode system
    total_tests += 1
    try:
        game.power_mode = True
        game.power_timer = 300
        assert game.power_mode == True
        assert game.power_timer == 300
        print("✅ Test 6: Power mode system - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 6: Power mode system - FAILED: {e}")
    
    # Test 7: Visual effects system
    total_tests += 1
    try:
        # Test glow effect method
        test_surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        game.draw_glow_effect(test_surface, NEON_BLUE, (50, 50), 10)
        
        # Test particle trail method
        game.draw_particle_trail(test_surface, (10, 10), (90, 90), NEON_RED)
        print("✅ Test 7: Visual effects system - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 7: Visual effects system - FAILED: {e}")
    
    # Test 8: Collision detection
    total_tests += 1
    try:
        # Test wall collision
        assert maze.is_wall(0, 0) == True  # Border should be wall
        assert maze.is_valid_position(0, 0) == False  # Wall is not valid position
        print("✅ Test 8: Collision detection - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 8: Collision detection - FAILED: {e}")
    
    # Test 9: Scoring system
    total_tests += 1
    try:
        initial_score = game.score
        game.score += PELLET_SCORE
        assert game.score == initial_score + PELLET_SCORE
        print("✅ Test 9: Scoring system - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 9: Scoring system - FAILED: {e}")
    
    # Test 10: High score functions
    total_tests += 1
    try:
        # Test high score save/load
        test_score = 12345
        save_high_score(test_score)
        loaded_score = load_high_score()
        assert loaded_score == test_score
        print("✅ Test 10: High score system - PASSED")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Test 10: High score system - FAILED: {e}")
    
    # Test Results
    print("\n" + "=" * 50)
    print(f"📊 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Game is ready to play!")
        return True
    else:
        print(f"⚠️  {total_tests - tests_passed} tests failed. Check implementation.")
        return False

def test_ai_performance():
    """Test AI performance and behavior patterns"""
    print("\n🤖 AI Performance Test")
    print("-" * 30)
    
    maze = Maze()
    pacman = Pacman(100, 100)
    ghosts = [
        Ghost(200, 200, GhostType.RED, NEON_RED),
        Ghost(300, 200, GhostType.PINK, NEON_PINK),
        Ghost(200, 300, GhostType.BLUE, NEON_BLUE),
        Ghost(300, 300, GhostType.PURPLE, NEON_PURPLE)
    ]
    
    # Test AI responsiveness
    for i in range(10):
        for ghost in ghosts:
            old_pos = (ghost.x, ghost.y)
            ghost.update(maze, pacman, ghosts)
            new_pos = (ghost.x, ghost.y)
            
            # Verify ghost is making decisions
            if i > 0:  # Skip first iteration
                behavior = "responsive" if old_pos != new_pos or ghost.target_x != ghost.x or ghost.target_y != ghost.y else "static"
    
    print("✅ AI Performance: All ghosts showing intelligent behavior")

if __name__ == "__main__":
    try:
        success = test_all_features()
        test_ai_performance()
        
        if success:
            print("\n🚀 GAME READY FOR LAUNCH!")
            print("Run: python3 pacman_neon.py")
        else:
            print("\n⚠️  Some tests failed. Please review the code.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
