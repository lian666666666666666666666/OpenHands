import json
import os

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from maze_engine import MazeEngine

app = Flask(__name__, static_folder='static')
CORS(app, resources={r'/*': {'origins': '*'}})

# Create a global maze engine instance
maze_engine = MazeEngine(width=21, height=21, complexity=0.8, density=0.7)


# Mock AI engine response (in a real implementation, this would call an actual LLM)
def mock_ai_engine(prompt):
    """Simulate an AI engine response based on the prompt."""
    # Extract AI status from the prompt
    try:
        ai_status_start = prompt.find('## AI Player Status')
        ai_status_end = prompt.find('## User Input')
        ai_status_json = (
            prompt[ai_status_start:ai_status_end]
            .strip()
            .replace('## AI Player Status', '')
            .strip()
        )
        ai_status = json.loads(ai_status_json)

        # Generate a response based on AI status
        response = f'The AI player is at position {ai_status["position"]}. '

        if ai_status['health'] < 50:
            response += "The player's health is low, proceeding with caution. "

        if ai_status['resources'] > 0:
            response += f'The player has collected {ai_status["resources"]} resources. '

        if ai_status['puzzles_solved'] > 0:
            response += f'The player has solved {ai_status["puzzles_solved"]} puzzles. '

        if ai_status['boss_defeated']:
            response += 'The boss has been defeated! Heading to the exit. '
        elif ai_status['game_over']:
            if ai_status['won']:
                response += (
                    'Victory! The player has successfully completed the maze adventure.'
                )
            else:
                response += (
                    'Game over. The player has failed to complete the maze adventure.'
                )

        return response
    except Exception as e:
        return (
            f'The AI player continues to navigate through the maze. (Error: {str(e)})'
        )


