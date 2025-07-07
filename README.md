# Neon-Pacman-with-AI
A modern, neon-styled Pacman game featuring advanced AI-powered ghosts with dynamic behavioral patterns, enhanced visual effects, and retro chiptune audio.

## ✨ Enhanced Features
- **Advanced Neon Visual Style**: Multi-layer glowing graphics with dynamic lighting effects and particle trails
- **Enhanced AI-Powered Ghosts**: Four different AI personalities with scatter/chase modes:
  - **🔴 Red Ghost (Aggressive)**: Direct chase with anti-clustering behavior
  - **🩷 Pink Ghost (Ambush)**: Strategic positioning and escape route blocking
  - **🔵 Blue Ghost (Patrol)**: Dynamic patrol with proximity-based chase switching
  - **🟣 Purple Ghost (Random)**: Unpredictable movement with occasional chase behavior
- **⚡ Power Mode System**: Power pellets make ghosts vulnerable with visual feedback
- **🎵 Enhanced Chiptune Audio**: Programmatically generated 8-bit style sound effects
- **💫 Advanced Visual Effects**: Screen shake, particle trails, pulsing animations
- **🏆 High Score Tracking**: Persistent score saving and display
- **🔄 Dynamic AI Modes**: Ghosts switch between scatter and chase behaviors
- **🎯 Improved Gameplay**: Enhanced collision detection, scoring system, and feedback

## Installation & Setup

### Quick Start
```bash
# Clone the repository
git clone <your-repo-url>
cd Neon-Pacman-with-AI

# Run the setup script
python3 setup.py

# Or use the launcher script
./run_game.sh
```

### Manual Setup
1. Create and activate virtual environment:
   ```bash
   python3 -m venv pacman_env
   source pacman_env/bin/activate  # Linux/Mac
   # pacman_env\Scripts\activate   # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the game:
   ```bash
   python3 pacman_neon.py
   ```

## Controls
- **Arrow Keys**: Move Pacman (Up, Down, Left, Right)
- **SPACE**: Pause/Unpause game
- **ESC**: Quit game

## Game Mechanics
- Collect small pellets for 10 points each
- Collect large power pellets for 50 points each
- Avoid the AI ghosts or lose a life
- Game ends when all lives are lost or all pellets are collected

## AI Ghost Behaviors
Each ghost uses different AI algorithms to create varied and challenging gameplay:
- **Pathfinding**: Ghosts navigate around walls intelligently
- **Target Selection**: Different strategies for choosing movement targets
- **Adaptive Behavior**: AI responds to player actions in real-time

## Technical Features
- **Neon Glow Effects**: Dynamic lighting and glow rendering
- **Procedural Audio**: Chiptune sounds generated programmatically using NumPy
- **Smooth Animation**: 60 FPS with animated Pacman mouth
- **Intelligent AI**: Each ghost type implements unique pathfinding algorithms
- **Collision Detection**: Precise collision detection for walls, pellets, and ghosts
- **Screen Wrapping**: Seamless movement across screen boundaries

## Dependencies
- Python 3.7+
- Pygame 2.5.2+
- NumPy 1.24.3+

## Project Structure
```
Neon-Pacman-with-AI/
├── pacman_neon.py      # Main game file
├── setup.py            # Setup script
├── run_game.sh         # Launcher script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```
