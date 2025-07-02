from ai_player import AIPlayer
from maze_generator import CellType, MazeGenerator
from prompt_generator import PromptGenerator


class MazeEngine:
    def __init__(self, width=15, height=15, complexity=0.75, density=0.75):
        """
        Initialize the maze game engine.

        Args:
            width: Width of the maze
            height: Height of the maze
            complexity: Complexity of the maze (0-1)
            density: Density of walls (0-1)
        """
        self.width = width
        self.height = height
        self.complexity = complexity
        self.density = density

        # Initialize components
        self.maze_generator = MazeGenerator(width, height, complexity, density)
        self.prompt_generator = PromptGenerator()

        # Game state
        self.maze = None
        self.ai_player = None
        self.game_history = []
        self.turn_count = 0
        self.max_turns = 100  # Prevent infinite loops

        # Knowledge base for enhancing prompts
        self.knowledge_base = {
            'Maze Navigation': """
            The AI player navigates through the maze using pathfinding algorithms.
            It can detect walls, traps, resources, puzzles, and the boss.
            The player must make strategic decisions to optimize its path.
            """,
            'Resource Collection': """
            Resources provide benefits to the AI player:
            - Increase chance of solving puzzles
            - Improve combat effectiveness against the boss
            - May heal the player or provide special abilities
            """,
            'Trap Mechanics': """
            Traps can damage the player, reducing health.
            Some traps may have special effects like:
            - Teleporting the player to a random location
            - Temporarily reducing visibility
            - Creating new walls or changing the maze structure
            """,
            'Puzzle Solving': """
            Puzzles require the AI to demonstrate problem-solving abilities.
            Success depends on:
            - Resources collected
            - Previous puzzles solved
            - Random chance (representing difficulty)
            """,
            'Boss Battle': """
            The boss guards the path to the exit.
            Combat success depends on:
            - Player health
            - Resources collected
            - Puzzles solved
            - Strategic approach
            """,
        }

        # Initialize a new game
        self.new_game()

    def new_game(self):
        """Start a new game by generating a maze and initializing the AI player."""
        # Generate a new maze
        self.maze = self.maze_generator.generate()

        # Initialize AI player
        self.ai_player = AIPlayer(self.maze)

        # Reset game state
        self.game_history = []
        self.turn_count = 0

        return {
            'message': 'New maze game initialized',
            'maze_size': (self.height, self.width),
            'start_position': self.ai_player.position,
        }

    def process_user_input(self, user_input):
        """
        Process user input to generate a prompt and advance the game.

        Args:
            user_input: String input from the user

        Returns:
            Dictionary with the generated prompt and game state
        """
        # Prepare game parameters
        game_parameters = {
            'maze_size': (self.height, self.width),
            'complexity': self.complexity,
            'density': self.density,
            'turn_count': self.turn_count,
            'max_turns': self.max_turns,
        }

        # Prepare game state
        game_state = {
            'maze_representation': self.maze.tolist(),
            'cell_types': {
                name: value for name, value in [(t.name, t.value) for t in CellType]
            },
        }

        # Get AI player status
        ai_status = self.ai_player.get_status()

        # Generate the prompt
        prompt = self.prompt_generator.generate_prompt(
            user_input, game_parameters, game_state, ai_status
        )

        # Enhance prompt with knowledge
        enhanced_prompt = self.prompt_generator.enhance_prompt_with_knowledge(
            prompt, self.knowledge_base
        )

        return {
            'prompt': enhanced_prompt,
            'game_state': game_state,
            'ai_status': ai_status,
        }

    def advance_game(self, engine_response=None):
        """
        Advance the game by one turn based on the AI player's strategy.

        Args:
            engine_response: Optional response from the AI engine

        Returns:
            Dictionary with the result of the turn
        """
        if self.ai_player.game_over or self.turn_count >= self.max_turns:
            return {
                'message': 'Game already over',
                'game_over': True,
                'won': self.ai_player.won,
                'turn_count': self.turn_count,
            }

        # Increment turn counter
        self.turn_count += 1

        # Make a strategic move
        move_result = self.ai_player.make_strategic_move()

        # Record the move in game history
        history_entry = {
            'turn': self.turn_count,
            'position': self.ai_player.position,
            'action': move_result,
            'health': self.ai_player.health,
            'resources': self.ai_player.resources_collected,
            'puzzles_solved': self.ai_player.puzzles_solved,
            'engine_response': engine_response,
        }
        self.game_history.append(history_entry)

        # Check if game is over
        game_over = self.ai_player.game_over or self.turn_count >= self.max_turns

        return {
            'message': move_result,
            'position': self.ai_player.position,
            'health': self.ai_player.health,
            'resources': self.ai_player.resources_collected,
            'puzzles_solved': self.ai_player.puzzles_solved,
            'boss_defeated': self.ai_player.boss_defeated,
            'game_over': game_over,
            'won': self.ai_player.won,
            'turn_count': self.turn_count,
        }

    def visualize_maze(self):
        """Return a string visualization of the maze with the AI player's position."""
        if self.maze is None:
            return 'No maze generated yet'

        # Create a copy of the maze for visualization
        viz_maze = self.maze.copy()

        # Mark the AI player's position with a special value (9)
        y, x = self.ai_player.position
        original_cell = viz_maze[y, x]
        viz_maze[y, x] = 9  # Special value for player

        # Create the visualization string
        symbols = {
            CellType.WALL.value: '██',
            CellType.PATH.value: '  ',
            CellType.START.value: 'S ',
            CellType.END.value: 'E ',
            CellType.RESOURCE.value: 'R ',
            CellType.TRAP.value: 'T ',
            CellType.PUZZLE.value: 'P ',
            CellType.BOSS.value: 'B ',
            9: 'AI',  # Player symbol
        }

        viz_str = ''
        for row in viz_maze:
            viz_str += ''.join(symbols[cell] for cell in row) + '\n'

        # Restore the original cell value
        viz_maze[y, x] = original_cell

        return viz_str

    def get_game_summary(self):
        """Get a summary of the current game state."""
        if self.maze is None or self.ai_player is None:
            return 'No game in progress'

        return {
            'maze_size': (self.height, self.width),
            'turn_count': self.turn_count,
            'player_position': self.ai_player.position,
            'health': self.ai_player.health,
            'resources_collected': self.ai_player.resources_collected,
            'puzzles_solved': self.ai_player.puzzles_solved,
            'boss_defeated': self.ai_player.boss_defeated,
            'game_over': self.ai_player.game_over,
            'won': self.ai_player.won,
            'path_length': len(self.ai_player.path_history),
            'unique_cells_visited': len(self.ai_player.visited),
        }
