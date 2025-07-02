import random
from enum import Enum

import numpy as np


class EnhancedCellType(Enum):
    """Enhanced cell types for the maze."""

    WALL = 0
    PATH = 1
    START = 2
    END = 3
    RESOURCE_SMALL = 4  # Small resource (health potion, etc.)
    RESOURCE_LARGE = 5  # Large resource (weapon, armor, etc.)
    TRAP_BASIC = 6  # Basic trap (spikes, etc.)
    TRAP_ADVANCED = 7  # Advanced trap (poison gas, etc.)
    PUZZLE_EASY = 8  # Easy puzzle (simple lock, etc.)
    PUZZLE_HARD = 9  # Hard puzzle (complex mechanism, etc.)
    BOSS_MINION = 10  # Boss minion (smaller enemy)
    BOSS = 11  # Main boss
    TELEPORT = 12  # Teleportation point
    SHOP = 13  # Shop to buy/sell items
    CHECKPOINT = 14  # Checkpoint to save progress
    SECRET = 15  # Secret passage or hidden item


class EnhancedMazeGenerator:
    """Generate enhanced mazes with various features."""

    def __init__(
        self, width=21, height=21, complexity=0.75, density=0.75, difficulty='medium'
    ):
        """
        Initialize the maze generator.

        Args:
            width: Width of the maze (must be odd)
            height: Height of the maze (must be odd)
            complexity: Complexity of the maze (0-1)
            density: Density of the maze (0-1)
            difficulty: Difficulty level ('easy', 'medium', 'hard')
        """
        # Ensure odd dimensions
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.complexity = complexity
        self.density = density
        self.difficulty = difficulty

        # Set feature counts based on difficulty
        if difficulty == 'easy':
            self.resource_count = int(width * height * 0.05)  # 5% of cells
            self.trap_count = int(width * height * 0.02)  # 2% of cells
            self.puzzle_count = 1
            self.boss_minion_count = 1
            self.teleport_count = 0
            self.shop_count = 1
            self.checkpoint_count = 2
            self.secret_count = 1
        elif difficulty == 'medium':
            self.resource_count = int(width * height * 0.04)  # 4% of cells
            self.trap_count = int(width * height * 0.04)  # 4% of cells
            self.puzzle_count = 2
            self.boss_minion_count = 2
            self.teleport_count = 1
            self.shop_count = 1
            self.checkpoint_count = 1
            self.secret_count = 2
        else:  # hard
            self.resource_count = int(width * height * 0.03)  # 3% of cells
            self.trap_count = int(width * height * 0.06)  # 6% of cells
            self.puzzle_count = 3
            self.boss_minion_count = 3
            self.teleport_count = 2
            self.shop_count = 1
            self.checkpoint_count = 1
            self.secret_count = 3

    def generate(self):
        """Generate a random maze with enhanced features."""
        # Initialize maze with walls
        maze = np.zeros((self.height, self.width), dtype=int)

        # Fill borders with walls
        maze[0, :] = EnhancedCellType.WALL.value
        maze[-1, :] = EnhancedCellType.WALL.value
        maze[:, 0] = EnhancedCellType.WALL.value
        maze[:, -1] = EnhancedCellType.WALL.value

        # Create passages using modified Prim's algorithm
        self._create_passages(maze)

        # Place start and end points
        self._place_start_end(maze)

        # Place enhanced features
        self._place_resources(maze)
        self._place_traps(maze)
        self._place_puzzles(maze)
        self._place_bosses(maze)
        self._place_special_features(maze)

        return maze

    def _create_passages(self, maze):
        """Create passages in the maze using modified Prim's algorithm."""
        # Fill maze with walls
        maze.fill(EnhancedCellType.WALL.value)

        # Create a grid of cells to be connected
        width, height = ((self.width - 1) // 2, (self.height - 1) // 2)

        # Adjust complexity and density
        complexity = int(self.complexity * (5 * (width + height)))
        density = int(self.density * ((width // 2) * (height // 2)))

        # Make a grid of all wall cells
        for i in range(density):
            # Pick a random cell
            x, y = (
                random.randint(0, width - 1) * 2 + 1,
                random.randint(0, height - 1) * 2 + 1,
            )
            maze[y, x] = EnhancedCellType.PATH.value

            # Carve passages
            for j in range(complexity):
                neighbors = []

                # Check neighbors in 4 directions
                if x > 1:
                    neighbors.append((y, x - 2))
                if x < self.width - 2:
                    neighbors.append((y, x + 2))
                if y > 1:
                    neighbors.append((y - 2, x))
                if y < self.height - 2:
                    neighbors.append((y + 2, x))

                if neighbors:
                    # Pick a random neighbor
                    y_next, x_next = random.choice(neighbors)

                    # Connect cells if not already connected
                    if maze[y_next, x_next] == EnhancedCellType.WALL.value:
                        maze[y_next, x_next] = EnhancedCellType.PATH.value
                        maze[y_next + (y - y_next) // 2, x_next + (x - x_next) // 2] = (
                            EnhancedCellType.PATH.value
                        )

                        # Update current cell
                        x, y = (x_next, y_next)

        # Ensure there are enough path cells
        path_cells = np.sum(maze == EnhancedCellType.PATH.value)
        min_path_cells = int(
            self.width * self.height * 0.3
        )  # At least 30% of cells should be paths

        if path_cells < min_path_cells:
            # Add more paths
            for _ in range(min_path_cells - path_cells):
                # Find a wall adjacent to a path
                wall_cells = []
                for y in range(1, self.height - 1):
                    for x in range(1, self.width - 1):
                        if maze[y, x] == EnhancedCellType.WALL.value:
                            # Check if adjacent to a path
                            if (
                                maze[y - 1, x] == EnhancedCellType.PATH.value
                                or maze[y + 1, x] == EnhancedCellType.PATH.value
                                or maze[y, x - 1] == EnhancedCellType.PATH.value
                                or maze[y, x + 1] == EnhancedCellType.PATH.value
                            ):
                                wall_cells.append((y, x))

                if wall_cells:
                    # Convert a random wall to a path
                    y, x = random.choice(wall_cells)
                    maze[y, x] = EnhancedCellType.PATH.value

    def _place_start_end(self, maze):
        """Place start and end points in the maze."""
        # Find all path cells
        path_cells = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if maze[y, x] == EnhancedCellType.PATH.value:
                    path_cells.append((y, x))

        # Ensure we have enough path cells
        if len(path_cells) < 2:
            raise ValueError('Not enough path cells to place start and end points')

        # Place start point in the top-left quadrant
        top_left_cells = [
            (y, x)
            for y, x in path_cells
            if y < self.height // 2 and x < self.width // 2
        ]

        if top_left_cells:
            start_pos = random.choice(top_left_cells)
        else:
            start_pos = random.choice(path_cells)

        maze[start_pos[0], start_pos[1]] = EnhancedCellType.START.value
        path_cells.remove(start_pos)

        # Place end point in the bottom-right quadrant
        bottom_right_cells = [
            (y, x)
            for y, x in path_cells
            if y >= self.height // 2 and x >= self.width // 2
        ]

        if bottom_right_cells:
            end_pos = random.choice(bottom_right_cells)
        else:
            end_pos = random.choice(path_cells)

        maze[end_pos[0], end_pos[1]] = EnhancedCellType.END.value
        path_cells.remove(end_pos)

        # Store remaining path cells for feature placement
        self.path_cells = path_cells

    def _place_resources(self, maze):
        """Place resources in the maze."""
        if not self.path_cells:
            return

        # Determine small vs large resource ratio (70% small, 30% large)
        small_count = int(self.resource_count * 0.7)
        large_count = self.resource_count - small_count

        # Place small resources
        for _ in range(min(small_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.RESOURCE_SMALL.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place large resources
        for _ in range(min(large_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.RESOURCE_LARGE.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

    def _place_traps(self, maze):
        """Place traps in the maze."""
        if not self.path_cells:
            return

        # Determine basic vs advanced trap ratio (60% basic, 40% advanced)
        basic_count = int(self.trap_count * 0.6)
        advanced_count = self.trap_count - basic_count

        # Place basic traps
        for _ in range(min(basic_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.TRAP_BASIC.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place advanced traps
        for _ in range(min(advanced_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.TRAP_ADVANCED.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

    def _place_puzzles(self, maze):
        """Place puzzles in the maze."""
        if not self.path_cells:
            return

        # Determine easy vs hard puzzle ratio (70% easy, 30% hard)
        easy_count = int(self.puzzle_count * 0.7)
        hard_count = self.puzzle_count - easy_count

        # Place easy puzzles
        for _ in range(min(easy_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.PUZZLE_EASY.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place hard puzzles
        for _ in range(min(hard_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.PUZZLE_HARD.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

    def _place_bosses(self, maze):
        """Place bosses in the maze."""
        if not self.path_cells:
            return

        # Place boss minions
        for _ in range(min(self.boss_minion_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.BOSS_MINION.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place main boss (preferably near the end)
        # Find cells near the end
        end_pos = None
        for y in range(self.height):
            for x in range(self.width):
                if maze[y, x] == EnhancedCellType.END.value:
                    end_pos = (y, x)
                    break
            if end_pos:
                break

        if end_pos and self.path_cells:
            # Sort path cells by distance to end
            self.path_cells.sort(
                key=lambda pos: abs(pos[0] - end_pos[0]) + abs(pos[1] - end_pos[1])
            )

            # Place boss in a cell that's close to the end but not too close
            boss_index = min(len(self.path_cells) // 3, len(self.path_cells) - 1)
            boss_pos = self.path_cells[boss_index]
            maze[boss_pos[0], boss_pos[1]] = EnhancedCellType.BOSS.value
            self.path_cells.remove(boss_pos)

    def _place_special_features(self, maze):
        """Place special features in the maze."""
        if not self.path_cells:
            return

        # Place teleport points
        for _ in range(min(self.teleport_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.TELEPORT.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place shops
        for _ in range(min(self.shop_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.SHOP.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place checkpoints
        for _ in range(min(self.checkpoint_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.CHECKPOINT.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

        # Place secret passages/items
        for _ in range(min(self.secret_count, len(self.path_cells))):
            pos = random.choice(self.path_cells)
            maze[pos[0], pos[1]] = EnhancedCellType.SECRET.value
            self.path_cells.remove(pos)

            if not self.path_cells:
                return

    def visualize_maze(self, maze=None):
        """
        Visualize the maze as a string.

        Args:
            maze: The maze to visualize (if None, generate a new maze)

        Returns:
            String representation of the maze
        """
        if maze is None:
            maze = self.generate()

        # Define symbols for each cell type
        symbols = {
            EnhancedCellType.WALL.value: '██',
            EnhancedCellType.PATH.value: '  ',
            EnhancedCellType.START.value: 'S ',
            EnhancedCellType.END.value: 'E ',
            EnhancedCellType.RESOURCE_SMALL.value: 'r ',
            EnhancedCellType.RESOURCE_LARGE.value: 'R ',
            EnhancedCellType.TRAP_BASIC.value: 't ',
            EnhancedCellType.TRAP_ADVANCED.value: 'T ',
            EnhancedCellType.PUZZLE_EASY.value: 'p ',
            EnhancedCellType.PUZZLE_HARD.value: 'P ',
            EnhancedCellType.BOSS_MINION.value: 'm ',
            EnhancedCellType.BOSS.value: 'B ',
            EnhancedCellType.TELEPORT.value: '⊕ ',
            EnhancedCellType.SHOP.value: '$ ',
            EnhancedCellType.CHECKPOINT.value: '⚑ ',
            EnhancedCellType.SECRET.value: '? ',
        }

        # Build the string representation
        result = []
        for row in maze:
            line = ''
            for cell in row:
                line += symbols.get(cell, '??')
            result.append(line)

        return '\n'.join(result)


# For backward compatibility
class CellType(Enum):
    """Cell types for the maze."""

    WALL = 0
    PATH = 1
    START = 2
    END = 3
    RESOURCE = 4
    TRAP = 5
    PUZZLE = 6
    BOSS = 7


# For backward compatibility
class MazeGenerator(EnhancedMazeGenerator):
    """Generate mazes with various features (backward compatibility)."""

    def generate(self):
        """Generate a random maze with features."""
        # Generate enhanced maze
        enhanced_maze = super().generate()

        # Convert to old format
        maze = np.zeros_like(enhanced_maze)

        # Map enhanced cell types to old cell types
        maze[enhanced_maze == EnhancedCellType.WALL.value] = CellType.WALL.value
        maze[enhanced_maze == EnhancedCellType.PATH.value] = CellType.PATH.value
        maze[enhanced_maze == EnhancedCellType.START.value] = CellType.START.value
        maze[enhanced_maze == EnhancedCellType.END.value] = CellType.END.value
        maze[enhanced_maze == EnhancedCellType.RESOURCE_SMALL.value] = (
            CellType.RESOURCE.value
        )
        maze[enhanced_maze == EnhancedCellType.RESOURCE_LARGE.value] = (
            CellType.RESOURCE.value
        )
        maze[enhanced_maze == EnhancedCellType.TRAP_BASIC.value] = CellType.TRAP.value
        maze[enhanced_maze == EnhancedCellType.TRAP_ADVANCED.value] = (
            CellType.TRAP.value
        )
        maze[enhanced_maze == EnhancedCellType.PUZZLE_EASY.value] = (
            CellType.PUZZLE.value
        )
        maze[enhanced_maze == EnhancedCellType.PUZZLE_HARD.value] = (
            CellType.PUZZLE.value
        )
        maze[enhanced_maze == EnhancedCellType.BOSS_MINION.value] = CellType.BOSS.value
        maze[enhanced_maze == EnhancedCellType.BOSS.value] = CellType.BOSS.value

        # Special features become paths in old format
        maze[enhanced_maze == EnhancedCellType.TELEPORT.value] = CellType.PATH.value
        maze[enhanced_maze == EnhancedCellType.SHOP.value] = CellType.PATH.value
        maze[enhanced_maze == EnhancedCellType.CHECKPOINT.value] = CellType.PATH.value
        maze[enhanced_maze == EnhancedCellType.SECRET.value] = CellType.PATH.value

        return maze

    def visualize_maze(self, maze=None):
        """
        Visualize the maze as a string.

        Args:
            maze: The maze to visualize (if None, generate a new maze)

        Returns:
            String representation of the maze
        """
        if maze is None:
            maze = self.generate()

        # Define symbols for each cell type
        symbols = {
            CellType.WALL.value: '██',
            CellType.PATH.value: '  ',
            CellType.START.value: 'S ',
            CellType.END.value: 'E ',
            CellType.RESOURCE.value: 'R ',
            CellType.TRAP.value: 'T ',
            CellType.PUZZLE.value: 'P ',
            CellType.BOSS.value: 'B ',
        }

        # Build the string representation
        result = []
        for row in maze:
            line = ''
            for cell in row:
                line += symbols.get(cell, '??')
            result.append(line)

        return '\n'.join(result)
