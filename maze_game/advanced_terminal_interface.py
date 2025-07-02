#!/usr/bin/env python3
import curses
import time

from advanced_ai_player import AdvancedAIPlayer
from maze_generator import CellType, MazeGenerator


class AdvancedTerminalInterface:
    def __init__(self, stdscr):
        """Initialize the advanced terminal interface."""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        # Initialize colors
        self._init_colors()

        # Initialize maze and player
        self.maze_generator = MazeGenerator(21, 21, complexity=0.8, density=0.7)
        self.maze = self.maze_generator.generate()
        self.ai_player = AdvancedAIPlayer(self.maze)

        # Game state
        self.game_over = False
        self.won = False
        self.log_messages = ['Welcome to the Advanced Maze Adventure!']
        self.auto_mode = False
        self.auto_delay = 0.2  # seconds between moves in auto mode
        self.solution_visible = False

    def _init_colors(self):
        """Initialize color pairs for the interface."""
        curses.start_color()
        curses.use_default_colors()

        # Define color pairs
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Default
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Wall
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Path
        curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)  # Start
        curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # End
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Resource
        curses.init_pair(7, curses.COLOR_RED, curses.COLOR_BLACK)  # Trap
        curses.init_pair(8, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Puzzle
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_YELLOW)  # Boss
        curses.init_pair(10, curses.COLOR_WHITE, curses.COLOR_GREEN)  # Player
        curses.init_pair(11, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Solution path

    def draw_maze(self):
        """Draw the maze on the screen."""
        maze_height, maze_width = self.maze.shape

        # Get a copy of the maze for visualization
        if self.solution_visible:
            viz_maze = self.ai_player.get_solution_path_visualization()
            if viz_maze is None:
                viz_maze = self.maze.copy()
        else:
            viz_maze = self.maze.copy()

        # Mark the player's position
        player_y, player_x = self.ai_player.position
        original_cell = viz_maze[player_y, player_x]
        viz_maze[player_y, player_x] = 99  # Special value for player

        # Calculate starting position to center the maze
        start_y = max(0, (self.height - maze_height) // 2)
        start_x = max(
            0, (self.width - maze_width * 2) // 2
        )  # Each cell is 2 chars wide

        # Draw the maze
        for y in range(maze_height):
            for x in range(maze_width):
                if y + start_y < self.height and x * 2 + start_x + 1 < self.width:
                    cell_value = viz_maze[y, x]

                    # Set color and symbol based on cell type
                    if cell_value == CellType.WALL.value:
                        color = curses.color_pair(2)
                        symbol = '██'
                    elif cell_value == CellType.PATH.value:
                        color = curses.color_pair(3)
                        symbol = '  '
                    elif cell_value == CellType.START.value:
                        color = curses.color_pair(4)
                        symbol = 'S '
                    elif cell_value == CellType.END.value:
                        color = curses.color_pair(5)
                        symbol = 'E '
                    elif cell_value == CellType.RESOURCE.value:
                        color = curses.color_pair(6)
                        symbol = 'R '
                    elif cell_value == CellType.TRAP.value:
                        color = curses.color_pair(7)
                        symbol = 'T '
                    elif cell_value == CellType.PUZZLE.value:
                        color = curses.color_pair(8)
                        symbol = 'P '
                    elif cell_value == CellType.BOSS.value:
                        color = curses.color_pair(9)
                        symbol = 'B '
                    elif cell_value == 99:  # Player
                        color = curses.color_pair(10)
                        symbol = 'AI'
                    elif cell_value == 10:  # Solution path
                        color = curses.color_pair(11)
                        symbol = '· '
                    else:
                        color = curses.color_pair(1)
                        symbol = '??'

                    try:
                        self.stdscr.addstr(y + start_y, x * 2 + start_x, symbol, color)
                    except curses.error:
                        # Ignore errors from writing to the bottom-right corner
                        pass

        # Restore the original cell value
        viz_maze[player_y, player_x] = original_cell

    def draw_status(self):
        """Draw the player status information."""
        status = self.ai_player.get_status()

        # Calculate position for status display
        maze_height, maze_width = self.maze.shape
        start_y = max(0, (self.height - maze_height) // 2) + maze_height + 1

        # Draw status bar
        status_line = (
            f'Health: {status["health"]} | Resources: {status["resources"]} | '
            f'Puzzles: {status["puzzles_solved"]} | Boss: {"Defeated" if status["boss_defeated"] else "Alive"}'
        )

        try:
            self.stdscr.addstr(
                start_y, 2, status_line, curses.color_pair(1) | curses.A_BOLD
            )
        except curses.error:
            pass

        # Draw solution progress if available
        if 'solution_length' in status and status['solution_length'] > 0:
            progress = f'Solution: {status["solution_progress"]}/{status["solution_length"]} steps'
            try:
                self.stdscr.addstr(start_y + 1, 2, progress, curses.color_pair(1))
            except curses.error:
                pass

    def draw_log(self):
        """Draw the game log messages."""
        maze_height, maze_width = self.maze.shape
        start_y = max(0, (self.height - maze_height) // 2) + maze_height + 3

        # Draw log header
        try:
            self.stdscr.addstr(
                start_y, 2, 'Game Log:', curses.color_pair(1) | curses.A_BOLD
            )
        except curses.error:
            pass

        # Draw log messages (last 5)
        max_log_lines = min(5, self.height - start_y - 2)
        for i, msg in enumerate(self.log_messages[-max_log_lines:]):
            if start_y + i + 1 < self.height:
                try:
                    self.stdscr.addstr(start_y + i + 1, 4, msg, curses.color_pair(1))
                except curses.error:
                    pass

    def draw_menu(self):
        """Draw the menu options."""
        try:
            self.stdscr.addstr(
                2, 2, 'ADVANCED MAZE ADVENTURE', curses.color_pair(1) | curses.A_BOLD
            )
            self.stdscr.addstr(4, 2, 'Controls:', curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(5, 4, 'N - New Game', curses.color_pair(1))
            self.stdscr.addstr(6, 4, 'A - Toggle Auto Mode', curses.color_pair(1))
            self.stdscr.addstr(
                7, 4, 'S - Show/Hide Solution Path', curses.color_pair(1)
            )
            self.stdscr.addstr(
                8, 4, 'E - Execute Complete Solution', curses.color_pair(1)
            )
            self.stdscr.addstr(9, 4, 'Q - Quit', curses.color_pair(1))

            # Show auto mode status
            auto_status = 'ON' if self.auto_mode else 'OFF'
            self.stdscr.addstr(
                11,
                4,
                f'Auto Mode: {auto_status}',
                curses.color_pair(1) | (curses.A_BOLD if self.auto_mode else 0),
            )

            # Show solution visibility status
            solution_status = 'VISIBLE' if self.solution_visible else 'HIDDEN'
            self.stdscr.addstr(
                12,
                4,
                f'Solution Path: {solution_status}',
                curses.color_pair(1) | (curses.A_BOLD if self.solution_visible else 0),
            )
        except curses.error:
            pass

    def new_game(self):
        """Start a new game."""
        self.maze = self.maze_generator.generate()
        self.ai_player = AdvancedAIPlayer(self.maze)
        self.game_over = False
        self.won = False
        self.log_messages = ['New game started!']
        self.auto_mode = False
        self.solution_visible = False

    def advance_game(self):
        """Advance the game by one turn."""
        if self.game_over:
            return

        result = self.ai_player.make_strategic_move()
        self.log_messages.append(result)

        # Check if game is over
        status = self.ai_player.get_status()
        self.game_over = status['game_over']
        self.won = status['won']

        if self.game_over:
            if self.won:
                self.log_messages.append('Victory! You have completed the maze!')
            else:
                self.log_messages.append(
                    'Game over! You have failed to complete the maze.'
                )

    def execute_solution(self):
        """Execute the complete solution at once."""
        if self.game_over:
            return

        results = self.ai_player.execute_complete_solution()
        if isinstance(results, list):
            self.log_messages.append(
                f'Executed complete solution ({len(results)} steps)'
            )
            # Add the last few results to the log
            for result in results[-3:]:
                self.log_messages.append(result)
        else:
            self.log_messages.append(results)

        # Check if game is over
        status = self.ai_player.get_status()
        self.game_over = status['game_over']
        self.won = status['won']

        if self.game_over:
            if self.won:
                self.log_messages.append('Victory! You have completed the maze!')
            else:
                self.log_messages.append(
                    'Game over! You have failed to complete the maze.'
                )

    def run(self):
        """Run the main game loop."""
        # Hide cursor
        curses.curs_set(0)

        # Set nodelay mode for non-blocking input
        self.stdscr.nodelay(True)

        # Main game loop
        last_auto_move_time = time.time()

        while True:
            # Clear screen
            self.stdscr.clear()

            # Draw interface elements
            self.draw_menu()
            self.draw_maze()
            self.draw_status()
            self.draw_log()

            # Refresh screen
            self.stdscr.refresh()

            # Auto mode logic
            if self.auto_mode and not self.game_over:
                current_time = time.time()
                if current_time - last_auto_move_time >= self.auto_delay:
                    self.advance_game()
                    last_auto_move_time = current_time

            # Handle input
            try:
                key = self.stdscr.getch()

                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('n') or key == ord('N'):
                    self.new_game()
                elif key == ord('a') or key == ord('A'):
                    self.auto_mode = not self.auto_mode
                    self.log_messages.append(
                        f'Auto mode {"enabled" if self.auto_mode else "disabled"}'
                    )
                elif key == ord('s') or key == ord('S'):
                    self.solution_visible = not self.solution_visible
                    self.log_messages.append(
                        f'Solution path {"shown" if self.solution_visible else "hidden"}'
                    )
                elif key == ord('e') or key == ord('E'):
                    self.execute_solution()

            except curses.error:
                pass

            # Small delay to prevent high CPU usage
            time.sleep(0.05)


def main():
    """Main function to run the advanced terminal interface."""
    # Initialize curses
    curses.wrapper(lambda stdscr: AdvancedTerminalInterface(stdscr).run())


if __name__ == '__main__':
    main()
