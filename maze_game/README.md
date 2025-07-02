# Luxury Maze Adventure

A sophisticated maze game where AI players navigate through randomly generated mazes, collecting resources, avoiding traps, solving puzzles, and defeating bosses to reach the end.

## Features

- **Random Maze Generation**: Creates unique mazes with varying complexity and density
- **AI Player Navigation**: Strategic pathfinding algorithms guide the AI through the maze
- **Rich Game Elements**: Resources, traps, puzzles, and boss battles
- **Prompt-Based Engine**: Uses a prompt generation system that can be connected to LLM engines
- **Web Interface**: Interactive visualization and control of the maze game
- **Terminal Interface**: Alternative text-based interface for testing and development

## Architecture

The system follows a modular architecture with the following components:

1. **Maze Generator**: Creates random mazes with various features
2. **AI Player**: Implements pathfinding and decision-making algorithms
3. **Prompt Generator**: Creates structured prompts for the AI engine
4. **Maze Engine**: Coordinates game logic and state management
5. **Web Interface**: Provides a browser-based UI for the game
6. **Terminal Interface**: Provides a text-based UI for testing

## Technical Implementation

- **Maze Generation**: Uses a modified Prim's algorithm for maze creation
- **AI Navigation**: Implements BFS (Breadth-First Search) for pathfinding
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

## Customization

You can customize the game by modifying the following parameters:

- Maze dimensions (width, height)
- Complexity and density of the maze
- AI player strategies
- Knowledge base for prompt enhancement

## License

This project is licensed under the MIT License - see the LICENSE file for details.
