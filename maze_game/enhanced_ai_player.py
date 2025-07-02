import heapq
import random

import numpy as np
from enhanced_maze_generator import EnhancedCellType


class PlayerStats:
    """Player statistics and inventory."""

    def __init__(self):
        """Initialize player stats."""
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 5
        self.resources = 0
        self.gold = 0
        self.keys = 0
        self.puzzles_solved = 0
        self.traps_disarmed = 0
        self.enemies_defeated = 0
        self.boss_defeated = False
        self.checkpoints_reached = 0
        self.secrets_found = 0
        self.inventory = []
        self.skills = []
        self.status_effects = {}  # Effect name -> (turns_remaining, effect_strength)

    def apply_status_effect(self, effect, duration, strength):
        """Apply a status effect to the player."""
        self.status_effects[effect] = (duration, strength)

    def update_status_effects(self):
        """Update status effects at the end of a turn."""
        effects_to_remove = []

        for effect, (duration, strength) in self.status_effects.items():
            # Reduce duration
            new_duration = duration - 1

            if new_duration <= 0:
                effects_to_remove.append(effect)
            else:
                self.status_effects[effect] = (new_duration, strength)

                # Apply effect
                if effect == 'poison':
                    self.health -= strength
                elif effect == 'regeneration':
                    self.health = min(self.max_health, self.health + strength)
                elif effect == 'strength':
                    pass  # Passive effect, applied when calculating attack
                elif effect == 'weakness':
                    pass  # Passive effect, applied when calculating attack

        # Remove expired effects
        for effect in effects_to_remove:
            del self.status_effects[effect]

    def get_effective_attack(self):
        """Get the effective attack value after status effects."""
        attack = self.attack

        # Apply status effects
        if 'strength' in self.status_effects:
            _, strength = self.status_effects['strength']
            attack += strength

        if 'weakness' in self.status_effects:
            _, strength = self.status_effects['weakness']
            attack -= strength

        return max(1, attack)  # Minimum attack of 1

    def get_effective_defense(self):
        """Get the effective defense value after status effects."""
        defense = self.defense

        # Apply status effects
        if 'protection' in self.status_effects:
            _, strength = self.status_effects['protection']
            defense += strength

        if 'vulnerability' in self.status_effects:
            _, strength = self.status_effects['vulnerability']
            defense -= strength

        return max(0, defense)  # Minimum defense of 0

    def has_skill(self, skill):
        """Check if the player has a specific skill."""
        return skill in self.skills

    def add_skill(self, skill):
        """Add a skill to the player."""
        if skill not in self.skills:
            self.skills.append(skill)

    def add_item(self, item):
        """Add an item to the inventory."""
        self.inventory.append(item)

    def use_item(self, item_index):
        """Use an item from the inventory."""
        if 0 <= item_index < len(self.inventory):
            item = self.inventory.pop(item_index)

            # Apply item effects
            if item == 'health_potion':
                self.health = min(self.max_health, self.health + 30)
                return f'Used health potion. Health restored to {self.health}.'
            elif item == 'strength_potion':
                self.apply_status_effect('strength', 5, 5)
                return 'Used strength potion. Attack increased for 5 turns.'
            elif item == 'defense_potion':
                self.apply_status_effect('protection', 5, 5)
                return 'Used defense potion. Defense increased for 5 turns.'
            elif item == 'antidote':
                if 'poison' in self.status_effects:
                    del self.status_effects['poison']
                return 'Used antidote. Poison cured.'
            else:
                return f'Used {item}.'
        else:
            return 'Invalid item index.'


