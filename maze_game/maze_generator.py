import random
from enum import Enum

import numpy as np


class CellType(Enum):
    WALL = 0
    PATH = 1
    START = 2
    END = 3
    RESOURCE = 4
    TRAP = 5
    PUZZLE = 6
    BOSS = 7


class MazeGenerator:
    def __init__(self, width, height, complexity=0.75, density=0.75):
        """
        Initialize a maze generator with given dimensions and parameters.

        Args:
            width: Width of the maze (must be odd)
            height: Height of the maze (must be odd)
            complexity: Complexity of the maze (0-1)
            density: Density of walls (0-1)
        """
        # Ensure dimensions are odd
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.complexity = complexity
        self.density = density

    def generate(self):
        """Generate a random maze using a modified version of Prim's algorithm."""
        # Initialize maze with walls
        maze = np.zeros((self.height, self.width), dtype=int)

        # Create walls
        for i in range(self.height):
            for j in range(self.width):
                if i == 0 or j == 0 or i == self.height - 1 or j == self.width - 1:
                    maze[i, j] = CellType.WALL.value
                elif i % 2 == 0 and j % 2 == 0:
                    maze[i, j] = CellType.WALL.value

        # Make passages
        for i in range(0, self.height, 2):
            for j in range(0, self.width, 2):
                if i > 0 and j > 0 and i < self.height - 1 and j < self.width - 1:
                    maze[i, j] = CellType.PATH.value

                    # Connect to a random adjacent cell
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
                    random.shuffle(directions)

                    for di, dj in directions:
                        ni, nj = i + di * 2, j + dj * 2
                        if 0 < ni < self.height - 1 and 0 < nj < self.width - 1:
                            if maze[ni, nj] == CellType.PATH.value:
                                maze[i + di, j + dj] = CellType.PATH.value
                                break

        # Add more random paths for complexity
        for _ in range(int((self.width * self.height) * self.complexity * 0.1)):
            x, y = random.randint(1, self.width - 2), random.randint(1, self.height - 2)
            if maze[y, x] == CellType.WALL.value:
                # Check if making this a path would create a 2x2 open area
                neighbors = [(y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)]
                path_neighbors = sum(
                    1
                    for ny, nx in neighbors
                    if 0 <= ny < self.height
                    and 0 <= nx < self.width
                    and maze[ny, nx] == CellType.PATH.value
                )

                if (
                    path_neighbors <= 2
                ):  # Only create a path if it won't create a 2x2 open area
                    maze[y, x] = CellType.PATH.value

        # Set start and end points
        # Start at top left area
        start_candidates = [
            (i, j)
            for i in range(1, self.height // 3)
            for j in range(1, self.width // 3)
            if maze[i, j] == CellType.PATH.value
        ]
        if start_candidates:
            start_y, start_x = random.choice(start_candidates)
            maze[start_y, start_x] = CellType.START.value
        else:
            # Fallback if no suitable start found
            maze[1, 1] = CellType.START.value

        # End at bottom right area
        end_candidates = [
            (i, j)
            for i in range(self.height * 2 // 3, self.height - 1)
            for j in range(self.width * 2 // 3, self.width - 1)
            if maze[i, j] == CellType.PATH.value
        ]
        if end_candidates:
            end_y, end_x = random.choice(end_candidates)
            maze[end_y, end_x] = CellType.END.value
        else:
            # Fallback if no suitable end found
            maze[self.height - 2, self.width - 2] = CellType.END.value

        # Add resources, traps, puzzles, and boss
        self._add_features(maze)

        return maze

    def _add_features(self, maze):
        """Add resources, traps, puzzles, and boss to the maze."""
        path_cells = [
            (i, j)
            for i in range(1, self.height - 1)
            for j in range(1, self.width - 1)
            if maze[i, j] == CellType.PATH.value
        ]

        if not path_cells:
            return

        # Add resources (10% of path cells)
        resource_count = max(1, int(len(path_cells) * 0.1))
        for _ in range(resource_count):
            if not path_cells:
                break
            y, x = path_cells.pop(random.randrange(len(path_cells)))
            maze[y, x] = CellType.RESOURCE.value

        # Add traps (5% of path cells)
        trap_count = max(1, int(len(path_cells) * 0.05))
        for _ in range(trap_count):
            if not path_cells:
                break
            y, x = path_cells.pop(random.randrange(len(path_cells)))
            maze[y, x] = CellType.TRAP.value

        # Add puzzles (3% of path cells)
        puzzle_count = max(1, int(len(path_cells) * 0.03))
        for _ in range(puzzle_count):
            if not path_cells:
                break
            y, x = path_cells.pop(random.randrange(len(path_cells)))
            maze[y, x] = CellType.PUZZLE.value

        # Add boss (1 near the end)
        if path_cells:
            # Find cells near the end
            end_pos = [
                (i, j)
                for i in range(self.height)
                for j in range(self.width)
                if maze[i, j] == CellType.END.value
            ]

            if end_pos:
                end_y, end_x = end_pos[0]
                # Get path cells sorted by distance to end
                path_cells.sort(
                    key=lambda pos: abs(pos[0] - end_y) + abs(pos[1] - end_x)
                )

                # Place boss in the first third of the path closest to the end
                boss_candidates = path_cells[: max(1, len(path_cells) // 3)]
                if boss_candidates:
                    y, x = random.choice(boss_candidates)
                    maze[y, x] = CellType.BOSS.value

    def get_cell_type_name(self, cell_value):
        """Convert cell value to its name."""
        for cell_type in CellType:
            if cell_type.value == cell_value:
                return cell_type.name
        return 'UNKNOWN'

    def print_maze(self, maze):
        """Print the maze in a readable format."""
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

        for row in maze:
            print(''.join(symbols[cell] for cell in row))
