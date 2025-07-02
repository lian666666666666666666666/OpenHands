import random

from enhanced_ai_player import EnhancedAIPlayer
from enhanced_maze_generator import EnhancedCellType


class OptimizedAIPlayer(EnhancedAIPlayer):
    """Optimized AI player with improved decision-making and anti-stuck mechanisms."""

    def __init__(self, maze, start_pos=None):
        """Initialize the optimized AI player."""
        super().__init__(maze, start_pos)

        # Additional tracking for anti-stuck mechanisms
        self.position_history = {}  # Position -> count of visits
        self.stuck_threshold = (
            3  # Number of visits to same position to consider "stuck"
        )
        self.last_target_type = None  # Track last target type to avoid oscillation
        self.consecutive_same_target = (
            0  # Count consecutive moves toward same target type
        )
        self.max_consecutive_target = 5  # Max consecutive moves toward same target type

        # Quest system
        self.current_quest = None
        self.quest_progress = 0
        self.quest_complete = False
        self.available_quests = [
            'resource_collector',  # Collect 5 resources
            'puzzle_master',  # Solve 3 puzzles
            'boss_slayer',  # Defeat the boss
            'explorer',  # Visit 10 unique cells
            'treasure_hunter',  # Find 2 secrets
        ]

        # Initialize a random quest
        self._select_random_quest()

    def _select_random_quest(self):
        """Select a random quest for the player."""
        if self.available_quests:
            self.current_quest = random.choice(self.available_quests)
            self.quest_progress = 0
            self.quest_complete = False

            # Set initial progress based on current state
            if self.current_quest == 'resource_collector':
                self.quest_progress = self.stats.resources
            elif self.current_quest == 'puzzle_master':
                self.quest_progress = self.stats.puzzles_solved
            elif self.current_quest == 'boss_slayer':
                self.quest_progress = 1 if self.stats.boss_defeated else 0
            elif self.current_quest == 'explorer':
                self.quest_progress = len(self.visited)
            elif self.current_quest == 'treasure_hunter':
                self.quest_progress = self.stats.secrets_found

    def _update_quest_progress(self):
        """Update the progress of the current quest."""
        if not self.current_quest or self.quest_complete:
            return

        old_progress = self.quest_progress

        # Update progress based on quest type
        if self.current_quest == 'resource_collector':
            self.quest_progress = self.stats.resources
            quest_target = 5
        elif self.current_quest == 'puzzle_master':
            self.quest_progress = self.stats.puzzles_solved
            quest_target = 3
        elif self.current_quest == 'boss_slayer':
            self.quest_progress = 1 if self.stats.boss_defeated else 0
            quest_target = 1
        elif self.current_quest == 'explorer':
            self.quest_progress = len(self.visited)
            quest_target = 10
        elif self.current_quest == 'treasure_hunter':
            self.quest_progress = self.stats.secrets_found
            quest_target = 2

        # Check if quest is complete
        if self.quest_progress >= quest_target:
            self.quest_complete = True

            # Give rewards for completing the quest
            if self.current_quest == 'resource_collector':
                self.stats.attack += 5
                self.stats.gold += 30
                return 'Resource Collector quest complete! Attack +5, Gold +30'
            elif self.current_quest == 'puzzle_master':
                self.stats.add_skill('advanced_puzzle_solving')
                self.stats.max_health += 20
                self.stats.health += 20
                return 'Puzzle Master quest complete! Learned advanced puzzle solving, Max Health +20'
            elif self.current_quest == 'boss_slayer':
                self.stats.attack += 10
                self.stats.defense += 5
                return 'Boss Slayer quest complete! Attack +10, Defense +5'
            elif self.current_quest == 'explorer':
                self.stats.add_skill('trap_detection')
                self.stats.add_skill('advanced_trap_detection')
                return 'Explorer quest complete! Learned trap detection skills'
            elif self.current_quest == 'treasure_hunter':
                self.stats.gold += 50
                self.stats.add_item('strength_potion')
                self.stats.add_item('health_potion')
                return 'Treasure Hunter quest complete! Gold +50, received potions'

        # If progress was made but quest not complete
        if self.quest_progress > old_progress:
            return f'Quest progress: {self.quest_progress}/{quest_target}'

        return None

    def move_to(self, position):
        """Override move_to to add anti-stuck mechanisms and quest tracking."""
        # Update position history for anti-stuck mechanism
        self.position_history[position] = self.position_history.get(position, 0) + 1

        # Call the parent method to perform the actual move
        result = super().move_to(position)

        # Update quest progress
        quest_update = self._update_quest_progress()
        if quest_update:
            self.action_log.append(quest_update)

            # If quest complete, select a new one
            if self.quest_complete:
                if self.current_quest in self.available_quests:
                    self.available_quests.remove(self.current_quest)

                if self.available_quests:
                    self._select_random_quest()
                    self.action_log.append(f'New quest: {self.current_quest}')

        return result

    def make_strategic_move(self):
        """Make a strategic move based on current game state with anti-stuck mechanisms."""
        if self.game_over:
            return 'Game over'

        # If we have a complete solution, use it
        if self.complete_solution and self.solution_index < len(self.complete_solution):
            next_pos = self.complete_solution[self.solution_index]
            self.solution_index += 1
            return self.move_to(next_pos)

        # Use inventory items if needed
        result = self._check_and_use_items()
        if result:
            return result

        # Get all possible targets with their paths
        targets = self._get_all_targets()

        # If no targets found, explore or move randomly
        if not targets:
            return self._explore_or_random()

        # Choose the best target based on current state and strategy
        best_target = self._choose_best_target(targets)

        # Move toward the chosen target
        if best_target and best_target['path'] and len(best_target['path']) > 0:
            # Check for target type oscillation
            if self.last_target_type == best_target['type']:
                self.consecutive_same_target += 1
            else:
                self.consecutive_same_target = 0
                self.last_target_type = best_target['type']

            # If we've been pursuing the same target type for too long, try something else
            if self.consecutive_same_target > self.max_consecutive_target:
                # Filter out the current target type
                alternative_targets = [
                    t for t in targets if t['type'] != self.last_target_type
                ]
                if alternative_targets:
                    best_target = self._choose_best_target(alternative_targets)
                    self.consecutive_same_target = 0
                    self.last_target_type = best_target['type']

            return self.move_to(best_target['path'][0])

        # Fallback: Explore or move randomly
        return self._explore_or_random()

    def _check_and_use_items(self):
        """Check if we need to use any items from inventory."""
        # Critical health - use health potion immediately
        if self.stats.health < self.stats.max_health * 0.3:
            for i, item in enumerate(self.stats.inventory):
                if item == 'health_potion':
                    return self.stats.use_item(i)

        # Prepare for boss battle
        if not self.stats.boss_defeated:
            # Check if boss is adjacent
            y, x = self.position
            for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                ny, nx = y + dy, x + dx
                if (
                    0 <= ny < self.height
                    and 0 <= nx < self.width
                    and self.maze[ny, nx] == EnhancedCellType.BOSS.value
                ):
                    # Boss is adjacent, use combat items
                    for i, item in enumerate(self.stats.inventory):
                        if item in ['strength_potion', 'defense_potion']:
                            return self.stats.use_item(i)

        # Use antidote if poisoned
        if 'poison' in self.stats.status_effects:
            for i, item in enumerate(self.stats.inventory):
                if item == 'antidote':
                    return self.stats.use_item(i)

        return None

    def _get_all_targets(self):
        """Get all possible targets with their paths and priorities."""
        targets = []

        # Check if boss is defeated
        if self.stats.boss_defeated:
            # Priority 1: Go for end
            end_path = self.find_path_to_target(EnhancedCellType.END.value)
            if end_path:
                targets.append(
                    {
                        'type': 'end',
                        'path': end_path,
                        'priority': 100,  # Highest priority
                        'distance': len(end_path),
                    }
                )
            return targets  # If boss is defeated, only care about reaching the end

        # Quest-related targets get priority boost
        quest_priority_boost = 20  # Boost for quest-related targets

        # Health-related targets (when health is low)
        if self.stats.health < self.stats.max_health * 0.5:
            # Checkpoints
            checkpoint_path = self.find_path_to_target(
                EnhancedCellType.CHECKPOINT.value
            )
            if checkpoint_path:
                priority = 90 if self.stats.health < self.stats.max_health * 0.3 else 70
                targets.append(
                    {
                        'type': 'checkpoint',
                        'path': checkpoint_path,
                        'priority': priority,
                        'distance': len(checkpoint_path),
                    }
                )

            # Small resources (might have health)
            resource_path = self.find_path_to_target(
                EnhancedCellType.RESOURCE_SMALL.value
            )
            if resource_path:
                priority = 85 if self.stats.health < self.stats.max_health * 0.3 else 65
                # Boost priority if on resource collector quest
                if (
                    self.current_quest == 'resource_collector'
                    and not self.quest_complete
                ):
                    priority += quest_priority_boost
                targets.append(
                    {
                        'type': 'small_resource',
                        'path': resource_path,
                        'priority': priority,
                        'distance': len(resource_path),
                    }
                )

        # Boss (if we're strong enough)
        boss_ready = self.stats.health > self.stats.max_health * 0.7 and (
            self.stats.resources >= 3 or self.stats.attack >= 15
        )

        if boss_ready:
            boss_path = self.find_path_to_target(EnhancedCellType.BOSS.value)
            if boss_path:
                priority = 80
                # Boost priority if on boss slayer quest
                if self.current_quest == 'boss_slayer' and not self.quest_complete:
                    priority += quest_priority_boost
                targets.append(
                    {
                        'type': 'boss',
                        'path': boss_path,
                        'priority': priority,
                        'distance': len(boss_path),
                    }
                )

        # Shop (if we have gold)
        if self.stats.gold >= 20:
            shop_path = self.find_path_to_target(EnhancedCellType.SHOP.value)
            if shop_path:
                priority = 75 if self.stats.health < self.stats.max_health * 0.5 else 55
                targets.append(
                    {
                        'type': 'shop',
                        'path': shop_path,
                        'priority': priority,
                        'distance': len(shop_path),
                    }
                )

        # Resources
        large_resource_path = self.find_path_to_target(
            EnhancedCellType.RESOURCE_LARGE.value
        )
        if large_resource_path:
            priority = 60
            # Boost priority if on resource collector quest
            if self.current_quest == 'resource_collector' and not self.quest_complete:
                priority += quest_priority_boost
            targets.append(
                {
                    'type': 'large_resource',
                    'path': large_resource_path,
                    'priority': priority,
                    'distance': len(large_resource_path),
                }
            )

        if not boss_ready:  # Only look for small resources if not ready for boss
            resource_path = self.find_path_to_target(
                EnhancedCellType.RESOURCE_SMALL.value
            )
            if resource_path:
                priority = 50
                # Boost priority if on resource collector quest
                if (
                    self.current_quest == 'resource_collector'
                    and not self.quest_complete
                ):
                    priority += quest_priority_boost
                targets.append(
                    {
                        'type': 'small_resource',
                        'path': resource_path,
                        'priority': priority,
                        'distance': len(resource_path),
                    }
                )

        # Puzzles
        easy_puzzle_path = self.find_path_to_target(EnhancedCellType.PUZZLE_EASY.value)
        if easy_puzzle_path:
            priority = 45
            # Boost priority if on puzzle master quest
            if self.current_quest == 'puzzle_master' and not self.quest_complete:
                priority += quest_priority_boost
            targets.append(
                {
                    'type': 'easy_puzzle',
                    'path': easy_puzzle_path,
                    'priority': priority,
                    'distance': len(easy_puzzle_path),
                }
            )

        hard_puzzle_path = self.find_path_to_target(EnhancedCellType.PUZZLE_HARD.value)
        if hard_puzzle_path:
            priority = 40
            # Boost priority if on puzzle master quest
            if self.current_quest == 'puzzle_master' and not self.quest_complete:
                priority += quest_priority_boost
            targets.append(
                {
                    'type': 'hard_puzzle',
                    'path': hard_puzzle_path,
                    'priority': priority,
                    'distance': len(hard_puzzle_path),
                }
            )

        # Secrets
        secret_path = self.find_path_to_target(EnhancedCellType.SECRET.value)
        if secret_path:
            priority = 35
            # Boost priority if on treasure hunter quest
            if self.current_quest == 'treasure_hunter' and not self.quest_complete:
                priority += quest_priority_boost
            targets.append(
                {
                    'type': 'secret',
                    'path': secret_path,
                    'priority': priority,
                    'distance': len(secret_path),
                }
            )

        # Boss (even if not ready)
        if not boss_ready:
            boss_path = self.find_path_to_target(EnhancedCellType.BOSS.value)
            if boss_path:
                priority = 30
                # Boost priority if on boss slayer quest
                if self.current_quest == 'boss_slayer' and not self.quest_complete:
                    priority += quest_priority_boost
                targets.append(
                    {
                        'type': 'boss',
                        'path': boss_path,
                        'priority': priority,
                        'distance': len(boss_path),
                    }
                )

        # Teleport
        teleport_path = self.find_path_to_target(EnhancedCellType.TELEPORT.value)
        if teleport_path:
            targets.append(
                {
                    'type': 'teleport',
                    'path': teleport_path,
                    'priority': 25,
                    'distance': len(teleport_path),
                }
            )

        # Boss minions
        minion_path = self.find_path_to_target(EnhancedCellType.BOSS_MINION.value)
        if minion_path:
            targets.append(
                {
                    'type': 'minion',
                    'path': minion_path,
                    'priority': 20,
                    'distance': len(minion_path),
                }
            )

        return targets

    def _choose_best_target(self, targets):
        """Choose the best target based on priority and distance."""
        if not targets:
            return None

        # First, check if we're stuck in a loop
        # If we've visited the same position multiple times, prioritize unexplored areas
        stuck_positions = [
            pos
            for pos, count in self.position_history.items()
            if count >= self.stuck_threshold
        ]

        # If we're stuck, prioritize exploration
        if stuck_positions and self.position in stuck_positions:
            # Temporarily boost priority of unexplored targets
            for target in targets:
                if target['path'] and target['path'][0] not in self.visited:
                    target['priority'] += 50
                elif target['path'] and target['path'][0] not in stuck_positions:
                    target['priority'] += 30

        # Sort by priority (high to low) and then by distance (short to long)
        sorted_targets = sorted(targets, key=lambda t: (-t['priority'], t['distance']))

        # Add randomness to prevent getting stuck in loops
        # 15% chance to choose a random target from top 3 choices
        if len(sorted_targets) >= 3 and random.random() < 0.15:
            return random.choice(sorted_targets[:3])

        return sorted_targets[0] if sorted_targets else None

    def _explore_or_random(self):
        """Explore unvisited paths or move randomly."""
        # Get valid moves
        valid_moves = self.get_valid_moves()

        # Prioritize unvisited moves
        unvisited_moves = [move for move in valid_moves if move not in self.visited]

        if unvisited_moves:
            # Boost explorer quest progress
            if self.current_quest == 'explorer' and not self.quest_complete:
                self.action_log.append('Exploring new areas...')

            return self.move_to(random.choice(unvisited_moves))

        # If all moves have been visited, choose the least visited one
        if valid_moves:
            visit_counts = {
                move: self.position_history.get(move, 0) for move in valid_moves
            }
            least_visited = min(valid_moves, key=lambda move: visit_counts[move])
            return self.move_to(least_visited)

        # Fallback: Move randomly
        return self.move_random()

    def get_status(self):
        """Get the current status of the AI player with quest information."""
        status = super().get_status()

        # Add quest information
        if self.current_quest:
            quest_info = {
                'resource_collector': {
                    'target': 5,
                    'description': 'Collect 5 resources',
                },
                'puzzle_master': {'target': 3, 'description': 'Solve 3 puzzles'},
                'boss_slayer': {'target': 1, 'description': 'Defeat the boss'},
                'explorer': {'target': 10, 'description': 'Visit 10 unique cells'},
                'treasure_hunter': {'target': 2, 'description': 'Find 2 secrets'},
            }

            quest_data = quest_info.get(self.current_quest, {})
            status['current_quest'] = self.current_quest
            status['quest_description'] = quest_data.get('description', '')
            status['quest_progress'] = self.quest_progress
            status['quest_target'] = quest_data.get('target', 0)
            status['quest_complete'] = self.quest_complete

        return status
