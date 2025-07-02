import json


class PromptGenerator:
    def __init__(self):
        """Initialize the prompt generator with default templates."""
        # Base template for all prompts
        self.base_template = """
# Maze Adventure Game

## Game Parameters
{game_parameters}

## Current Game State
{game_state}

## AI Player Status
{ai_status}

## User Input
{user_input}

## System Instructions
{system_instructions}

Based on the above information, generate the next step in the maze adventure.
Describe what happens as the AI navigates through the maze, encounters obstacles,
collects resources, solves puzzles, and battles the boss.
"""

        # Default system instructions
        self.default_system_instructions = """
1. Maintain the game's internal state according to the AI player's actions
2. Generate vivid descriptions of the maze environment
3. Create engaging narratives for resource collection, trap encounters, puzzle solving, and boss battles
4. Balance difficulty to provide an appropriate challenge
5. Ensure the game follows its internal logic and rules consistently
6. Respond to user input by adjusting the game experience accordingly
"""

    def generate_prompt(
        self,
        user_input,
        game_parameters,
        game_state,
        ai_status,
        system_instructions=None,
    ):
        """
        Generate a complete prompt for the AI engine.

        Args:
            user_input: Input from the user about how they want the game to proceed
            game_parameters: Dictionary of game parameters (size, complexity, etc.)
            game_state: Current state of the maze and game
            ai_status: Status of the AI player
            system_instructions: Optional custom system instructions

        Returns:
            A formatted prompt string
        """
        # Format game parameters
        formatted_params = json.dumps(game_parameters, indent=2)

        # Format game state
        formatted_state = json.dumps(game_state, indent=2)

        # Format AI status
        formatted_ai_status = json.dumps(ai_status, indent=2)

        # Use default system instructions if none provided
        if system_instructions is None:
            system_instructions = self.default_system_instructions

        # Fill in the template
        prompt = self.base_template.format(
            game_parameters=formatted_params,
            game_state=formatted_state,
            ai_status=formatted_ai_status,
            user_input=user_input,
            system_instructions=system_instructions,
        )

        return prompt

    def enhance_prompt_with_knowledge(self, prompt, knowledge_base):
        """
        Enhance the prompt with domain-specific knowledge.

        Args:
            prompt: The base prompt
            knowledge_base: Dictionary of domain-specific knowledge

        Returns:
            Enhanced prompt with knowledge incorporated
        """
        # Format knowledge as a section
        knowledge_section = '## Domain Knowledge\n'
        for category, info in knowledge_base.items():
            knowledge_section += f'### {category}\n{info}\n\n'

        # Insert knowledge before system instructions
        enhanced_prompt = prompt.replace(
            '## System Instructions', f'{knowledge_section}## System Instructions'
        )

        return enhanced_prompt
