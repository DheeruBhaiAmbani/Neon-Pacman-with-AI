#!/usr/bin/env python3
"""
Neon Pacman with AI - A modern, neon-styled Pacman game featuring AI-powered ghosts
"""

import pygame
import sys
import math
import random
from enum import Enum
from typing import List, Tuple, Optional
import numpy as np

# Initialize Pygame
pygame.init()

# Initialize audio with error handling
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_AVAILABLE = True
except pygame.error:
    print("⚠️  Audio not available in this environment")
    AUDIO_AVAILABLE = False

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
CELL_SIZE = 20
MAZE_WIDTH = SCREEN_WIDTH // CELL_SIZE
MAZE_HEIGHT = SCREEN_HEIGHT // CELL_SIZE

# Neon Colors
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_YELLOW = (255, 255, 0)
NEON_PURPLE = (138, 43, 226)
NEON_RED = (255, 0, 100)
NEON_ORANGE = (255, 165, 0)
BLACK = (0, 0, 0)
DARK_BLUE = (0, 0, 50)
GLOW_WHITE = (255, 255, 255)

# Game Constants
PACMAN_SPEED = 4
GHOST_SPEED = 3
PELLET_SCORE = 10
POWER_PELLET_SCORE = 50
LIVES = 3

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GhostType(Enum):
    RED = "aggressive"
    PINK = "ambush"
    BLUE = "patrol"
    PURPLE = "random"

class AudioManager:
    """Manages retro chiptune audio for the game"""
    
    def __init__(self):
        self.sounds = {}
        self.music_playing = False
        self.volume = 0.7
        
        # Create simple chiptune-style sounds programmatically
        self.create_sounds()
        
    def create_sounds(self):
        """Create retro chiptune sounds using pygame"""
        if not AUDIO_AVAILABLE:
            # Create silent sounds as fallback
            silent = np.zeros((1000, 2), dtype=np.int16)
            for key in ['pellet', 'power_pellet', 'ghost_death', 'game_over']:
                self.sounds[key] = None
            return
            
        try:
            # Create simple waveforms for retro sounds
            sample_rate = 22050
            
            # Pellet collection sound (short beep)
            duration = 0.1
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            for i in range(frames):
                wave = 0.3 * np.sin(2 * np.pi * 800 * i / sample_rate)
                arr[i] = [wave, wave]
            self.sounds['pellet'] = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
            
            # Power pellet sound (ascending beep)
            duration = 0.3
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            for i in range(frames):
                freq = 400 + (i / frames) * 400
                wave = 0.4 * np.sin(2 * np.pi * freq * i / sample_rate)
                arr[i] = [wave, wave]
            self.sounds['power_pellet'] = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
            
            # Ghost death sound (descending)
            duration = 0.5
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            for i in range(frames):
                freq = 600 - (i / frames) * 400
                wave = 0.3 * np.sin(2 * np.pi * freq * i / sample_rate)
                arr[i] = [wave, wave]
            self.sounds['ghost_death'] = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
            
            # Game over sound
            duration = 1.0
            frames = int(duration * sample_rate)
            arr = np.zeros((frames, 2))
            for i in range(frames):
                freq = 200 - (i / frames) * 100
                wave = 0.2 * np.sin(2 * np.pi * freq * i / sample_rate)
                arr[i] = [wave, wave]
            self.sounds['game_over'] = pygame.sndarray.make_sound((arr * 32767).astype(np.int16))
            
        except Exception as e:
            print(f"Audio creation failed: {e}")
            # Create silent sounds as fallback
            silent = pygame.sndarray.make_sound(np.zeros((1000, 2), dtype=np.int16))
            for key in ['pellet', 'power_pellet', 'ghost_death', 'game_over']:
                self.sounds[key] = silent
    
    def play_sound(self, sound_name: str):
        """Play a sound effect"""
        if AUDIO_AVAILABLE and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(self.volume)
            self.sounds[sound_name].play()
    
    def set_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))