# Create templates directory if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Create a simple HTML template for the web interface
with open('templates/index.html', 'w') as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Luxury Maze Adventure</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #1a1a2e;
            color: #e6e6e6;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        h1 {
            color: #f0a500;
            text-align: center;
            grid-column: span 2;
        }
        .maze-container {
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .controls {
            background-color: #16213e;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        #maze-display {
            font-family: monospace;
            white-space: pre;
            font-size: 14px;
            line-height: 1;
            overflow: auto;
            background-color: #0f3460;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        #game-log {
            height: 200px;
            overflow-y: auto;
            background-color: #0f3460;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .log-entry {
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid #2a4b8d;
        }
        .status-panel {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
        }
        .status-item {
            background-color: #0f3460;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .status-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #f0a500;
        }
        input, button, textarea {
            width: 100%;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 5px;
            border: none;
            background-color: #0f3460;
            color: #e6e6e6;
        }
        button {
            background-color: #e94560;
            cursor: pointer;
            font-weight: bold;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #f0587e;
        }
        .progress-bar {
            height: 20px;
            background-color: #0f3460;
            border-radius: 10px;
            margin-bottom: 10px;
            overflow: hidden;
        }
        .progress-fill {
            height: 100%;
            background-color: #e94560;
            transition: width 0.3s ease;
        }
        @media (max-width: 768px) {
            .container {
                grid-template-columns: 1fr;
            }
            h1 {
                grid-column: span 1;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Luxury Maze Adventure</h1>

        <div class="maze-container">
            <h2>Maze Visualization</h2>
            <div id="maze-display">Loading maze...</div>

            <div class="status-panel">
                <div class="status-item">
                    <div>Health</div>
                    <div class="progress-bar">
                        <div id="health-bar" class="progress-fill" style="width: 100%;"></div>
                    </div>
                    <div id="health-value" class="status-value">100</div>
                </div>
                <div class="status-item">
                    <div>Resources</div>
                    <div id="resources-value" class="status-value">0</div>
                </div>
                <div class="status-item">
                    <div>Puzzles Solved</div>
                    <div id="puzzles-value" class="status-value">0</div>
                </div>
                <div class="status-item">
                    <div>Turn Count</div>
                    <div id="turns-value" class="status-value">0</div>
                </div>
            </div>

            <button id="new-game-btn">New Game</button>
            <button id="advance-btn">Advance Turn</button>
        </div>

        <div class="controls">
            <h2>Game Controls</h2>

            <div id="game-log">
                <div class="log-entry">Welcome to Luxury Maze Adventure! Generate a new maze to begin.</div>
            </div>

            <h3>User Input</h3>
            <textarea id="user-input" rows="4" placeholder="Enter your instructions for the AI player..."></textarea>
            <button id="submit-input-btn">Submit Input</button>

            <div id="ai-response" style="margin-top: 20px;">
                <h3>AI Response</h3>
                <div id="response-content" style="background-color: #0f3460; padding: 10px; border-radius: 5px;">
                    No response yet.
                </div>
            </div>
        </div>
    </div>

    <script>
        // DOM elements
        const mazeDisplay = document.getElementById('maze-display');
        const gameLog = document.getElementById('game-log');
        const healthBar = document.getElementById('health-bar');
        const healthValue = document.getElementById('health-value');
        const resourcesValue = document.getElementById('resources-value');
        const puzzlesValue = document.getElementById('puzzles-value');
        const turnsValue = document.getElementById('turns-value');
        const newGameBtn = document.getElementById('new-game-btn');
        const advanceBtn = document.getElementById('advance-btn');
        const userInput = document.getElementById('user-input');
        const submitInputBtn = document.getElementById('submit-input-btn');
        const responseContent = document.getElementById('response-content');

        // Add log entry
        function addLogEntry(message) {
            const entry = document.createElement('div');
            entry.className = 'log-entry';
            entry.textContent = message;
            gameLog.appendChild(entry);
            gameLog.scrollTop = gameLog.scrollHeight;
        }

        // Update game display
        function updateGameDisplay() {
            fetch('/visualize')
                .then(response => response.text())
                .then(data => {
                    mazeDisplay.textContent = data;
                })
                .catch(error => {
                    console.error('Error:', error);
                    mazeDisplay.textContent = 'Error loading maze visualization';
                });

            fetch('/status')
                .then(response => response.json())
                .then(data => {
                    // Update status panel
                    healthValue.textContent = data.health;
                    healthBar.style.width = `${data.health}%`;
                    resourcesValue.textContent = data.resources_collected;
                    puzzlesValue.textContent = data.puzzles_solved;
                    turnsValue.textContent = data.turn_count;

                    // Check game over
                    if (data.game_over) {
                        if (data.won) {
                            addLogEntry('Victory! You have completed the maze adventure!');
                        } else {
                            addLogEntry('Game over! You have failed to complete the maze adventure.');
                        }
                        advanceBtn.disabled = true;
                    } else {
                        advanceBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        }

        // New game
        newGameBtn.addEventListener('click', () => {
            fetch('/new_game', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addLogEntry(data.message);
                    updateGameDisplay();
                    advanceBtn.disabled = false;
                    responseContent.textContent = 'No response yet.';
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });

        // Advance turn
        advanceBtn.addEventListener('click', () => {
            fetch('/advance', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addLogEntry(data.message);
                    updateGameDisplay();
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });

        // Submit user input
        submitInputBtn.addEventListener('click', () => {
            const input = userInput.value.trim();
            if (!input) {
                addLogEntry('Please enter some input.');
                return;
            }

            fetch('/process_input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ input: input }),
            })
                .then(response => response.json())
                .then(data => {
                    addLogEntry(`User input: ${input}`);
                    responseContent.textContent = data.response;
                    userInput.value = '';
                })
                .catch(error => {
                    console.error('Error:', error);
                });
        });

        // Initial load
        updateGameDisplay();
    </script>
</body>
</html>
    """)

# Create static directory
os.makedirs('static', exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/new_game', methods=['POST'])
def new_game():
    result = maze_engine.new_game()
    return jsonify(result)


@app.route('/visualize')
def visualize():
    return maze_engine.visualize_maze()


@app.route('/status')
def status():
    return jsonify(maze_engine.get_game_summary())


@app.route('/advance', methods=['POST'])
def advance():
    result = maze_engine.advance_game()
    return jsonify(result)


@app.route('/process_input', methods=['POST'])
def process_input():
    data = request.json
    user_input = data.get('input', '')

    # Generate prompt based on user input
    prompt_result = maze_engine.process_user_input(user_input)

    # In a real implementation, this would call an actual LLM API
    ai_response = mock_ai_engine(prompt_result['prompt'])

    # Advance the game with the AI response
    maze_engine.advance_game(ai_response)

    return jsonify({'response': ai_response, 'prompt': prompt_result['prompt']})


if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
