import heapq

import numpy as np
from enhanced_maze_generator import EnhancedCellType
from optimized_ai_player import OptimizedAIPlayer


class LimitedVisionAI(OptimizedAIPlayer):
    """
    Super intelligent AI with limited vision (3x3) that optimizes for both
    finding the exit and collecting maximum resources.
    """

    def __init__(self, maze, start_pos=None):
        """Initialize the limited vision AI player."""
        super().__init__(maze, start_pos)

        # Limited vision parameters
        self.vision_range = 1  # 3x3 grid (1 cell in each direction)

        # Initialize fog of war - what the AI has seen
        self.fog_of_war = np.full_like(maze, -1)  # -1 represents unknown
        self.update_fog_of_war()

        # Resource tracking
        self.collected_resources = 0
        self.resource_positions = set()  # Track known resource positions
        self.collected_positions = set()  # Track collected resource positions

        # Memory of maze structure for path planning
        self.memory_maze = np.full_like(maze, -1)  # -1 represents unknown
        self.update_memory_maze()

        # Exploration parameters
        self.exploration_score = np.zeros_like(maze, dtype=float)
        self.last_exploration_update = 0
        self.exploration_decay = 0.95  # Decay factor for exploration scores

        # Path planning
        self.current_path = []
        self.current_target = None
        self.path_recompute_frequency = 5  # Recompute path every N turns

        # Resource value estimation
        self.resource_value = {
            EnhancedCellType.RESOURCE_SMALL.value: 10,
            EnhancedCellType.RESOURCE_LARGE.value: 25,
        }

        # End goal value (increases over time)
        self.end_value_base = 50
        self.end_value_increment = 2  # Increases by this amount each turn

        # Adaptive parameters
        self.resource_density = 0.0  # Estimated resource density
        self.resource_count = 0  # Number of resources seen
        self.cells_seen = 0  # Number of cells seen

        # Initialize the first path planning
        self.plan_optimal_path()

    def update_fog_of_war(self):
        """Update what the AI can see within its limited vision."""
        y, x = self.position
        vision_range = self.vision_range

        # Update what the AI can see in its 3x3 vision
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                ny, nx = y + dy, x + dx
                if 0 <= ny < self.height and 0 <= nx < self.width:
                    cell_value = self.maze[ny, nx]
                    self.fog_of_war[ny, nx] = cell_value

                    # Track resources
                    if cell_value in [
                        EnhancedCellType.RESOURCE_SMALL.value,
                        EnhancedCellType.RESOURCE_LARGE.value,
                    ]:
                        self.resource_positions.add((ny, nx))

                    # Update statistics for adaptive behavior
                    if self.fog_of_war[ny, nx] == -1:  # If this is a newly seen cell
                        self.cells_seen += 1
                        if cell_value in [
                            EnhancedCellType.RESOURCE_SMALL.value,
                            EnhancedCellType.RESOURCE_LARGE.value,
                        ]:
                            self.resource_count += 1

        # Update resource density estimate
        if self.cells_seen > 0:
            self.resource_density = self.resource_count / self.cells_seen

    def update_memory_maze(self):
        """Update the AI's memory of the maze structure."""
        # Copy what we can see to memory
        mask = self.fog_of_war != -1
        self.memory_maze[mask] = self.fog_of_war[mask]

        # Mark collected resources as paths in memory
        for pos in self.collected_positions:
            y, x = pos
            self.memory_maze[y, x] = EnhancedCellType.PATH.value

    def update_exploration_scores(self):
        """Update exploration scores to guide the AI toward unexplored areas."""
        # Decay all exploration scores
        self.exploration_score *= self.exploration_decay

        # Increase exploration score for frontier cells (known cells adjacent to unknown cells)
        frontier_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if (
                    self.memory_maze[y, x] != -1
                    and self.memory_maze[y, x] != EnhancedCellType.WALL.value
                ):
                    # Check if this cell is adjacent to an unknown cell
                    for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ny, nx = y + dy, x + dx
                        if (
                            0 <= ny < self.height
                            and 0 <= nx < self.width
                            and self.memory_maze[ny, nx] == -1
                        ):
                            frontier_cells.append((y, x))
                            break

        # Boost exploration score for frontier cells
        for y, x in frontier_cells:
            self.exploration_score[y, x] += 5.0

        # Current position has 0 exploration value
        y, x = self.position
        self.exploration_score[y, x] = 0.0

        self.last_exploration_update = self.turn_count

    def collect_resource(self, position):
        """Collect a resource at the given position."""
        y, x = position
        if (
            0 <= y < self.height
            and 0 <= x < self.width
            and self.maze[y, x]
            in [
                EnhancedCellType.RESOURCE_SMALL.value,
                EnhancedCellType.RESOURCE_LARGE.value,
            ]
        ):
            # Mark as collected
            self.collected_positions.add(position)
            if position in self.resource_positions:
                self.resource_positions.remove(position)

            # Update collected count
            self.collected_resources += 1

            # Update maze (resource disappears)
            self.maze[y, x] = EnhancedCellType.PATH.value

            # Update memory
            self.memory_maze[y, x] = EnhancedCellType.PATH.value

            return True
        return False

    def move_to(self, position):
        """Override move_to to handle resource collection and fog of war updates."""
        # Check if moving to a resource
        y, x = position
        if (
            0 <= y < self.height
            and 0 <= x < self.width
            and self.maze[y, x]
            in [
                EnhancedCellType.RESOURCE_SMALL.value,
                EnhancedCellType.RESOURCE_LARGE.value,
            ]
        ):
            self.collect_resource(position)

        # Call parent method to perform the actual move
        result = super().move_to(position)

        # Update what the AI can see
        self.update_fog_of_war()
        self.update_memory_maze()

        # Update exploration scores periodically
        if self.turn_count - self.last_exploration_update >= 3:
            self.update_exploration_scores()

        # Recompute path if needed
        if (
            not self.current_path
            or self.turn_count % self.path_recompute_frequency == 0
        ):
            self.plan_optimal_path()

        return result

    def estimate_path_value(self, path, target_type):
        """Estimate the value of a path considering resources along the way."""
        if not path:
            return -float('inf')

        value = 0
        resources_on_path = 0

        # Value of resources along the path
        for i, pos in enumerate(path):
            y, x = pos
            if (
                0 <= y < self.height
                and 0 <= x < self.width
                and self.memory_maze[y, x]
                in [
                    EnhancedCellType.RESOURCE_SMALL.value,
                    EnhancedCellType.RESOURCE_LARGE.value,
                ]
            ):
                # Resources earlier in the path are more valuable (discount factor)
                discount = 0.95**i
                resource_value = self.resource_value.get(self.memory_maze[y, x], 0)
                value += resource_value * discount
                resources_on_path += 1

        # Value of the target
        if target_type == EnhancedCellType.END.value:
            # End value increases over time to ensure we eventually go there
            end_value = self.end_value_base + self.turn_count * self.end_value_increment
            value += end_value
        elif target_type in [
            EnhancedCellType.RESOURCE_SMALL.value,
            EnhancedCellType.RESOURCE_LARGE.value,
        ]:
            value += self.resource_value.get(target_type, 0)

        # Exploration value
        for pos in path:
            y, x = pos
            if 0 <= y < self.height and 0 <= x < self.width:
                value += self.exploration_score[y, x]

        # Penalize longer paths slightly
        path_length_penalty = len(path) * 0.5
        value -= path_length_penalty

        return value, resources_on_path

    def find_path_in_memory(self, target_pos):
        """Find a path to a target position using the AI's memory of the maze."""
        if not target_pos:
            return None

        # A* algorithm implementation
        start = self.position
        target_y, target_x = target_pos

        # Heuristic function: Manhattan distance
        def heuristic(pos):
            return abs(pos[0] - target_y) + abs(pos[1] - target_x)

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
            if current == target_pos:
                return path + [current]

            # Try all four directions
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = current[0] + dy, current[1] + dx
                next_pos = (ny, nx)

                if (
                    0 <= ny < self.height
                    and 0 <= nx < self.width
                    and next_pos not in closed_set
                ):
                    # Check if the cell is traversable based on memory
                    cell_memory = self.memory_maze[ny, nx]

                    # If unknown or known to be traversable
                    if cell_memory == -1 or (
                        cell_memory != EnhancedCellType.WALL.value
                    ):
                        new_path = path + [current]
                        # f_score = g_score (path length) + heuristic
                        f_score = len(new_path) + heuristic(next_pos)

                        # If it's unknown, add a small penalty
                        if cell_memory == -1:
                            f_score += 2

                        heapq.heappush(open_set, (f_score, next_pos, new_path))

        return None  # No path found

    def find_nearest_resource(self):
        """Find the nearest known resource."""
        if not self.resource_positions:
            return None

        # Find paths to all known resources
        resource_paths = []
        for resource_pos in self.resource_positions:
            path = self.find_path_in_memory(resource_pos)
            if path:
                # Get the resource type
                y, x = resource_pos
                resource_type = self.memory_maze[y, x]
                # Estimate the value of this path
                value, resources = self.estimate_path_value(path, resource_type)
                resource_paths.append((value, resources, path, resource_pos))

        # Sort by value (highest first)
        resource_paths.sort(reverse=True)

        if resource_paths:
            return resource_paths[0][3], resource_paths[0][2]  # position, path
        return None, None

    def find_path_to_end(self):
        """Find a path to the end, considering resources along the way."""
        # Find the end position
        end_positions = []
        for y in range(self.height):
            for x in range(self.width):
                if self.memory_maze[y, x] == EnhancedCellType.END.value:
                    end_positions.append((y, x))

        if not end_positions:
            return None, None

        # Find paths to all known end positions
        end_paths = []
        for end_pos in end_positions:
            path = self.find_path_in_memory(end_pos)
            if path:
                # Estimate the value of this path
                value, resources = self.estimate_path_value(
                    path, EnhancedCellType.END.value
                )
                end_paths.append((value, resources, path, end_pos))

        # Sort by value (highest first)
        end_paths.sort(reverse=True)

        if end_paths:
            return end_paths[0][3], end_paths[0][2]  # position, path
        return None, None

    def find_exploration_target(self):
        """Find a good exploration target."""
        # Find frontier cells (known cells adjacent to unknown cells)
        frontier_cells = []
        for y in range(self.height):
            for x in range(self.width):
                if (
                    self.memory_maze[y, x] != -1
                    and self.memory_maze[y, x] != EnhancedCellType.WALL.value
                ):
                    # Check if this cell is adjacent to an unknown cell
                    for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        ny, nx = y + dy, x + dx
                        if (
                            0 <= ny < self.height
                            and 0 <= nx < self.width
                            and self.memory_maze[ny, nx] == -1
                        ):
                            frontier_cells.append((y, x))
                            break

        if not frontier_cells:
            return None, None

        # Find paths to frontier cells
        frontier_paths = []
        for frontier_pos in frontier_cells:
            path = self.find_path_in_memory(frontier_pos)
            if path:
                # Use exploration score as value
                y, x = frontier_pos
                value = (
                    self.exploration_score[y, x] - len(path) * 0.5
                )  # Penalize distance
                frontier_paths.append((value, path, frontier_pos))

        # Sort by value (highest first)
        frontier_paths.sort(reverse=True)

        if frontier_paths and len(frontier_paths) > 0:
            return frontier_paths[0][2], frontier_paths[0][1]  # position, path
        return None, None

    def plan_optimal_path(self):
        """Plan the optimal path considering resources and the end goal."""
        # If we've already defeated the boss, prioritize the end
        if self.stats.boss_defeated:
            end_pos, end_path = self.find_path_to_end()
            if end_path:
                self.current_target = end_pos
                self.current_path = end_path
                return

        # Find paths to resources and end
        resource_pos, resource_path = self.find_nearest_resource()
        end_pos, end_path = self.find_path_to_end()

        # Evaluate paths
        resource_value = -float('inf')
        end_value = -float('inf')

        if resource_path:
            resource_value, resource_count = self.estimate_path_value(
                resource_path, self.memory_maze[resource_pos[0], resource_pos[1]]
            )

        if end_path:
            end_value, end_resource_count = self.estimate_path_value(
                end_path, EnhancedCellType.END.value
            )

        # Choose the best path
        if resource_value > end_value and resource_path:
            self.current_target = resource_pos
            self.current_path = resource_path
        elif end_path:
            self.current_target = end_pos
            self.current_path = end_path
        else:
            # If no good path to resources or end, explore
            explore_pos, explore_path = self.find_exploration_target()
            if explore_path:
                self.current_target = explore_pos
                self.current_path = explore_path

    def make_strategic_move(self):
        """Make a strategic move based on the planned path."""
        if self.game_over:
            return 'Game over'

        # If we're at a resource, collect it
        y, x = self.position
        if self.maze[y, x] in [
            EnhancedCellType.RESOURCE_SMALL.value,
            EnhancedCellType.RESOURCE_LARGE.value,
        ]:
            self.collect_resource(self.position)

        # If we need to recompute the path
        if (
            not self.current_path
            or self.turn_count % self.path_recompute_frequency == 0
        ):
            self.plan_optimal_path()

        # If we have a path, follow it
        if self.current_path and len(self.current_path) > 0:
            next_pos = self.current_path[0]
            self.current_path = self.current_path[1:]
            return self.move_to(next_pos)

        # If no path, explore
        explore_pos, explore_path = self.find_exploration_target()
        if explore_path and len(explore_path) > 0:
            return self.move_to(explore_path[0])

        # Fallback: move randomly to a valid adjacent cell
        return self.move_random()

    def get_status(self):
        """Get the current status of the AI player."""
        status = super().get_status()

        # Add limited vision AI specific information
        status['collected_resources'] = self.collected_resources
        status['known_resources'] = len(self.resource_positions)
        status['cells_seen'] = self.cells_seen
        status['resource_density'] = self.resource_density
        status['current_target_type'] = (
            self.memory_maze[self.current_target[0], self.current_target[1]]
            if self.current_target
            else None
        )

        return status

    def get_fog_of_war_visualization(self):
        """Get a visualization of the fog of war."""
        # Create a copy of the maze for visualization
        viz_maze = np.full_like(self.maze, -1)  # -1 for unknown

        # Fill in what the AI knows
        viz_maze[self.fog_of_war != -1] = self.fog_of_war[self.fog_of_war != -1]

        # Mark the player's position
        y, x = self.position
        viz_maze[y, x] = 99  # Special value for player

        # Mark the 3x3 vision area
        vision_range = self.vision_range
        for dy in range(-vision_range, vision_range + 1):
            for dx in range(-vision_range, vision_range + 1):
                ny, nx = y + dy, x + dx
                if (
                    0 <= ny < self.height
                    and 0 <= nx < self.width
                    and viz_maze[ny, nx] == -1
                ):
                    viz_maze[ny, nx] = 98  # Special value for vision boundary

        # Mark collected resources
        for pos in self.collected_positions:
            cy, cx = pos
            if viz_maze[cy, cx] != 99:  # Don't overwrite player
                viz_maze[cy, cx] = 97  # Special value for collected resources

        # If we have a path, mark it
        if self.current_path:
            for pos in self.current_path:
                py, px = pos
                if viz_maze[py, px] != 99:  # Don't overwrite player
                    viz_maze[py, px] = 96  # Special value for path

        return viz_maze
