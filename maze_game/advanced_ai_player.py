import heapq
import random

import numpy as np
from maze_generator import CellType


class AdvancedAIPlayer:
    def __init__(self, maze, start_pos=None):
        """
        Initialize an advanced AI player for navigating the maze.

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

        # Complete solution path
        self.complete_solution = None
        self.solution_index = 0
        self.action_log = []

        # Calculate optimal solution immediately
        self.calculate_complete_solution()

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
            self.action_log.append(result)

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

    def find_path_to_target(self, target_type, avoid_types=None):
        """
        Find the shortest path to a specific target type using A* algorithm.

        Args:
            target_type: The cell type to find
            avoid_types: List of cell types to avoid (optional)

        Returns:
            List of positions forming the path, or None if no path found
        """
        if self.game_over:
            return None

        if avoid_types is None:
            avoid_types = []

        # A* algorithm implementation
        start = self.position

        # Find all target positions
        target_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y, x] == target_type:
                    target_positions.append((y, x))

        if not target_positions:
            return None

        # Heuristic function: Manhattan distance to closest target
        def heuristic(pos):
            return min(
                abs(pos[0] - t[0]) + abs(pos[1] - t[1]) for t in target_positions
            )

        # Priority queue for A*
        open_set = []
        # (f_score, position, path)
        heapq.heappush(open_set, (heuristic(start), start, []))

        # Closed set to avoid revisiting
        closed_set = set()

        while open_set:
            _, current, path = heapq.heappop(open_set)

            if current in closed_set:
                continue

            closed_set.add(current)

            # Check if we reached the target
            if self.maze[current[0], current[1]] == target_type:
                return path

            # Try all four directions
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = current[0] + dy, current[1] + dx
                next_pos = (ny, nx)

                if (
                    0 <= ny < self.height
                    and 0 <= nx < self.width
                    and self.maze[ny, nx] != CellType.WALL.value
                    and next_pos not in closed_set
                    and self.maze[ny, nx] not in avoid_types
                ):
                    new_path = path + [next_pos]
                    # f_score = g_score (path length) + heuristic
                    f_score = len(new_path) + heuristic(next_pos)

                    heapq.heappush(open_set, (f_score, next_pos, new_path))

        return None  # No path found

    def calculate_complete_solution(self):
        """Calculate the complete solution path through the maze."""
        # Reset player state for planning
        original_position = self.position
        original_health = self.health
        original_resources = self.resources_collected
        original_puzzles = self.puzzles_solved
        original_boss = self.boss_defeated

        # Plan the complete path
        complete_path = []
        action_sequence = []

        # Step 1: Collect resources first (prioritize closest ones)
        resource_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y, x] == CellType.RESOURCE.value:
                    resource_positions.append((y, x))

        # Sort resources by distance from current position
        resource_positions.sort(
            key=lambda pos: abs(pos[0] - self.position[0])
            + abs(pos[1] - self.position[1])
        )

        # Collect at least 3 resources or as many as available
        resources_to_collect = min(3, len(resource_positions))

        for i in range(resources_to_collect):
            target = resource_positions[i]
            path = self.find_path_to_target(CellType.RESOURCE.value)
            if path:
                complete_path.extend(path)
                action_sequence.append(f'Collecting resource at {target}')
                # Update position for next path calculation
                self.position = path[-1]
                self.resources_collected += 1

        # Step 2: Solve puzzles to gain advantage
        puzzle_path = self.find_path_to_target(CellType.PUZZLE.value)
        if puzzle_path:
            complete_path.extend(puzzle_path)
            action_sequence.append('Solving puzzle')
            self.position = puzzle_path[-1]
            self.puzzles_solved += 1

        # Step 3: Defeat the boss
        boss_path = self.find_path_to_target(CellType.BOSS.value)
        if boss_path:
            complete_path.extend(boss_path)
            action_sequence.append('Defeating boss')
            self.position = boss_path[-1]
            self.boss_defeated = True

        # Step 4: Head to the exit
        end_path = self.find_path_to_target(CellType.END.value)
        if end_path:
            complete_path.extend(end_path)
            action_sequence.append('Reaching the exit')
            self.position = end_path[-1]

        # Restore original state
        self.position = original_position
        self.health = original_health
        self.resources_collected = original_resources
        self.puzzles_solved = original_puzzles
        self.boss_defeated = original_boss

        # Store the complete solution
        self.complete_solution = complete_path
        self.solution_actions = action_sequence

        return complete_path

    def execute_complete_solution(self):
        """Execute the complete solution path at once."""
        if not self.complete_solution:
            return 'No solution available'

        results = []

        # Execute each step in the solution
        for pos in self.complete_solution:
            result = self.move_to(pos)
            results.append(result)

            # Stop if game over
            if self.game_over:
                break

        return results

    def make_strategic_move(self):
        """Make a strategic move based on current game state."""
        if self.game_over:
            return 'Game over'

        # If we have a complete solution, use it
        if self.complete_solution and self.solution_index < len(self.complete_solution):
            next_pos = self.complete_solution[self.solution_index]
            self.solution_index += 1
            return self.move_to(next_pos)

        # Otherwise, use the original strategic logic
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
            'solution_length': len(self.complete_solution)
            if self.complete_solution
            else 0,
            'solution_progress': self.solution_index,
            'action_log': self.action_log[-5:] if self.action_log else [],
        }

    def get_solution_path_visualization(self, maze_copy=None):
        """
        Get a visualization of the solution path on the maze.

        Args:
            maze_copy: Optional copy of the maze to visualize on

        Returns:
            2D numpy array with the solution path marked
        """
        if not self.complete_solution:
            return None

        if maze_copy is None:
            maze_copy = self.maze.copy()

        # Mark the solution path with a special value (10)
        for pos in self.complete_solution:
            y, x = pos
            # Don't overwrite special cells
            if maze_copy[y, x] == CellType.PATH.value:
                maze_copy[y, x] = 10  # Special value for solution path

        return maze_copy
