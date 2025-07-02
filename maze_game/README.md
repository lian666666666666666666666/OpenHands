# Luxury Maze Adventure

A sophisticated maze game where AI players navigate through randomly generated mazes, collecting resources, avoiding traps, solving puzzles, and defeating bosses to reach the end.

## Features

- **Enhanced Random Maze Generation**: Creates unique mazes with varying complexity, density, and difficulty levels
- **Super-Intelligent AI Player**: Advanced pathfinding and strategic decision-making with complete solution planning
- **Optimized AI with Anti-Stuck Mechanisms**: Improved decision-making logic that prevents getting stuck in loops
- **Rich Game Elements**:
  - Multiple resource types (small and large)
  - Different trap varieties (basic and advanced)
  - Puzzle challenges (easy and hard)
  - Enemy encounters (minions and boss)
  - Special features (teleports, shops, checkpoints, secrets)
- **RPG-Style Progression**:
  - Character stats (health, attack, defense)
  - Inventory system with usable items
  - Skills and abilities
  - Status effects
  - Gold and economy
- **Quest System**:
  - Dynamic quest assignment
  - Multiple quest types (resource collection, puzzle solving, boss slaying, etc.)
  - Quest progress tracking
  - Rewards for quest completion
- **Prompt-Based Engine**: Uses a structured prompt generation system that can be connected to LLM engines
- **Web Interface**: Interactive visualization and control of the maze game
- **Terminal Interface**: Alternative text-based interface for testing and development
- **Enhanced Terminal Interface**: Rich curses-based interface with color, animation, solution visualization, and auto-navigation
- **Quest Terminal Interface**: Advanced interface with quest system, improved visualization, and anti-stuck AI

## Architecture

The system follows a modular architecture with the following components:

1. **Enhanced Maze Generator**: Creates complex mazes with various features and difficulty levels
2. **AI Player**: Basic pathfinding and decision-making algorithms
3. **Enhanced AI Player**: Advanced AI with RPG mechanics, inventory, skills, and strategic planning
4. **Optimized AI Player**: Improved AI with quest system and anti-stuck mechanisms
5. **Prompt Generator**: Creates structured prompts for the AI engine
6. **Maze Engine**: Coordinates game logic and state management
7. **Web Interface**: Provides a browser-based UI for the game
8. **Terminal Interface**: Provides a text-based UI for testing
9. **Enhanced Terminal Interface**: Provides a rich curses-based UI with color, animation, and advanced visualization
10. **Quest Terminal Interface**: Provides an advanced UI with quest system and improved visualization

## Technical Implementation

- **Maze Generation**: Uses a modified Prim's algorithm with enhanced feature placement
- **AI Navigation**: Implements A* algorithm for optimal pathfinding with complete solution planning
- **Anti-Stuck Mechanisms**: Intelligent decision-making with position tracking and priority adjustments
- **Quest System**: Dynamic quest assignment with progress tracking and rewards
- **RPG Mechanics**: Full stats system with inventory, skills, status effects, and strategic combat
- **Docker Support**: Containerized deployment for easy setup
- **Web Framework**: Flask-based web server with interactive UI
- **Prompt Engineering**: Structured JSON-based prompts with knowledge enhancement
- **Curses Interface**: Rich terminal-based UI with color, animation, and interactive controls

## Getting Started

### Prerequisites

- Docker and Docker Compose (for containerized deployment)
- Python 3.9+ (for local development)

### Installation

1. Clone the repository
2. Navigate to the project directory

### Running with Docker

```bash
docker-compose up
```

The web interface will be available at http://localhost:12000

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the web interface:
```bash
python web_interface.py
```

3. Or run the terminal interface:
```bash
python terminal_interface.py
```

4. Or run the advanced terminal interface:
```bash
python advanced_terminal_interface.py
# or
./run_advanced.sh
```

5. Or run the enhanced terminal interface with RPG features:
```bash
python enhanced_terminal_interface.py
# or
./run_enhanced.sh
```

6. Or run the quest terminal interface with quest system and anti-stuck AI:
```bash
python quest_terminal_interface.py
# or
./run_quest.sh
```

## Usage

### Web Interface

1. Open your browser and navigate to http://localhost:12000
2. Click "New Game" to generate a new maze
3. Use "Advance Turn" to let the AI make moves automatically
4. Enter custom instructions in the text area and click "Submit Input"

### Terminal Interface

1. Run `python terminal_interface.py`
2. Follow the on-screen menu to navigate the game
3. Choose options to advance turns, provide input, or start a new game

### Advanced Terminal Interface

1. Run `python advanced_terminal_interface.py` or `./run_advanced.sh`
2. Use the following controls:
   - N: Start a new game
   - A: Toggle auto mode (AI will navigate automatically)
   - S: Show/hide the complete solution path
   - E: Execute the complete solution at once
   - Q: Quit the game
3. Watch as the AI player intelligently navigates through the maze

### Enhanced Terminal Interface

1. Run `python enhanced_terminal_interface.py` or `./run_enhanced.sh`
2. Use the following controls:
   - N: Start a new game
   - A: Toggle auto mode (AI will navigate automatically)
   - S: Show/hide the complete solution path
   - E: Execute the complete solution at once
   - I: Show/hide inventory
   - 1-9: Use inventory items
   - D: Change difficulty (easy/medium/hard)
   - H: Show help screen
   - Q: Quit the game
3. Enjoy the rich RPG experience with:
   - Color-coded maze elements
   - Health bar and status effects
   - Inventory management
   - Combat with enemies and boss
   - Shops, teleports, and secrets
   - Multiple difficulty levels

### Quest Terminal Interface

1. Run `python quest_terminal_interface.py` or `./run_quest.sh`
2. Use the following controls:
   - N: Start a new game
   - A: Toggle auto mode (AI will navigate automatically)
   - S: Show/hide the complete solution path
   - E: Execute the complete solution at once
   - I: Show/hide inventory
   - Q: Show/hide quest panel
   - 1-9: Use inventory items
   - D: Change difficulty (easy/medium/hard)
   - H: Show help screen
   - X: Quit the game
3. Experience the advanced gameplay with:
   - Dynamic quest system with multiple quest types
   - Quest progress tracking and rewards
   - Anti-stuck AI with improved decision-making
   - Enhanced visualization with color-coded elements
   - Position tracking to prevent getting stuck in loops
   - Optimized target selection based on game state

## Customization

You can customize the game by modifying the following parameters:

- Maze dimensions (width, height)
- Complexity and density of the maze
- AI player strategies
- Knowledge base for prompt enhancement

### Command Line Options

```bash
python run.py --help
```

Available options:
- `--mode`: Choose between 'web', 'terminal', 'advanced', 'enhanced', or 'quest' interfaces
- `--port`: Set the port for the web interface
- `--width`, `--height`: Set maze dimensions
- `--complexity`, `--density`: Adjust maze generation parameters
- `--difficulty`: Set game difficulty ('easy', 'medium', 'hard')
- `--auto`: Start in auto mode (advanced/enhanced/quest terminal only)
- `--show-solution`: Show solution path immediately (advanced/enhanced/quest terminal only)
- `--show-inventory`: Show inventory immediately (enhanced/quest terminal only)
- `--show-quest`: Show quest panel immediately (quest terminal only)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