class Maze:
    """Represents the game maze"""
    
    def __init__(self):
        self.width = MAZE_WIDTH
        self.height = MAZE_HEIGHT
        self.walls = set()
        self.pellets = set()
        self.power_pellets = set()
        self.generate_maze()
    
    def generate_maze(self):
        """Generate a simple maze layout"""
        # Create border walls
        for x in range(self.width):
            self.walls.add((x, 0))
            self.walls.add((x, self.height - 1))
        for y in range(self.height):
            self.walls.add((0, y))
            self.walls.add((self.width - 1, y))
        
        # Add some internal walls for complexity
        wall_patterns = [
            # Horizontal walls
            [(x, 5) for x in range(5, 15)],
            [(x, 10) for x in range(10, 20)],
            [(x, 15) for x in range(5, 25)],
            [(x, 20) for x in range(15, 30)],
            # Vertical walls
            [(10, y) for y in range(8, 13)],
            [(20, y) for y in range(3, 8)],
            [(30, y) for y in range(12, 18)],
        ]
        
        for pattern in wall_patterns:
            for pos in pattern:
                if 0 < pos[0] < self.width - 1 and 0 < pos[1] < self.height - 1:
                    self.walls.add(pos)
        
        # Generate pellets in empty spaces
        for x in range(1, self.width - 1):
            for y in range(1, self.height - 1):
                if (x, y) not in self.walls:
                    # Add power pellets in corners
                    if (x < 3 or x > self.width - 4) and (y < 3 or y > self.height - 4):
                        if random.random() < 0.3:  # 30% chance for power pellet in corners
                            self.power_pellets.add((x, y))
                    else:
                        # Regular pellets everywhere else
                        if random.random() < 0.7:  # 70% chance for regular pellet
                            self.pellets.add((x, y))
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if position is a wall"""
        return (x, y) in self.walls
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is valid (not a wall and within bounds)"""
        return (0 <= x < self.width and 0 <= y < self.height and 
                (x, y) not in self.walls)

