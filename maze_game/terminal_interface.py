import json
import time

from maze_engine import MazeEngine


def clear_screen():
    """Clear the terminal screen."""
    print('\033c', end='')


def print_header():
    """Print the game header."""
    print('=' * 60)
    print('                LUXURY MAZE ADVENTURE')
    print('=' * 60)
    print()


def print_status(status):
    """Print the player's status."""
    print('-' * 60)
    print(
        f'Health: {status["health"]}  |  Resources: {status["resources_collected"]}  |  '
        + f'Puzzles: {status["puzzles_solved"]}  |  Turn: {status["turn_count"]}'
    )
    print(
        f'Position: {status["player_position"]}  |  Boss Defeated: {"Yes" if status["boss_defeated"] else "No"}'
    )
    print('-' * 60)
    print()


def main():
    """Main function to run the terminal interface."""
    # Initialize the maze engine
    engine = MazeEngine(width=21, height=21, complexity=0.8, density=0.7)
    engine.new_game()

    # Game loop
    running = True
    while running:
        # Clear screen and print header
        clear_screen()
        print_header()

        # Print maze visualization
        print(engine.visualize_maze())

        # Print player status
        status = engine.get_game_summary()
        print_status(status)

        # Check if game is over
        if status['game_over']:
            if status['won']:
                print('Congratulations! You have won the game!')
            else:
                print('Game over! You have failed to complete the maze.')

            # Ask to play again
            play_again = input('Play again? (y/n): ').lower()
            if play_again == 'y':
                engine.new_game()
                continue
            else:
                running = False
                break

        # Menu options
        print('Options:')
        print('1. Advance one turn (AI makes a move)')
        print('2. Enter user input')
        print('3. Start new game')
        print('4. Quit')

        # Get user choice
        choice = input('Enter your choice (1-4): ')

        if choice == '1':
            # Advance one turn
            result = engine.advance_game()
            print(f'\nResult: {result["message"]}')
            input('Press Enter to continue...')

        elif choice == '2':
            # Get user input
            user_input = input('\nEnter your instructions for the AI player: ')

            # Process input
            prompt_result = engine.process_user_input(user_input)

            # Mock AI engine response
            print('\nGenerating AI response...')
            time.sleep(1)  # Simulate processing time

            # Extract AI status from the prompt for a simple mock response
            try:
                ai_status = json.loads(
                    prompt_result['prompt']
                    .split('## AI Player Status')[1]
                    .split('## User Input')[0]
                    .strip()
                )

                # Generate a simple response based on AI status
                response = f'The AI player is at position {ai_status["position"]}. '

                if ai_status['health'] < 50:
                    response += "The player's health is low, proceeding with caution. "

                if ai_status['resources'] > 0:
                    response += (
                        f'The player has collected {ai_status["resources"]} resources. '
                    )

                if ai_status['puzzles_solved'] > 0:
                    response += (
                        f'The player has solved {ai_status["puzzles_solved"]} puzzles. '
                    )

                if ai_status['boss_defeated']:
                    response += 'The boss has been defeated! Heading to the exit. '
                elif ai_status['game_over']:
                    if ai_status['won']:
                        response += 'Victory! The player has successfully completed the maze adventure.'
                    else:
                        response += 'Game over. The player has failed to complete the maze adventure.'
            except Exception as e:
                response = f'The AI player continues to navigate through the maze. Error: {str(e)}'

            print(f'\nAI Response: {response}')

            # Advance the game with the response
            result = engine.advance_game(response)
            print(f'\nResult: {result["message"]}')

            input('Press Enter to continue...')

        elif choice == '3':
            # Start new game
            engine.new_game()
            print('\nNew game started!')
            input('Press Enter to continue...')

        elif choice == '4':
            # Quit
            running = False

        else:
            print('\nInvalid choice. Please try again.')
            input('Press Enter to continue...')


if __name__ == '__main__':
    main()
