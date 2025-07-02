import random
from collections import deque

import numpy as np
from maze_generator import CellType


class AIPlayer:
    def __init__(self, maze, start_pos=None):
        """
        Initialize an AI player for navigating the maze.

        Args:
            maze: 2D numpy array representing the maze
            start_pos: Starting position (y, x) or None to find automatically
        """
        self.maze = maze
        self.height, self.width = maze.shape

        # Find start position if not provided
        if start_pos is None:
            start_positions = np.where(maze == CellType.START.value)
            if len(start_positions[0]) > 0:
                self.position = (start_positions[0][0], start_positions[1][0])
            else:
                # Default to top-left corner if no start position found
                self.position = (1, 1)
        else:
            self.position = start_pos

        # Initialize player state
        self.resources_collected = 0
        self.health = 100
        self.puzzles_solved = 0
        self.boss_defeated = False
        self.game_over = False
        self.won = False
        self.visited = set([self.position])
        self.path_history = [self.position]

        # Knowledge of the maze
        self.known_maze = np.full_like(maze, -1)  # -1 represents unknown
        self.update_known_maze()

    def update_known_maze(self):
        """Update the player's knowledge of the maze based on current position."""
        y, x = self.position

        # Mark current position as known
        self.known_maze[y, x] = self.maze[y, x]

        # Mark adjacent cells as known
        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ny, nx = y + dy, x + dx
            if 0 <= ny < self.height and 0 <= nx < self.width:
                self.known_maze[ny, nx] = self.maze[ny, nx]

    def get_valid_moves(self):
        """Get list of valid moves from current position."""
        y, x = self.position
        valid_moves = []

        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < self.height
                and 0 <= nx < self.width
                and self.maze[ny, nx] != CellType.WALL.value
            ):
                valid_moves.append((ny, nx))

        return valid_moves

    def move_random(self):
        """Move randomly to a valid adjacent cell."""
        valid_moves = self.get_valid_moves()
        if valid_moves:
            next_pos = random.choice(valid_moves)
            return self.move_to(next_pos)
        return 'No valid moves available'

    def move_to(self, position):
        """Move to a specific position and handle the consequences."""
        if position in self.get_valid_moves():
            y, x = position
            cell_type = self.maze[y, x]

            # Update position
            self.position = position
            self.visited.add(position)
            self.path_history.append(position)
            self.update_known_maze()

            # Handle cell effects
            result = self._handle_cell_effect(cell_type)

            # Check win/lose conditions
            self._check_game_state()

            return result
        else:
            return 'Invalid move'

    def _handle_cell_effect(self, cell_type):
        """Handle the effect of landing on a specific cell type."""
        if cell_type == CellType.RESOURCE.value:
            self.resources_collected += 1
            return 'Collected a resource!'

        elif cell_type == CellType.TRAP.value:
            damage = random.randint(10, 30)
            self.health -= damage
            return f'Triggered a trap! Lost {damage} health.'

        elif cell_type == CellType.PUZZLE.value:
            # Simulate puzzle solving with a chance of success
            if random.random() < 0.7:  # 70% chance to solve
                self.puzzles_solved += 1
                return 'Solved a puzzle!'
            else:
                return 'Failed to solve the puzzle.'

        elif cell_type == CellType.BOSS.value:
            # Boss battle outcome depends on resources and puzzles solved
            success_chance = (
                0.3 + (self.resources_collected * 0.1) + (self.puzzles_solved * 0.15)
            )
            if random.random() < success_chance:
                self.boss_defeated = True
                return 'Defeated the boss!'
            else:
                damage = random.randint(30, 50)
                self.health -= damage
                return f'Lost the boss battle! Lost {damage} health.'

        elif cell_type == CellType.END.value:
            if self.boss_defeated:
                self.won = True
                return 'Reached the end! Victory!'
            else:
                return 'Reached the end, but must defeat the boss first!'

        elif cell_type == CellType.START.value:
            return 'Back at the starting point.'

        else:  # PATH
            return 'Moved to an empty path.'

    def _check_game_state(self):
        """Check if the game is over (win or lose)."""
        if self.health <= 0:
            self.game_over = True
            self.won = False
        elif self.won:
            self.game_over = True

    def find_path_to_target(self, target_type):
        """Find the shortest path to a specific target type using BFS."""
        if self.game_over:
            return None

        # Use BFS to find the shortest path
        queue = deque([(self.position, [])])
        visited = set([self.position])

        while queue:
            (y, x), path = queue.popleft()

            # Check if current position is the target
            if self.maze[y, x] == target_type:
                return path

            # Try all four directions
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = y + dy, x + dx
                if (
                    0 <= ny < self.height
                    and 0 <= nx < self.width
                    and self.maze[ny, nx] != CellType.WALL.value
                    and (ny, nx) not in visited
                ):
                    new_path = path + [(ny, nx)]
                    queue.append(((ny, nx), new_path))
                    visited.add((ny, nx))

        return None  # No path found

    def make_strategic_move(self):
        """Make a strategic move based on current game state."""
        if self.game_over:
            return 'Game over'

        # Priority 1: If at low health and resources are available, go for resources
        if self.health < 40 and not self.resources_collected:
            path = self.find_path_to_target(CellType.RESOURCE.value)
            if path and len(path) > 0:
                return self.move_to(path[0])

        # Priority 2: If boss not defeated and we have resources, go for boss
        if not self.boss_defeated and self.resources_collected > 0:
            path = self.find_path_to_target(CellType.BOSS.value)
            if path and len(path) > 0:
                return self.move_to(path[0])

        # Priority 3: If boss defeated, go for end
        if self.boss_defeated:
            path = self.find_path_to_target(CellType.END.value)
            if path and len(path) > 0:
                return self.move_to(path[0])

        # Priority 4: Collect resources
        path = self.find_path_to_target(CellType.RESOURCE.value)
        if path and len(path) > 0:
            return self.move_to(path[0])

        # Priority 5: Solve puzzles
        path = self.find_path_to_target(CellType.PUZZLE.value)
        if path and len(path) > 0:
            return self.move_to(path[0])

        # Priority 6: Go for boss even without resources
        path = self.find_path_to_target(CellType.BOSS.value)
        if path and len(path) > 0:
            return self.move_to(path[0])

        # Priority 7: Explore unvisited paths
        valid_moves = self.get_valid_moves()
        unvisited_moves = [move for move in valid_moves if move not in self.visited]

        if unvisited_moves:
            return self.move_to(random.choice(unvisited_moves))

        # Fallback: Move randomly
        return self.move_random()

    def get_status(self):
        """Get the current status of the AI player."""
        return {
            'position': self.position,
            'health': self.health,
            'resources': self.resources_collected,
            'puzzles_solved': self.puzzles_solved,
            'boss_defeated': self.boss_defeated,
            'game_over': self.game_over,
            'won': self.won,
        }