class Pacman:
    """Player-controlled Pacman character"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.speed = PACMAN_SPEED
        self.radius = CELL_SIZE // 2 - 2
        self.mouth_angle = 0
        self.mouth_speed = 8
    
    def update(self, maze: Maze):
        """Update Pacman's position and animation"""
        # Try to change direction if requested
        next_x = self.x + self.next_direction.value[0] * self.speed
        next_y = self.y + self.next_direction.value[1] * self.speed
        
        if maze.is_valid_position(next_x // CELL_SIZE, next_y // CELL_SIZE):
            self.direction = self.next_direction
        
        # Move in current direction
        new_x = self.x + self.direction.value[0] * self.speed
        new_y = self.y + self.direction.value[1] * self.speed
        
        # Check collision with walls
        if maze.is_valid_position(new_x // CELL_SIZE, new_y // CELL_SIZE):
            self.x = new_x
            self.y = new_y
        
        # Screen wrapping
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
        
        # Update mouth animation
        self.mouth_angle = (self.mouth_angle + self.mouth_speed) % 360
    
    def set_direction(self, direction: Direction):
        """Set the next direction for Pacman"""
        self.next_direction = direction
    
    def get_grid_pos(self) -> Tuple[int, int]:
        """Get Pacman's position in grid coordinates"""
        return (self.x // CELL_SIZE, self.y // CELL_SIZE)

class Ghost:
    """AI-powered ghost with different behavioral patterns"""
    
    def __init__(self, x: int, y: int, ghost_type: GhostType, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.ghost_type = ghost_type
        self.color = color
        self.direction = random.choice(list(Direction))
        self.speed = GHOST_SPEED
        self.target_x = x
        self.target_y = y
        self.patrol_points = []
        self.current_patrol = 0
        self.stuck_counter = 0
        self.mode_timer = 0
        self.scatter_mode = False
        self.home_corner = (x, y)  # Each ghost's home corner
        
        # Initialize patrol points and home corners for different ghost types
        if ghost_type == GhostType.BLUE:
            self.patrol_points = [
                (2 * CELL_SIZE, 2 * CELL_SIZE),
                ((MAZE_WIDTH - 3) * CELL_SIZE, 2 * CELL_SIZE),
                ((MAZE_WIDTH - 3) * CELL_SIZE, (MAZE_HEIGHT - 3) * CELL_SIZE),
                (2 * CELL_SIZE, (MAZE_HEIGHT - 3) * CELL_SIZE)
            ]
        
        # Set home corners for scatter mode
        if ghost_type == GhostType.RED:
            self.home_corner = ((MAZE_WIDTH - 2) * CELL_SIZE, 2 * CELL_SIZE)
        elif ghost_type == GhostType.PINK:
            self.home_corner = (2 * CELL_SIZE, 2 * CELL_SIZE)
        elif ghost_type == GhostType.BLUE:
            self.home_corner = ((MAZE_WIDTH - 2) * CELL_SIZE, (MAZE_HEIGHT - 2) * CELL_SIZE)
        elif ghost_type == GhostType.PURPLE:
            self.home_corner = (2 * CELL_SIZE, (MAZE_HEIGHT - 2) * CELL_SIZE)
    
    def update(self, maze: Maze, pacman: Pacman, other_ghosts: List['Ghost']):
        """Update ghost AI and movement"""
        # Update mode timer for scatter/chase behavior
        self.mode_timer += 1
        if self.mode_timer > 300:  # Switch modes every 5 seconds at 60 FPS
            self.scatter_mode = not self.scatter_mode
            self.mode_timer = 0
        
        self.choose_target(pacman, other_ghosts)
        self.move_towards_target(maze)
    
    def choose_target(self, pacman: Pacman, other_ghosts: List['Ghost']):
        """Choose target based on ghost AI type and current mode"""
        # In scatter mode, all ghosts go to their home corners
        if self.scatter_mode:
            self.target_x = self.home_corner[0]
            self.target_y = self.home_corner[1]
            return
        
        if self.ghost_type == GhostType.RED:
            # Aggressive: Direct chase with slight randomness to avoid clustering
            self.target_x = pacman.x
            self.target_y = pacman.y
            
            # Add slight offset if too close to other red ghosts
            for ghost in other_ghosts:
                if ghost != self and ghost.ghost_type == GhostType.RED:
                    distance = math.sqrt((self.x - ghost.x)**2 + (self.y - ghost.y)**2)
                    if distance < CELL_SIZE * 3:
                        offset = random.randint(-2, 2) * CELL_SIZE
                        self.target_x += offset
                        self.target_y += offset
            
        elif self.ghost_type == GhostType.PINK:
            # Ambush: Predict Pacman's movement with improved logic
            prediction_distance = 4 * CELL_SIZE
            
            # Consider Pacman's current direction and speed
            future_x = pacman.x + pacman.direction.value[0] * prediction_distance
            future_y = pacman.y + pacman.direction.value[1] * prediction_distance
            
            # Add strategic positioning - try to cut off escape routes
            if abs(pacman.x - self.x) > abs(pacman.y - self.y):
                # Pacman is more horizontally distant, predict vertical movement
                future_y += pacman.direction.value[1] * prediction_distance * 2
            else:
                # Pacman is more vertically distant, predict horizontal movement
                future_x += pacman.direction.value[0] * prediction_distance * 2
            
            self.target_x = future_x
            self.target_y = future_y
            
        elif self.ghost_type == GhostType.BLUE:
            # Patrol: Enhanced patrol with dynamic adjustment
            if self.patrol_points:
                target_point = self.patrol_points[self.current_patrol]
                distance_to_target = math.sqrt(
                    (self.x - target_point[0])**2 + (self.y - target_point[1])**2
                )
                
                if distance_to_target < CELL_SIZE * 1.5:
                    self.current_patrol = (self.current_patrol + 1) % len(self.patrol_points)
                
                # If Pacman is very close, temporarily chase instead of patrol
                pacman_distance = math.sqrt((self.x - pacman.x)**2 + (self.y - pacman.y)**2)
                if pacman_distance < CELL_SIZE * 5:
                    self.target_x = pacman.x
                    self.target_y = pacman.y
                else:
                    self.target_x = target_point[0]
                    self.target_y = target_point[1]
            
        elif self.ghost_type == GhostType.PURPLE:
            # Random: Improved random movement with occasional chase
            if random.random() < 0.15:  # 15% chance to change target
                if random.random() < 0.3:  # 30% of the time, chase Pacman
                    self.target_x = pacman.x + random.randint(-3, 3) * CELL_SIZE
                    self.target_y = pacman.y + random.randint(-3, 3) * CELL_SIZE
                else:
                    # Random movement
                    self.target_x = random.randint(2, MAZE_WIDTH - 3) * CELL_SIZE
                    self.target_y = random.randint(2, MAZE_HEIGHT - 3) * CELL_SIZE
    
    def move_towards_target(self, maze: Maze):
        """Move towards the chosen target using pathfinding"""
        # Simple pathfinding: choose direction that gets closest to target
        best_direction = self.direction
        best_distance = float('inf')
        
        for direction in Direction:
            new_x = self.x + direction.value[0] * self.speed
            new_y = self.y + direction.value[1] * self.speed
            
            # Check if move is valid
            if maze.is_valid_position(new_x // CELL_SIZE, new_y // CELL_SIZE):
                distance = math.sqrt((new_x - self.target_x)**2 + (new_y - self.target_y)**2)
                
                # Avoid reversing direction unless stuck
                if direction.value[0] == -self.direction.value[0] and direction.value[1] == -self.direction.value[1]:
                    if self.stuck_counter < 10:
                        continue
                
                if distance < best_distance:
                    best_distance = distance
                    best_direction = direction
        
        # Move in chosen direction
        new_x = self.x + best_direction.value[0] * self.speed
        new_y = self.y + best_direction.value[1] * self.speed
        
        if maze.is_valid_position(new_x // CELL_SIZE, new_y // CELL_SIZE):
            self.x = new_x
            self.y = new_y
            self.direction = best_direction
            self.stuck_counter = 0
        else:
            self.stuck_counter += 1
        
        # Screen wrapping
        if self.x < 0:
            self.x = SCREEN_WIDTH
        elif self.x > SCREEN_WIDTH:
            self.x = 0
    
    def get_grid_pos(self) -> Tuple[int, int]:
        """Get ghost's position in grid coordinates"""
        return (self.x // CELL_SIZE, self.y // CELL_SIZE)

class Game:
    """Main game class"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Neon Pacman with AI")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.score = 0
        self.lives = LIVES
        self.game_over = False
        self.paused = False
        self.power_mode = False
        self.power_timer = 0
        self.frame_count = 0
        
        # Visual effects
        self.screen_shake = 0
        self.last_positions = {}  # For particle trails
        
        # Audio
        self.audio = AudioManager()
        
        # Initialize game objects
        self.maze = Maze()
        self.pacman = Pacman(CELL_SIZE * 2, CELL_SIZE * 2)
        
        # Create ghosts with different AI types
        self.ghosts = [
            Ghost(CELL_SIZE * 18, CELL_SIZE * 10, GhostType.RED, NEON_RED),
            Ghost(CELL_SIZE * 20, CELL_SIZE * 10, GhostType.PINK, NEON_PINK),
            Ghost(CELL_SIZE * 18, CELL_SIZE * 12, GhostType.BLUE, NEON_BLUE),
            Ghost(CELL_SIZE * 20, CELL_SIZE * 12, GhostType.PURPLE, NEON_PURPLE)
        ]
        
        # Store initial positions for particle trails
        for ghost in self.ghosts:
            self.last_positions[id(ghost)] = (ghost.x, ghost.y)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_UP:
                    self.pacman.set_direction(Direction.UP)
                elif event.key == pygame.K_DOWN:
                    self.pacman.set_direction(Direction.DOWN)
                elif event.key == pygame.K_LEFT:
                    self.pacman.set_direction(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.pacman.set_direction(Direction.RIGHT)
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
        
        return True
    
    def update(self):
        """Update game logic"""
        if self.game_over or self.paused:
            return
        
        self.frame_count += 1
        
        # Update power mode
        if self.power_mode:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_mode = False
        
        # Update Pacman
        self.pacman.update(self.maze)
        
        # Store previous positions for particle trails
        for ghost in self.ghosts:
            self.last_positions[id(ghost)] = (ghost.x, ghost.y)
        
        # Update ghosts
        for ghost in self.ghosts:
            ghost.update(self.maze, self.pacman, self.ghosts)
        
        # Check pellet collection
        pacman_grid = self.pacman.get_grid_pos()
        if pacman_grid in self.maze.pellets:
            self.maze.pellets.remove(pacman_grid)
            self.score += PELLET_SCORE
            self.audio.play_sound('pellet')
        
        if pacman_grid in self.maze.power_pellets:
            self.maze.power_pellets.remove(pacman_grid)
            self.score += POWER_PELLET_SCORE
            self.power_mode = True
            self.power_timer = 300  # 5 seconds at 60 FPS
            self.screen_shake = 10
            self.audio.play_sound('power_pellet')
        
        # Check ghost collisions
        for ghost in self.ghosts:
            distance = math.sqrt((self.pacman.x - ghost.x)**2 + (self.pacman.y - ghost.y)**2)
            if distance < CELL_SIZE:
                if self.power_mode:
                    # In power mode, ghosts are vulnerable
                    self.score += 200
                    self.screen_shake = 5
                    # Reset ghost position
                    ghost.x = CELL_SIZE * (18 + self.ghosts.index(ghost) % 2)
                    ghost.y = CELL_SIZE * (10 + self.ghosts.index(ghost) // 2)
                    self.audio.play_sound('ghost_death')
                else:
                    # Normal collision - lose life
                    self.lives -= 1
                    self.screen_shake = 15
                    self.audio.play_sound('ghost_death')
                    if self.lives <= 0:
                        self.game_over = True
                        self.audio.play_sound('game_over')
                    else:
                        # Reset positions
                        self.pacman.x = CELL_SIZE * 2
                        self.pacman.y = CELL_SIZE * 2
                        for i, g in enumerate(self.ghosts):
                            g.x = CELL_SIZE * (18 + i % 2)
                            g.y = CELL_SIZE * (10 + i // 2)
        
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
        
        # Check win condition
        if not self.maze.pellets and not self.maze.power_pellets:
            self.game_over = True
    
    def draw_glow_effect(self, surface, color, center, radius, intensity=1.0):
        """Draw an enhanced glowing effect with multiple layers"""
        glow_surface = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
        
        # Create multiple glow layers for better effect
        for i in range(5):
            alpha = int((80 - i * 12) * intensity)
            if alpha > 0:
                glow_radius = radius + i * 3
                glow_color = (*color, alpha)
                pygame.draw.circle(glow_surface, glow_color, 
                                 (radius * 3, radius * 3), glow_radius)
        
        surface.blit(glow_surface, (center[0] - radius * 3, center[1] - radius * 3))
    
    def draw_particle_trail(self, surface, start_pos, end_pos, color, particles=5):
        """Draw a particle trail effect"""
        for i in range(particles):
            t = i / particles
            x = int(start_pos[0] + (end_pos[0] - start_pos[0]) * t)
            y = int(start_pos[1] + (end_pos[1] - start_pos[1]) * t)
            alpha = int(255 * (1 - t))
            particle_color = (*color, alpha)
            
            particle_surface = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, particle_color, (3, 3), 3)
            surface.blit(particle_surface, (x - 3, y - 3))
    
    def draw(self):
        """Render the game"""
        # Apply screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Clear screen with dark background
        if self.power_mode:
            # Darker background during power mode
            bg_color = (0, 0, 30) if self.power_timer % 20 < 10 else DARK_BLUE
            self.screen.fill(bg_color)
        else:
            self.screen.fill(DARK_BLUE)
        
        # Draw maze walls with enhanced neon glow
        for wall_pos in self.maze.walls:
            x, y = wall_pos[0] * CELL_SIZE + shake_x, wall_pos[1] * CELL_SIZE + shake_y
            center = (x + CELL_SIZE//2, y + CELL_SIZE//2)
            
            # Enhanced glow for walls
            intensity = 1.2 if self.power_mode else 1.0
            self.draw_glow_effect(self.screen, NEON_BLUE, center, CELL_SIZE//2, intensity)
            
            # Draw wall with slight animation
            wall_brightness = 255 if not self.power_mode else int(255 * (0.7 + 0.3 * math.sin(self.frame_count * 0.1)))
            wall_color = (0, wall_brightness, wall_brightness)
            pygame.draw.rect(self.screen, wall_color, 
                           (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
        
        # Draw pellets with pulsing effect
        for pellet_pos in self.maze.pellets:
            x, y = pellet_pos[0] * CELL_SIZE + shake_x, pellet_pos[1] * CELL_SIZE + shake_y
            center = (x + CELL_SIZE//2, y + CELL_SIZE//2)
            
            # Pulsing effect
            pulse = 0.8 + 0.2 * math.sin(self.frame_count * 0.15)
            self.draw_glow_effect(self.screen, NEON_YELLOW, center, int(4 * pulse), pulse)
            pygame.draw.circle(self.screen, NEON_YELLOW, center, int(3 * pulse))
        
        # Draw power pellets with enhanced effects
        for pellet_pos in self.maze.power_pellets:
            x, y = pellet_pos[0] * CELL_SIZE + shake_x, pellet_pos[1] * CELL_SIZE + shake_y
            center = (x + CELL_SIZE//2, y + CELL_SIZE//2)
            
            # Strong pulsing and rotating effect
            pulse = 0.7 + 0.3 * math.sin(self.frame_count * 0.2)
            rotation = self.frame_count * 0.1
            
            self.draw_glow_effect(self.screen, NEON_GREEN, center, int(12 * pulse), pulse * 1.5)
            
            # Draw rotating power pellet
            radius = int(8 * pulse)
            for i in range(8):
                angle = rotation + i * math.pi / 4
                px = center[0] + radius * math.cos(angle) * 0.5
                py = center[1] + radius * math.sin(angle) * 0.5
                pygame.draw.circle(self.screen, NEON_GREEN, (int(px), int(py)), 2)
            
            pygame.draw.circle(self.screen, NEON_GREEN, center, radius)
        
        # Draw Pacman with enhanced effects
        pacman_center = (int(self.pacman.x + shake_x), int(self.pacman.y + shake_y))
        
        # Power mode effect for Pacman
        if self.power_mode:
            power_intensity = 1.5 + 0.5 * math.sin(self.frame_count * 0.3)
            self.draw_glow_effect(self.screen, NEON_YELLOW, pacman_center, 
                                self.pacman.radius, power_intensity)
        else:
            self.draw_glow_effect(self.screen, NEON_YELLOW, pacman_center, self.pacman.radius)
        
        # Draw Pacman with mouth animation
        mouth_start_angle = self.pacman.mouth_angle
        mouth_end_angle = self.pacman.mouth_angle + 60
        
        # Adjust mouth direction based on movement
        direction_angles = {
            Direction.RIGHT: 0,
            Direction.LEFT: 180,
            Direction.UP: 270,
            Direction.DOWN: 90
        }
        base_angle = direction_angles.get(self.pacman.direction, 0)
        mouth_start_angle += base_angle
        mouth_end_angle += base_angle
        
        # Draw Pacman body
        pacman_color = NEON_YELLOW
        if self.power_mode:
            # Slightly different color during power mode
            brightness = int(255 * (0.8 + 0.2 * math.sin(self.frame_count * 0.2)))
            pacman_color = (brightness, brightness, 0)
        
        pygame.draw.circle(self.screen, pacman_color, pacman_center, self.pacman.radius)
        
        # Draw mouth
        if abs(math.sin(math.radians(self.pacman.mouth_angle))) > 0.3:
            mouth_points = [pacman_center]
            for angle in [mouth_start_angle, mouth_end_angle]:
                x = pacman_center[0] + self.pacman.radius * math.cos(math.radians(angle))
                y = pacman_center[1] + self.pacman.radius * math.sin(math.radians(angle))
                mouth_points.append((int(x), int(y)))
            pygame.draw.polygon(self.screen, DARK_BLUE, mouth_points)
        
        # Draw ghosts with enhanced effects and particle trails
        for ghost in self.ghosts:
            ghost_center = (int(ghost.x + shake_x), int(ghost.y + shake_y))
            
            # Draw particle trail
            if id(ghost) in self.last_positions:
                last_pos = self.last_positions[id(ghost)]
                trail_start = (int(last_pos[0] + shake_x), int(last_pos[1] + shake_y))
                self.draw_particle_trail(self.screen, trail_start, ghost_center, ghost.color)
            
            # Ghost color changes in power mode
            ghost_color = ghost.color
            if self.power_mode:
                # Ghosts become blue and flash when vulnerable
                flash_rate = max(1, self.power_timer // 30)
                if self.frame_count % (flash_rate * 2) < flash_rate:
                    ghost_color = (0, 0, 255)  # Blue when vulnerable
                else:
                    ghost_color = (255, 255, 255)  # White flash
            
            # Enhanced glow for ghosts
            glow_intensity = 1.0
            if ghost.scatter_mode:
                glow_intensity = 0.7  # Dimmer when in scatter mode
            elif self.power_mode:
                glow_intensity = 0.5  # Much dimmer when vulnerable
            
            self.draw_glow_effect(self.screen, ghost_color, ghost_center, CELL_SIZE//2, glow_intensity)
            
            # Draw ghost body
            pygame.draw.circle(self.screen, ghost_color, ghost_center, CELL_SIZE//2 - 2)
            
            # Draw ghost eyes
            eye_offset = CELL_SIZE//6
            left_eye = (ghost_center[0] - eye_offset, ghost_center[1] - eye_offset)
            right_eye = (ghost_center[0] + eye_offset, ghost_center[1] - eye_offset)
            
            eye_color = GLOW_WHITE if not self.power_mode else (255, 0, 0)  # Red eyes when vulnerable
            pygame.draw.circle(self.screen, eye_color, left_eye, 3)
            pygame.draw.circle(self.screen, eye_color, right_eye, 3)
            pygame.draw.circle(self.screen, BLACK, left_eye, 2)
            pygame.draw.circle(self.screen, BLACK, right_eye, 2)
            
            # Draw mode indicator
            if ghost.scatter_mode:
                # Small indicator for scatter mode
                indicator_pos = (ghost_center[0], ghost_center[1] - CELL_SIZE//2 - 5)
                pygame.draw.circle(self.screen, NEON_ORANGE, indicator_pos, 2)
        
        # Enhanced UI
        score_text = self.font.render(f"Score: {self.score}", True, NEON_GREEN)
        lives_text = self.font.render(f"Lives: {self.lives}", True, NEON_RED)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        
        # Power mode indicator
        if self.power_mode:
            power_text = self.font.render(f"POWER MODE: {self.power_timer // 60 + 1}s", True, NEON_GREEN)
            text_rect = power_text.get_rect(center=(SCREEN_WIDTH // 2, 30))
            
            # Pulsing effect for power mode text
            pulse = 0.8 + 0.2 * math.sin(self.frame_count * 0.4)
            glow_surface = pygame.Surface(power_text.get_size(), pygame.SRCALPHA)
            glow_surface.fill((*NEON_GREEN, int(100 * pulse)))
            self.screen.blit(glow_surface, (text_rect.x - 2, text_rect.y - 2))
            self.screen.blit(power_text, text_rect)
        
        # Draw AI ghost info with mode indicators
        ghost_info = [
            ("Red: Aggressive", NEON_RED),
            ("Pink: Ambush", NEON_PINK), 
            ("Blue: Patrol", NEON_BLUE),
            ("Purple: Random", NEON_PURPLE)
        ]
        
        for i, (info, color) in enumerate(ghost_info):
            ghost = self.ghosts[i]
            mode_text = " (Scatter)" if ghost.scatter_mode else " (Chase)"
            full_text = info + mode_text
            
            text_color = color if not self.power_mode else (100, 100, 255)
            text = self.small_font.render(full_text, True, text_color)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 10 + i * 25))
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if not self.maze.pellets and not self.maze.power_pellets:
                game_over_text = self.font.render("YOU WIN!", True, NEON_GREEN)
            else:
                game_over_text = self.font.render("GAME OVER", True, NEON_RED)
            
            final_score_text = self.font.render(f"Final Score: {self.score}", True, NEON_GREEN)
            restart_text = self.small_font.render("Press ESC to quit", True, NEON_YELLOW)
            
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 50))
            self.screen.blit(final_score_text, 
                           (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2))
            self.screen.blit(restart_text, 
                           (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 50))
        
        # Draw pause screen
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            pause_text = self.font.render("PAUSED", True, NEON_YELLOW)
            continue_text = self.small_font.render("Press SPACE to continue", True, NEON_GREEN)
            
            self.screen.blit(pause_text, 
                           (SCREEN_WIDTH//2 - pause_text.get_width()//2, SCREEN_HEIGHT//2 - 25))
            self.screen.blit(continue_text, 
                           (SCREEN_WIDTH//2 - continue_text.get_width()//2, SCREEN_HEIGHT//2 + 25))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # 60 FPS
        
        pygame.quit()
        return self.score

def main():
    """Main function"""
    print("🎮 Neon Pacman with AI")
    print("=" * 40)
    print("Controls:")
    print("  Arrow Keys - Move Pacman")
    print("  SPACE - Pause/Unpause")
    print("  ESC - Quit")
    print("\nAI Ghost Types:")
    print("  🔴 Red: Aggressive chaser")
    print("  🩷 Pink: Ambush predictor") 
    print("  🔵 Blue: Corner patrol")
    print("  🟣 Purple: Random movement")
    print("\nGame Features:")
    print("  ⚡ Power Pellets - Make ghosts vulnerable")
    print("  🌟 Enhanced AI - Scatter/Chase modes")
    print("  💫 Neon Effects - Dynamic lighting")
    print("  🎵 Chiptune Audio - Retro sound effects")
    print("=" * 40)
    
    # Load high score
    high_score = load_high_score()
    if high_score > 0:
        print(f"🏆 Current High Score: {high_score}")
        print("=" * 40)
    
    game = Game()
    final_score = game.run()
    
    # Save high score if beaten
    if final_score > high_score:
        save_high_score(final_score)
        print(f"🎉 NEW HIGH SCORE: {final_score}!")
    else:
        print(f"Final Score: {final_score}")

def load_high_score():
    """Load high score from file"""
    try:
        with open('highscore.txt', 'r') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_high_score(score):
    """Save high score to file"""
    try:
        with open('highscore.txt', 'w') as f:
            f.write(str(score))
    except Exception as e:
        print(f"Could not save high score: {e}")

if __name__ == "__main__":
    main()
