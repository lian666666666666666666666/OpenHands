#!/usr/bin/env python3
import curses
import time

from enhanced_maze_generator import EnhancedCellType, EnhancedMazeGenerator
from optimized_ai_player import OptimizedAIPlayer


class QuestTerminalInterface:
    """Enhanced terminal interface with quest system and improved visualization."""

    def __init__(self, stdscr):
        """Initialize the quest terminal interface."""
        self.stdscr = stdscr
        self.height, self.width = stdscr.getmaxyx()

        # Initialize colors
        self._init_colors()

        # Initialize maze and player
        self.maze_generator = EnhancedMazeGenerator(
            21, 21, complexity=0.8, density=0.7, difficulty='medium'
        )
        self.maze = self.maze_generator.generate()
        self.ai_player = OptimizedAIPlayer(self.maze)

        # Game state
        self.game_over = False
        self.won = False
        self.log_messages = ['Welcome to the Quest Maze Adventure!']
        self.auto_mode = False
        self.auto_delay = 0.2  # seconds between moves in auto mode
        self.solution_visible = False
        self.show_inventory = False
        self.show_help = False
        self.show_quest = True
        self.difficulty = 'medium'

        # Animation state
        self.animation_frame = 0
        self.animation_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']

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
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Resource Small
        curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_GREEN)  # Resource Large
        curses.init_pair(8, curses.COLOR_RED, curses.COLOR_BLACK)  # Trap Basic
        curses.init_pair(9, curses.COLOR_RED, curses.COLOR_YELLOW)  # Trap Advanced
        curses.init_pair(10, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Puzzle Easy
        curses.init_pair(11, curses.COLOR_CYAN, curses.COLOR_BLUE)  # Puzzle Hard
        curses.init_pair(12, curses.COLOR_RED, curses.COLOR_BLACK)  # Boss Minion
        curses.init_pair(13, curses.COLOR_WHITE, curses.COLOR_RED)  # Boss
        curses.init_pair(14, curses.COLOR_MAGENTA, curses.COLOR_CYAN)  # Teleport
        curses.init_pair(15, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Shop
        curses.init_pair(16, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Checkpoint
        curses.init_pair(17, curses.COLOR_BLACK, curses.COLOR_MAGENTA)  # Secret
        curses.init_pair(18, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Player
        curses.init_pair(19, curses.COLOR_WHITE, curses.COLOR_CYAN)  # Solution path
        curses.init_pair(20, curses.COLOR_YELLOW, curses.COLOR_RED)  # Health critical
        curses.init_pair(21, curses.COLOR_BLACK, curses.COLOR_RED)  # Health low
        curses.init_pair(22, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Health medium
        curses.init_pair(23, curses.COLOR_BLACK, curses.COLOR_GREEN)  # Health high
        curses.init_pair(24, curses.COLOR_WHITE, curses.COLOR_MAGENTA)  # Title
        curses.init_pair(25, curses.COLOR_YELLOW, curses.COLOR_BLUE)  # Quest
        curses.init_pair(26, curses.COLOR_BLACK, curses.COLOR_CYAN)  # Quest complete

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
                    if cell_value == EnhancedCellType.WALL.value:
                        color = curses.color_pair(2)
                        symbol = '██'
                    elif cell_value == EnhancedCellType.PATH.value:
                        color = curses.color_pair(3)
                        symbol = '  '
                    elif cell_value == EnhancedCellType.START.value:
                        color = curses.color_pair(4)
                        symbol = 'S '
                    elif cell_value == EnhancedCellType.END.value:
                        color = curses.color_pair(5)
                        symbol = 'E '
                    elif cell_value == EnhancedCellType.RESOURCE_SMALL.value:
                        color = curses.color_pair(6)
                        symbol = 'r '
                    elif cell_value == EnhancedCellType.RESOURCE_LARGE.value:
                        color = curses.color_pair(7)
                        symbol = 'R '
                    elif cell_value == EnhancedCellType.TRAP_BASIC.value:
                        color = curses.color_pair(8)
                        symbol = 't '
                    elif cell_value == EnhancedCellType.TRAP_ADVANCED.value:
                        color = curses.color_pair(9)
                        symbol = 'T '
                    elif cell_value == EnhancedCellType.PUZZLE_EASY.value:
                        color = curses.color_pair(10)
                        symbol = 'p '
                    elif cell_value == EnhancedCellType.PUZZLE_HARD.value:
                        color = curses.color_pair(11)
                        symbol = 'P '
                    elif cell_value == EnhancedCellType.BOSS_MINION.value:
                        color = curses.color_pair(12)
                        symbol = 'm '
                    elif cell_value == EnhancedCellType.BOSS.value:
                        color = curses.color_pair(13)
                        symbol = 'B '
                    elif cell_value == EnhancedCellType.TELEPORT.value:
                        color = curses.color_pair(14)
                        symbol = '⊕ '
                    elif cell_value == EnhancedCellType.SHOP.value:
                        color = curses.color_pair(15)
                        symbol = '$ '
                    elif cell_value == EnhancedCellType.CHECKPOINT.value:
                        color = curses.color_pair(16)
                        symbol = '⚑ '
                    elif cell_value == EnhancedCellType.SECRET.value:
                        color = curses.color_pair(17)
                        symbol = '? '
                    elif cell_value == 99:  # Player
                        color = curses.color_pair(18)
                        symbol = 'AI'
                    elif cell_value == 100:  # Solution path
                        color = curses.color_pair(19)
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

        # Draw health bar
        health_percent = status['health'] / status['max_health']
        health_bar_width = 20
        health_filled = int(health_percent * health_bar_width)

        try:
            self.stdscr.addstr(
                start_y, 2, 'Health: [', curses.color_pair(1) | curses.A_BOLD
            )

            # Choose color based on health percentage
            if health_percent < 0.25:
                health_color = curses.color_pair(20)  # Critical
            elif health_percent < 0.5:
                health_color = curses.color_pair(21)  # Low
            elif health_percent < 0.75:
                health_color = curses.color_pair(22)  # Medium
            else:
                health_color = curses.color_pair(23)  # High

            # Draw filled part
            for i in range(health_filled):
                self.stdscr.addstr(start_y, 10 + i, ' ', health_color)

            # Draw empty part
            for i in range(health_filled, health_bar_width):
                self.stdscr.addstr(start_y, 10 + i, ' ', curses.color_pair(1))

            self.stdscr.addstr(
                start_y,
                10 + health_bar_width,
                f'] {status["health"]}/{status["max_health"]}',
                curses.color_pair(1) | curses.A_BOLD,
            )
        except curses.error:
            pass

        # Draw stats
        try:
            stats_line = f'Attack: {status["attack"]} | Defense: {status["defense"]} | Gold: {status["gold"]} | Resources: {status["resources_collected"]}'
            self.stdscr.addstr(
                start_y + 1, 2, stats_line, curses.color_pair(1) | curses.A_BOLD
            )
        except curses.error:
            pass

        # Draw achievements
        try:
            achievements_line = f'Puzzles: {status["puzzles_solved"]} | Traps: {status["traps_disarmed"]} | Enemies: {status["enemies_defeated"]} | Boss: {"Defeated" if status["boss_defeated"] else "Alive"}'
            self.stdscr.addstr(start_y + 2, 2, achievements_line, curses.color_pair(1))
        except curses.error:
            pass

        # Draw solution progress if available
        if 'solution_length' in status and status['solution_length'] > 0:
            try:
                progress = f'Solution: {status["solution_progress"]}/{status["solution_length"]} steps'
                self.stdscr.addstr(start_y + 3, 2, progress, curses.color_pair(1))
            except curses.error:
                pass

        # Draw status effects
        if status['status_effects']:
            try:
                effects_line = 'Status Effects: '
                for effect, (duration, strength) in status['status_effects'].items():
                    effects_line += f'{effect}({duration}) '
                self.stdscr.addstr(start_y + 4, 2, effects_line, curses.color_pair(1))
            except curses.error:
                pass

    def draw_quest(self):
        """Draw the current quest information."""
        if not self.show_quest:
            return

        status = self.ai_player.get_status()

        if 'current_quest' not in status:
            return

        # Calculate position
        maze_height, maze_width = self.maze.shape
        start_y = 5
        start_x = maze_width * 2 + 5

        # Draw quest header
        try:
            self.stdscr.addstr(
                start_y, start_x, 'CURRENT QUEST', curses.color_pair(25) | curses.A_BOLD
            )
        except curses.error:
            pass

        # Draw quest details
        try:
            quest_name = status['current_quest'].replace('_', ' ').title()
            self.stdscr.addstr(
                start_y + 1, start_x, quest_name, curses.color_pair(1) | curses.A_BOLD
            )
        except curses.error:
            pass

        try:
            self.stdscr.addstr(
                start_y + 2, start_x, status['quest_description'], curses.color_pair(1)
            )
        except curses.error:
            pass

        # Draw progress bar
        try:
            progress_text = (
                f'Progress: {status["quest_progress"]}/{status["quest_target"]}'
            )
            if status['quest_complete']:
                self.stdscr.addstr(
                    start_y + 3,
                    start_x,
                    'COMPLETED!',
                    curses.color_pair(26) | curses.A_BOLD,
                )
            else:
                self.stdscr.addstr(
                    start_y + 3, start_x, progress_text, curses.color_pair(1)
                )
        except curses.error:
            pass

    def draw_inventory(self):
        """Draw the player's inventory."""
        if not self.show_inventory:
            return

        status = self.ai_player.get_status()
        inventory = status['inventory']
        skills = status['skills']

        # Calculate position
        maze_height, maze_width = self.maze.shape
        start_y = 12 if self.show_quest else 5
        start_x = maze_width * 2 + 5

        # Draw inventory header
        try:
            self.stdscr.addstr(
                start_y, start_x, 'INVENTORY', curses.color_pair(1) | curses.A_BOLD
            )
        except curses.error:
            pass

        # Draw items
        if inventory:
            for i, item in enumerate(inventory):
                try:
                    self.stdscr.addstr(
                        start_y + i + 1,
                        start_x,
                        f'{i + 1}. {item}',
                        curses.color_pair(1),
                    )
                except curses.error:
                    pass
        else:
            try:
                self.stdscr.addstr(
                    start_y + 1, start_x, 'No items', curses.color_pair(1)
                )
            except curses.error:
                pass

        # Draw skills header
        try:
            self.stdscr.addstr(
                start_y + len(inventory) + 2,
                start_x,
                'SKILLS',
                curses.color_pair(1) | curses.A_BOLD,
            )
        except curses.error:
            pass

        # Draw skills
        if skills:
            for i, skill in enumerate(skills):
                try:
                    self.stdscr.addstr(
                        start_y + len(inventory) + i + 3,
                        start_x,
                        f'• {skill}',
                        curses.color_pair(1),
                    )
                except curses.error:
                    pass
        else:
            try:
                self.stdscr.addstr(
                    start_y + len(inventory) + 3,
                    start_x,
                    'No skills',
                    curses.color_pair(1),
                )
            except curses.error:
                pass

    def draw_log(self):
        """Draw the game log messages."""
        maze_height, maze_width = self.maze.shape
        start_y = max(0, (self.height - maze_height) // 2) + maze_height + 6

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

    def draw_help(self):
        """Draw the help screen."""
        if not self.show_help:
            return

        # Calculate position (center of screen)
        help_height = 16
        help_width = 50
        start_y = max(0, (self.height - help_height) // 2)
        start_x = max(0, (self.width - help_width) // 2)

        # Draw help box
        for y in range(help_height):
            for x in range(help_width):
                if y == 0 or y == help_height - 1 or x == 0 or x == help_width - 1:
                    try:
                        self.stdscr.addstr(
                            start_y + y, start_x + x, '█', curses.color_pair(1)
                        )
                    except curses.error:
                        pass
                else:
                    try:
                        self.stdscr.addstr(
                            start_y + y, start_x + x, ' ', curses.color_pair(1)
                        )
                    except curses.error:
                        pass

        # Draw help title
        try:
            self.stdscr.addstr(
                start_y + 1,
                start_x + (help_width - 4) // 2,
                'HELP',
                curses.color_pair(24) | curses.A_BOLD,
            )
        except curses.error:
            pass

        # Draw help content
        help_items = [
            'N - Start a new game',
            'A - Toggle auto mode',
            'S - Show/hide solution path',
            'E - Execute complete solution',
            'I - Show/hide inventory',
            'Q - Show/hide quest panel',
            '1-9 - Use inventory item',
            'D - Change difficulty (easy/medium/hard)',
            'H - Show/hide this help',
            'X - Quit game',
        ]

        for i, item in enumerate(help_items):
            try:
                self.stdscr.addstr(
                    start_y + 3 + i, start_x + 2, item, curses.color_pair(1)
                )
            except curses.error:
                pass

        # Draw close instruction
        try:
            self.stdscr.addstr(
                start_y + help_height - 2,
                start_x + 2,
                'Press any key to close help',
                curses.color_pair(1) | curses.A_BOLD,
            )
        except curses.error:
            pass

    def draw_menu(self):
        """Draw the menu options."""
        try:
            # Draw title with animation
            title = 'QUEST MAZE ADVENTURE'
            anim_char = self.animation_chars[
                self.animation_frame % len(self.animation_chars)
            ]
            self.stdscr.addstr(
                2,
                2,
                f'{anim_char} {title} {anim_char}',
                curses.color_pair(24) | curses.A_BOLD,
            )

            # Draw difficulty
            self.stdscr.addstr(
                3,
                2,
                f'Difficulty: {self.difficulty.upper()}',
                curses.color_pair(1) | curses.A_BOLD,
            )

            self.stdscr.addstr(5, 2, 'Controls:', curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(6, 4, 'N - New Game', curses.color_pair(1))
            self.stdscr.addstr(7, 4, 'A - Toggle Auto Mode', curses.color_pair(1))
            self.stdscr.addstr(
                8, 4, 'S - Show/Hide Solution Path', curses.color_pair(1)
            )
            self.stdscr.addstr(
                9, 4, 'E - Execute Complete Solution', curses.color_pair(1)
            )
            self.stdscr.addstr(10, 4, 'I - Show/Hide Inventory', curses.color_pair(1))
            self.stdscr.addstr(11, 4, 'Q - Show/Hide Quest Panel', curses.color_pair(1))
            self.stdscr.addstr(12, 4, 'H - Help', curses.color_pair(1))
            self.stdscr.addstr(13, 4, 'X - Quit', curses.color_pair(1))

            # Show auto mode status
            auto_status = 'ON' if self.auto_mode else 'OFF'
            self.stdscr.addstr(
                15,
                4,
                f'Auto Mode: {auto_status}',
                curses.color_pair(1) | (curses.A_BOLD if self.auto_mode else 0),
            )

            # Show solution visibility status
            solution_status = 'VISIBLE' if self.solution_visible else 'HIDDEN'
            self.stdscr.addstr(
                16,
                4,
                f'Solution Path: {solution_status}',
                curses.color_pair(1) | (curses.A_BOLD if self.solution_visible else 0),
            )
        except curses.error:
            pass

    def draw_legend(self):
        """Draw the maze legend."""
        maze_height, maze_width = self.maze.shape
        start_y = max(0, (self.height - maze_height) // 2)
        start_x = maze_width * 2 + 5

        try:
            self.stdscr.addstr(
                start_y, start_x, 'LEGEND', curses.color_pair(1) | curses.A_BOLD
            )

            legend_items = [
                (curses.color_pair(4), 'S ', 'Start'),
                (curses.color_pair(5), 'E ', 'End'),
                (curses.color_pair(6), 'r ', 'Small Resource'),
                (curses.color_pair(7), 'R ', 'Large Resource'),
                (curses.color_pair(8), 't ', 'Basic Trap'),
                (curses.color_pair(9), 'T ', 'Advanced Trap'),
                (curses.color_pair(10), 'p ', 'Easy Puzzle'),
                (curses.color_pair(11), 'P ', 'Hard Puzzle'),
                (curses.color_pair(12), 'm ', 'Boss Minion'),
                (curses.color_pair(13), 'B ', 'Boss'),
                (curses.color_pair(14), '⊕ ', 'Teleport'),
                (curses.color_pair(15), '$ ', 'Shop'),
                (curses.color_pair(16), '⚑ ', 'Checkpoint'),
                (curses.color_pair(17), '? ', 'Secret'),
                (curses.color_pair(18), 'AI', 'Player'),
                (curses.color_pair(19), '· ', 'Solution Path'),
            ]

            for i, (color, symbol, desc) in enumerate(legend_items):
                self.stdscr.addstr(start_y + i + 1, start_x, symbol, color)
                self.stdscr.addstr(
                    start_y + i + 1, start_x + 3, desc, curses.color_pair(1)
                )
        except curses.error:
            pass

    def new_game(self):
        """Start a new game."""
        self.maze = self.maze_generator.generate()
        self.ai_player = OptimizedAIPlayer(self.maze)
        self.game_over = False
        self.won = False
        self.log_messages = ['New game started!']
        self.auto_mode = False
        self.solution_visible = False
        self.show_inventory = False

    def change_difficulty(self):
        """Change the game difficulty."""
        if self.difficulty == 'easy':
            self.difficulty = 'medium'
        elif self.difficulty == 'medium':
            self.difficulty = 'hard'
        else:
            self.difficulty = 'easy'

        self.maze_generator = EnhancedMazeGenerator(
            21, 21, complexity=0.8, density=0.7, difficulty=self.difficulty
        )
        self.log_messages.append(f'Difficulty changed to {self.difficulty}')

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

    def use_inventory_item(self, index):
        """Use an item from the inventory."""
        status = self.ai_player.get_status()
        inventory = status['inventory']

        if 0 <= index < len(inventory):
            result = self.ai_player.stats.use_item(index)
            self.log_messages.append(result)

    def run(self):
        """Run the main game loop."""
        # Hide cursor
        curses.curs_set(0)

        # Set nodelay mode for non-blocking input
        self.stdscr.nodelay(True)

        # Main game loop
        last_auto_move_time = time.time()
        last_animation_time = time.time()

        while True:
            # Clear screen
            self.stdscr.clear()

            # Update animation frame
            current_time = time.time()
            if (
                current_time - last_animation_time >= 0.1
            ):  # Update animation every 100ms
                self.animation_frame += 1
                last_animation_time = current_time

            # Draw interface elements
            self.draw_menu()
            self.draw_maze()
            self.draw_status()
            self.draw_log()
            self.draw_legend()
            self.draw_quest()
            self.draw_inventory()
            self.draw_help()

            # Refresh screen
            self.stdscr.refresh()

            # Auto mode logic
            if self.auto_mode and not self.game_over and not self.show_help:
                current_time = time.time()
                if current_time - last_auto_move_time >= self.auto_delay:
                    self.advance_game()
                    last_auto_move_time = current_time

            # Handle input
            try:
                key = self.stdscr.getch()

                if self.show_help:
                    # Any key closes help
                    if key != -1:
                        self.show_help = False
                else:
                    if key == ord('x') or key == ord('X'):
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
                    elif key == ord('i') or key == ord('I'):
                        self.show_inventory = not self.show_inventory
                    elif key == ord('q') or key == ord('Q'):
                        self.show_quest = not self.show_quest
                    elif key == ord('h') or key == ord('H'):
                        self.show_help = True
                    elif key == ord('d') or key == ord('D'):
                        self.change_difficulty()
                    elif ord('1') <= key <= ord('9'):
                        # Use inventory item
                        self.use_inventory_item(key - ord('1'))

            except curses.error:
                pass

            # Small delay to prevent high CPU usage
            time.sleep(0.05)


def main():
    """Main function to run the quest terminal interface."""
    # Initialize curses
    curses.wrapper(lambda stdscr: QuestTerminalInterface(stdscr).run())


if __name__ == '__main__':
    main()