class EnhancedAIPlayer:
    """Enhanced AI player with advanced pathfinding and decision-making."""

    def __init__(self, maze, start_pos=None):
        """
        Initialize an enhanced AI player for navigating the maze.

        Args:
            maze: 2D numpy array representing the maze
            start_pos: Starting position (y, x) or None to find automatically
        """
        self.maze = maze
        self.height, self.width = maze.shape

        # Find start position if not provided
        if start_pos is None:
            start_positions = np.where(maze == EnhancedCellType.START.value)
            if len(start_positions[0]) > 0:
                self.position = (start_positions[0][0], start_positions[1][0])
            else:
                # Default to top-left corner if no start position found
                self.position = (1, 1)
        else:
            self.position = start_pos

        # Initialize player stats
        self.stats = PlayerStats()

        # Game state
        self.game_over = False
        self.won = False
        self.turn_count = 0
        self.visited = set([self.position])
        self.path_history = [self.position]
        self.action_log = []

        # Knowledge of the maze
        self.known_maze = np.full_like(maze, -1)  # -1 represents unknown
        self.update_known_maze()

        # Teleport points (for teleportation feature)
        self.teleport_points = {}  # (y, x) -> (target_y, target_x)
        self._discover_teleport_points()

        # Complete solution path
        self.complete_solution = None
        self.solution_index = 0

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

    def _discover_teleport_points(self):
        """Discover teleport points in the maze."""
        teleport_positions = []

        # Find all teleport points
        for y in range(self.height):
            for x in range(self.width):
                if self.maze[y, x] == EnhancedCellType.TELEPORT.value:
                    teleport_positions.append((y, x))

        # Create teleport pairs
        if len(teleport_positions) >= 2:
            # Shuffle to create random pairs
            random.shuffle(teleport_positions)

            # Create pairs
            for i in range(0, len(teleport_positions) - 1, 2):
                self.teleport_points[teleport_positions[i]] = teleport_positions[i + 1]
                self.teleport_points[teleport_positions[i + 1]] = teleport_positions[i]

            # If odd number of teleport points, last one teleports to a random other point
            if len(teleport_positions) % 2 == 1:
                last_point = teleport_positions[-1]
                target_point = random.choice(teleport_positions[:-1])
                self.teleport_points[last_point] = target_point

    def get_valid_moves(self):
        """Get list of valid moves from current position."""
        y, x = self.position
        valid_moves = []

        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ny, nx = y + dy, x + dx
            if (
                0 <= ny < self.height
                and 0 <= nx < self.width
                and self.maze[ny, nx] != EnhancedCellType.WALL.value
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

            # Update status effects
            self.stats.update_status_effects()

            # Increment turn count
            self.turn_count += 1

            # Check win/lose conditions
            self._check_game_state()

            return result
        else:
            return 'Invalid move'

    def _handle_cell_effect(self, cell_type):
        """Handle the effect of landing on a specific cell type."""
        # Small resource (health potion, etc.)
        if cell_type == EnhancedCellType.RESOURCE_SMALL.value:
            self.stats.resources += 1

            # 70% chance of health potion, 30% chance of gold
            if random.random() < 0.7:
                health_gain = random.randint(10, 20)
                self.stats.health = min(
                    self.stats.max_health, self.stats.health + health_gain
                )
                return f'Found a small health potion! Restored {health_gain} health.'
            else:
                gold_gain = random.randint(5, 15)
                self.stats.gold += gold_gain
                return f'Found {gold_gain} gold coins!'

        # Large resource (weapon, armor, etc.)
        elif cell_type == EnhancedCellType.RESOURCE_LARGE.value:
            self.stats.resources += 2

            # 40% chance of weapon, 40% chance of armor, 20% chance of special item
            roll = random.random()
            if roll < 0.4:
                attack_gain = random.randint(2, 5)
                self.stats.attack += attack_gain
                return f'Found a better weapon! Attack increased by {attack_gain}.'
            elif roll < 0.8:
                defense_gain = random.randint(1, 3)
                self.stats.defense += defense_gain
                return f'Found better armor! Defense increased by {defense_gain}.'
            else:
                # Special item
                special_items = [
                    'health_potion',
                    'strength_potion',
                    'defense_potion',
                    'antidote',
                ]
                item = random.choice(special_items)
                self.stats.add_item(item)
                return f'Found a special item: {item}!'

        # Basic trap (spikes, etc.)
        elif cell_type == EnhancedCellType.TRAP_BASIC.value:
            # Check if player has trap detection skill
            if self.stats.has_skill('trap_detection'):
                # 80% chance to detect and avoid
                if random.random() < 0.8:
                    self.stats.traps_disarmed += 1
                    return 'Detected and avoided a basic trap!'

            # Take damage
            damage = random.randint(5, 15)
            damage -= self.stats.get_effective_defense() // 2  # Defense reduces damage
            damage = max(1, damage)  # Minimum damage of 1
            self.stats.health -= damage

            return f'Triggered a basic trap! Lost {damage} health.'

        # Advanced trap (poison gas, etc.)
        elif cell_type == EnhancedCellType.TRAP_ADVANCED.value:
            # Check if player has advanced trap detection skill
            if self.stats.has_skill('advanced_trap_detection'):
                # 60% chance to detect and avoid
                if random.random() < 0.6:
                    self.stats.traps_disarmed += 1
                    return 'Detected and avoided an advanced trap!'

            # Take damage and apply status effect
            damage = random.randint(10, 20)
            damage -= self.stats.get_effective_defense() // 2  # Defense reduces damage
            damage = max(1, damage)  # Minimum damage of 1
            self.stats.health -= damage

            # 50% chance of poison
            if random.random() < 0.5:
                self.stats.apply_status_effect('poison', 3, 5)
                return f'Triggered an advanced trap! Lost {damage} health and got poisoned!'
            else:
                self.stats.apply_status_effect('weakness', 3, 3)
                return f'Triggered an advanced trap! Lost {damage} health and got weakened!'

        # Easy puzzle
        elif cell_type == EnhancedCellType.PUZZLE_EASY.value:
            # Check if player has puzzle solving skill
            if self.stats.has_skill('puzzle_solving'):
                # 90% chance to solve
                success_chance = 0.9
            else:
                # 70% chance to solve
                success_chance = 0.7

            if random.random() < success_chance:
                self.stats.puzzles_solved += 1

                # Reward for solving
                reward_type = random.choice(['health', 'gold', 'key', 'skill'])

                if reward_type == 'health':
                    health_gain = random.randint(10, 20)
                    self.stats.health = min(
                        self.stats.max_health, self.stats.health + health_gain
                    )
                    return f'Solved an easy puzzle! Restored {health_gain} health.'
                elif reward_type == 'gold':
                    gold_gain = random.randint(10, 20)
                    self.stats.gold += gold_gain
                    return f'Solved an easy puzzle! Found {gold_gain} gold coins.'
                elif reward_type == 'key':
                    self.stats.keys += 1
                    return 'Solved an easy puzzle! Found a key.'
                else:  # skill
                    if not self.stats.has_skill('trap_detection'):
                        self.stats.add_skill('trap_detection')
                        return 'Solved an easy puzzle! Learned trap detection skill.'
                    else:
                        self.stats.gold += 15
                        return 'Solved an easy puzzle! Found 15 gold coins.'
            else:
                # Penalty for failing
                damage = random.randint(5, 10)
                self.stats.health -= damage
                return f'Failed to solve the easy puzzle. Lost {damage} health.'

        # Hard puzzle
        elif cell_type == EnhancedCellType.PUZZLE_HARD.value:
            # Check if player has advanced puzzle solving skill
            if self.stats.has_skill('advanced_puzzle_solving'):
                # 80% chance to solve
                success_chance = 0.8
            elif self.stats.has_skill('puzzle_solving'):
                # 60% chance to solve
                success_chance = 0.6
            else:
                # 40% chance to solve
                success_chance = 0.4

            if random.random() < success_chance:
                self.stats.puzzles_solved += 1

                # Reward for solving
                reward_type = random.choice(['health', 'attack', 'defense', 'skill'])

                if reward_type == 'health':
                    health_gain = random.randint(20, 30)
                    self.stats.health = min(
                        self.stats.max_health, self.stats.health + health_gain
                    )
                    return f'Solved a hard puzzle! Restored {health_gain} health.'
                elif reward_type == 'attack':
                    attack_gain = random.randint(3, 6)
                    self.stats.attack += attack_gain
                    return f'Solved a hard puzzle! Attack increased by {attack_gain}.'
                elif reward_type == 'defense':
                    defense_gain = random.randint(2, 4)
                    self.stats.defense += defense_gain
                    return f'Solved a hard puzzle! Defense increased by {defense_gain}.'
                else:  # skill
                    if not self.stats.has_skill('advanced_puzzle_solving'):
                        self.stats.add_skill('advanced_puzzle_solving')
                        return 'Solved a hard puzzle! Learned advanced puzzle solving skill.'
                    elif not self.stats.has_skill('advanced_trap_detection'):
                        self.stats.add_skill('advanced_trap_detection')
                        return 'Solved a hard puzzle! Learned advanced trap detection skill.'
                    else:
                        self.stats.gold += 30
                        return 'Solved a hard puzzle! Found 30 gold coins.'
            else:
                # Penalty for failing
                damage = random.randint(15, 25)
                self.stats.health -= damage
                return f'Failed to solve the hard puzzle. Lost {damage} health.'

        # Boss minion
        elif cell_type == EnhancedCellType.BOSS_MINION.value:
            # Battle with minion
            minion_health = random.randint(20, 40)
            minion_attack = random.randint(5, 15)

            battle_log = ['Encountered a boss minion!']

            # Battle until player or minion is defeated
            while minion_health > 0 and self.stats.health > 0:
                # Player attacks first
                player_damage = max(
                    1, self.stats.get_effective_attack() - random.randint(0, 5)
                )
                minion_health -= player_damage
                battle_log.append(f'You hit the minion for {player_damage} damage.')

                if minion_health <= 0:
                    break

                # Minion attacks
                minion_damage = max(
                    1, minion_attack - self.stats.get_effective_defense()
                )
                self.stats.health -= minion_damage
                battle_log.append(f'The minion hits you for {minion_damage} damage.')

            if minion_health <= 0:
                self.stats.enemies_defeated += 1

                # Reward for defeating
                reward_type = random.choice(['health', 'gold', 'item'])

                if reward_type == 'health':
                    health_gain = random.randint(10, 20)
                    self.stats.health = min(
                        self.stats.max_health, self.stats.health + health_gain
                    )
                    battle_log.append(
                        f'Defeated the minion! Found a health potion and restored {health_gain} health.'
                    )
                elif reward_type == 'gold':
                    gold_gain = random.randint(15, 25)
                    self.stats.gold += gold_gain
                    battle_log.append(
                        f'Defeated the minion! Found {gold_gain} gold coins.'
                    )
                else:  # item
                    special_items = [
                        'health_potion',
                        'strength_potion',
                        'defense_potion',
                    ]
                    item = random.choice(special_items)
                    self.stats.add_item(item)
                    battle_log.append(f'Defeated the minion! Found a {item}.')
            else:
                battle_log.append('You were defeated by the minion.')

            return '\n'.join(battle_log)

        # Main boss
        elif cell_type == EnhancedCellType.BOSS.value:
            # Check if already defeated
            if self.stats.boss_defeated:
                return 'The defeated boss lies motionless.'

            # Battle with boss
            boss_health = random.randint(80, 120)
            boss_attack = random.randint(15, 25)

            battle_log = ['Encountered the main boss!']

            # Battle until player or boss is defeated
            while boss_health > 0 and self.stats.health > 0:
                # Player attacks first
                player_damage = max(
                    1, self.stats.get_effective_attack() - random.randint(0, 10)
                )
                boss_health -= player_damage
                battle_log.append(f'You hit the boss for {player_damage} damage.')

                if boss_health <= 0:
                    break

                # Boss attacks
                boss_damage = max(1, boss_attack - self.stats.get_effective_defense())
                self.stats.health -= boss_damage
                battle_log.append(f'The boss hits you for {boss_damage} damage.')

                # Boss special attack (every 3rd turn)
                if len(battle_log) % 3 == 0:
                    special_attack = random.choice(['poison', 'weaken', 'heavy'])

                    if special_attack == 'poison':
                        self.stats.apply_status_effect('poison', 3, 8)
                        battle_log.append('The boss uses a poison attack!')
                    elif special_attack == 'weaken':
                        self.stats.apply_status_effect('weakness', 2, 5)
                        battle_log.append('The boss uses a weakening attack!')
                    else:  # heavy
                        heavy_damage = random.randint(15, 25)
                        self.stats.health -= heavy_damage
                        battle_log.append(
                            f'The boss uses a heavy attack for {heavy_damage} damage!'
                        )

            if boss_health <= 0:
                self.stats.boss_defeated = True
                self.stats.enemies_defeated += 1

                # Major reward for defeating boss
                self.stats.attack += 10
                self.stats.defense += 5
                self.stats.max_health += 20
                self.stats.health = self.stats.max_health

                battle_log.append(
                    'You defeated the boss! Your powers have increased significantly!'
                )
            else:
                battle_log.append('You were defeated by the boss.')

            return '\n'.join(battle_log)

        # Teleport point
        elif cell_type == EnhancedCellType.TELEPORT.value:
            if self.position in self.teleport_points:
                target = self.teleport_points[self.position]
                self.position = target
                self.path_history.append(target)
                self.update_known_maze()
                return f'Teleported to position {target}!'
            else:
                return 'This teleport point seems inactive.'

        # Shop
        elif cell_type == EnhancedCellType.SHOP.value:
            # Shop options
            options = [
                ('Health Potion (20 gold)', 20, 'health_potion'),
                ('Strength Potion (30 gold)', 30, 'strength_potion'),
                ('Defense Potion (30 gold)', 30, 'defense_potion'),
                ('Antidote (15 gold)', 15, 'antidote'),
                ('Weapon Upgrade (50 gold)', 50, 'weapon'),
                ('Armor Upgrade (40 gold)', 40, 'armor'),
                ('Max Health Increase (60 gold)', 60, 'max_health'),
            ]

            # Filter options based on available gold
            affordable = [opt for opt in options if opt[1] <= self.stats.gold]

            if not affordable:
                return "Visited the shop, but couldn't afford anything."

            # Choose a random affordable item
            choice = random.choice(affordable)
            name, cost, item_type = choice

            # Purchase the item
            self.stats.gold -= cost

            if item_type == 'health_potion':
                self.stats.add_item('health_potion')
                return f'Purchased a health potion for {cost} gold.'
            elif item_type == 'strength_potion':
                self.stats.add_item('strength_potion')
                return f'Purchased a strength potion for {cost} gold.'
            elif item_type == 'defense_potion':
                self.stats.add_item('defense_potion')
                return f'Purchased a defense potion for {cost} gold.'
            elif item_type == 'antidote':
                self.stats.add_item('antidote')
                return f'Purchased an antidote for {cost} gold.'
            elif item_type == 'weapon':
                attack_gain = random.randint(3, 7)
                self.stats.attack += attack_gain
                return f'Purchased a weapon upgrade for {cost} gold. Attack increased by {attack_gain}.'
            elif item_type == 'armor':
                defense_gain = random.randint(2, 5)
                self.stats.defense += defense_gain
                return f'Purchased an armor upgrade for {cost} gold. Defense increased by {defense_gain}.'
            elif item_type == 'max_health':
                health_gain = random.randint(15, 25)
                self.stats.max_health += health_gain
                self.stats.health += health_gain
                return f'Purchased a max health increase for {cost} gold. Max health increased by {health_gain}.'

        # Checkpoint
        elif cell_type == EnhancedCellType.CHECKPOINT.value:
            self.stats.checkpoints_reached += 1

            # Restore some health
            health_gain = random.randint(15, 30)
            self.stats.health = min(
                self.stats.max_health, self.stats.health + health_gain
            )

            return f'Reached a checkpoint! Restored {health_gain} health.'

        # Secret
        elif cell_type == EnhancedCellType.SECRET.value:
            self.stats.secrets_found += 1

            # Major reward for finding a secret
            reward_type = random.choice(['gold', 'item', 'stat', 'skill'])

            if reward_type == 'gold':
                gold_gain = random.randint(30, 50)
                self.stats.gold += gold_gain
                return f'Found a secret treasure! Gained {gold_gain} gold.'
            elif reward_type == 'item':
                special_items = [
                    'health_potion',
                    'strength_potion',
                    'defense_potion',
                    'antidote',
                ]
                for _ in range(2):  # Add 2 random items
                    self.stats.add_item(random.choice(special_items))
                return 'Found a secret stash of potions! Added 2 potions to inventory.'
            elif reward_type == 'stat':
                self.stats.attack += 3
                self.stats.defense += 2
                self.stats.max_health += 10
                self.stats.health = min(self.stats.max_health, self.stats.health + 10)
                return 'Found a secret shrine! All stats increased.'
            else:  # skill
                available_skills = []
                if not self.stats.has_skill('trap_detection'):
                    available_skills.append('trap_detection')
                if not self.stats.has_skill('advanced_trap_detection'):
                    available_skills.append('advanced_trap_detection')
                if not self.stats.has_skill('puzzle_solving'):
                    available_skills.append('puzzle_solving')
                if not self.stats.has_skill('advanced_puzzle_solving'):
                    available_skills.append('advanced_puzzle_solving')

                if available_skills:
                    skill = random.choice(available_skills)
                    self.stats.add_skill(skill)
                    return f'Found a secret scroll! Learned the {skill} skill.'
                else:
                    self.stats.gold += 40
                    return 'Found a secret treasure! Gained 40 gold.'

        # Start point
        elif cell_type == EnhancedCellType.START.value:
            return 'Back at the starting point.'

        # End point
        elif cell_type == EnhancedCellType.END.value:
            if self.stats.boss_defeated:
                self.won = True
                return 'Reached the end! Victory!'
            else:
                return 'Reached the end, but must defeat the boss first!'

        # Path
        else:  # PATH
            return 'Moved to an empty path.'

    def _check_game_state(self):
        """Check if the game is over (win or lose)."""
        if self.stats.health <= 0:
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
                    and self.maze[ny, nx] != EnhancedCellType.WALL.value
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
        original_health = self.stats.health
        original_resources = self.stats.resources
        original_puzzles = self.stats.puzzles_solved
        original_boss = self.stats.boss_defeated

        # Plan the complete path
        complete_path = []
        action_sequence = []

        # Step 1: Collect resources and solve puzzles
        # First, find all resources and puzzles
        resource_positions = []
        puzzle_positions = []
        shop_positions = []

        for y in range(self.height):
            for x in range(self.width):
                cell = self.maze[y, x]
                if cell in [
                    EnhancedCellType.RESOURCE_SMALL.value,
                    EnhancedCellType.RESOURCE_LARGE.value,
                ]:
                    resource_positions.append((y, x))
                elif cell in [
                    EnhancedCellType.PUZZLE_EASY.value,
                    EnhancedCellType.PUZZLE_HARD.value,
                ]:
                    puzzle_positions.append((y, x))
                elif cell == EnhancedCellType.SHOP.value:
                    shop_positions.append((y, x))

        # Sort by distance from current position
        resource_positions.sort(
            key=lambda pos: abs(pos[0] - self.position[0])
            + abs(pos[1] - self.position[1])
        )
        puzzle_positions.sort(
            key=lambda pos: abs(pos[0] - self.position[0])
            + abs(pos[1] - self.position[1])
        )

        # Collect resources (prioritize closest ones)
        resources_to_collect = min(3, len(resource_positions))
        for i in range(resources_to_collect):
            target = resource_positions[i]
            path = self.find_path_to_target(self.maze[target[0], target[1]])
            if path:
                complete_path.extend(path)
                action_sequence.append(f'Collecting resource at {target}')
                # Update position for next path calculation
                self.position = path[-1]
                self.stats.resources += 1

        # Solve puzzles (prioritize closest ones)
        puzzles_to_solve = min(2, len(puzzle_positions))
        for i in range(puzzles_to_solve):
            target = puzzle_positions[i]
            path = self.find_path_to_target(self.maze[target[0], target[1]])
            if path:
                complete_path.extend(path)
                action_sequence.append(f'Solving puzzle at {target}')
                # Update position for next path calculation
                self.position = path[-1]
                self.stats.puzzles_solved += 1

        # Visit shop if available
        if (
            shop_positions and self.stats.resources > 0
        ):  # Assume resources convert to gold
            target = shop_positions[0]
            path = self.find_path_to_target(EnhancedCellType.SHOP.value)
            if path:
                complete_path.extend(path)
                action_sequence.append('Visiting shop')
                # Update position for next path calculation
                self.position = path[-1]

        # Step 3: Defeat the boss
        boss_path = self.find_path_to_target(EnhancedCellType.BOSS.value)
        if boss_path:
            complete_path.extend(boss_path)
            action_sequence.append('Defeating boss')
            self.position = boss_path[-1]
            self.stats.boss_defeated = True

        # Step 4: Head to the exit
        end_path = self.find_path_to_target(EnhancedCellType.END.value)
        if end_path:
            complete_path.extend(end_path)
            action_sequence.append('Reaching the exit')
            self.position = end_path[-1]

        # Restore original state
        self.position = original_position
        self.stats.health = original_health
        self.stats.resources = original_resources
        self.stats.puzzles_solved = original_puzzles
        self.stats.boss_defeated = original_boss

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

        # Check if we need healing
        if self.stats.health < self.stats.max_health * 0.3:  # Less than 30% health
            # Check if we have a health potion
            for i, item in enumerate(self.stats.inventory):
                if item == 'health_potion':
                    return self.stats.use_item(i)

            # Look for resources or checkpoints
            resource_path = self.find_path_to_target(
                EnhancedCellType.RESOURCE_SMALL.value
            )
            checkpoint_path = self.find_path_to_target(
                EnhancedCellType.CHECKPOINT.value
            )

            if resource_path and (
                not checkpoint_path or len(resource_path) <= len(checkpoint_path)
            ):
                if len(resource_path) > 0:
                    return self.move_to(resource_path[0])
            elif checkpoint_path:
                if len(checkpoint_path) > 0:
                    return self.move_to(checkpoint_path[0])

        # Priority 1: If boss not defeated and we have resources, go for boss
        if not self.stats.boss_defeated and self.stats.resources > 0:
            # If health is low, try to heal first
            if self.stats.health < self.stats.max_health * 0.7:  # Less than 70% health
                # Check if we have a health potion
                for i, item in enumerate(self.stats.inventory):
                    if item == 'health_potion':
                        return self.stats.use_item(i)

                # Look for resources or checkpoints
                resource_path = self.find_path_to_target(
                    EnhancedCellType.RESOURCE_SMALL.value
                )
                checkpoint_path = self.find_path_to_target(
                    EnhancedCellType.CHECKPOINT.value
                )

                if resource_path and (
                    not checkpoint_path or len(resource_path) <= len(checkpoint_path)
                ):
                    if len(resource_path) > 0:
                        return self.move_to(resource_path[0])
                elif checkpoint_path:
                    if len(checkpoint_path) > 0:
                        return self.move_to(checkpoint_path[0])

            # If we have strength potion, use it before boss
            for i, item in enumerate(self.stats.inventory):
                if item == 'strength_potion':
                    return self.stats.use_item(i)

            # Go for boss
            path = self.find_path_to_target(EnhancedCellType.BOSS.value)
            if path and len(path) > 0:
                return self.move_to(path[0])

        # Priority 2: If boss defeated, go for end
        if self.stats.boss_defeated:
            path = self.find_path_to_target(EnhancedCellType.END.value)
            if path and len(path) > 0:
                return self.move_to(path[0])

        # Priority 3: Collect resources
        resource_path = self.find_path_to_target(EnhancedCellType.RESOURCE_SMALL.value)
        large_resource_path = self.find_path_to_target(
            EnhancedCellType.RESOURCE_LARGE.value
        )

        if large_resource_path and (
            not resource_path or len(large_resource_path) <= len(resource_path) * 1.5
        ):
            if len(large_resource_path) > 0:
                return self.move_to(large_resource_path[0])
        elif resource_path:
            if len(resource_path) > 0:
                return self.move_to(resource_path[0])

        # Priority 4: Solve puzzles
        easy_puzzle_path = self.find_path_to_target(EnhancedCellType.PUZZLE_EASY.value)
        hard_puzzle_path = self.find_path_to_target(EnhancedCellType.PUZZLE_HARD.value)

        if easy_puzzle_path and (
            not hard_puzzle_path or len(easy_puzzle_path) <= len(hard_puzzle_path)
        ):
            if len(easy_puzzle_path) > 0:
                return self.move_to(easy_puzzle_path[0])
        elif hard_puzzle_path:
            if len(hard_puzzle_path) > 0:
                return self.move_to(hard_puzzle_path[0])

        # Priority 5: Visit shop if we have gold
        if self.stats.gold >= 20:  # Minimum cost of cheapest item
            shop_path = self.find_path_to_target(EnhancedCellType.SHOP.value)
            if shop_path and len(shop_path) > 0:
                return self.move_to(shop_path[0])

        # Priority 6: Find secrets
        secret_path = self.find_path_to_target(EnhancedCellType.SECRET.value)
        if secret_path and len(secret_path) > 0:
            return self.move_to(secret_path[0])

        # Priority 7: Go for boss even without resources
        if not self.stats.boss_defeated:
            path = self.find_path_to_target(EnhancedCellType.BOSS.value)
            if path and len(path) > 0:
                return self.move_to(path[0])

        # Priority 8: Explore unvisited paths
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
            'health': self.stats.health,
            'max_health': self.stats.max_health,
            'attack': self.stats.attack,
            'defense': self.stats.defense,
            'resources_collected': self.stats.resources,
            'gold': self.stats.gold,
            'puzzles_solved': self.stats.puzzles_solved,
            'traps_disarmed': self.stats.traps_disarmed,
            'enemies_defeated': self.stats.enemies_defeated,
            'boss_defeated': self.stats.boss_defeated,
            'checkpoints_reached': self.stats.checkpoints_reached,
            'secrets_found': self.stats.secrets_found,
            'inventory': self.stats.inventory,
            'skills': self.stats.skills,
            'status_effects': self.stats.status_effects,
            'game_over': self.game_over,
            'won': self.won,
            'turn_count': self.turn_count,
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

        # Mark the solution path with a special value (100)
        for pos in self.complete_solution:
            y, x = pos
            # Don't overwrite special cells
            if maze_copy[y, x] == EnhancedCellType.PATH.value:
                maze_copy[y, x] = 100  # Special value for solution path

        return maze_copy
