# Luxury Maze Adventure

A sophisticated maze game where AI players navigate through randomly generated mazes, collecting resources, avoiding traps, solving puzzles, and defeating bosses to reach the end.

## Features

- **Random Maze Generation**: Creates unique mazes with varying complexity and density
- **AI Player Navigation**: Strategic pathfinding algorithms guide the AI through the maze
- **Rich Game Elements**: Resources, traps, puzzles, and boss battles
- **Prompt-Based Engine**: Uses a prompt generation system that can be connected to LLM engines
- **Web Interface**: Interactive visualization and control of the maze game
- **Terminal Interface**: Alternative text-based interface for testing and development
- **Advanced Terminal Interface**: Enhanced curses-based interface with solution visualization and auto-navigation

## Architecture

The system follows a modular architecture with the following components:

1. **Maze Generator**: Creates random mazes with various features
2. **AI Player**: Implements pathfinding and decision-making algorithms
3. **Prompt Generator**: Creates structured prompts for the AI engine
4. **Maze Engine**: Coordinates game logic and state management
5. **Web Interface**: Provides a browser-based UI for the game
6. **Terminal Interface**: Provides a text-based UI for testing
7. **Advanced Terminal Interface**: Provides a rich curses-based UI with solution visualization

## Technical Implementation

- **Maze Generation**: Uses a modified Prim's algorithm for maze creation
- **AI Navigation**: Implements A* algorithm for optimal pathfinding with complete solution planning
- **Docker Support**: Containerized deployment for easy setup
- **Web Framework**: Flask-based web server with interactive UI
- **Prompt Engineering**: Structured JSON-based prompts with knowledge enhancement

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
- `--mode`: Choose between 'web', 'terminal', or 'advanced' interfaces
- `--port`: Set the port for the web interface
- `--width`, `--height`: Set maze dimensions
- `--complexity`, `--density`: Adjust maze generation parameters
- `--auto`: Start in auto mode (advanced terminal only)
- `--show-solution`: Show solution path immediately (advanced terminal only)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
