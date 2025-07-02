#!/usr/bin/env python3
import argparse
import os
import sys


def main():
    """Main entry point for the maze game."""
    parser = argparse.ArgumentParser(description='Luxury Maze Adventure')
    parser.add_argument(
        '--mode',
        choices=['web', 'terminal', 'advanced', 'enhanced', 'quest', 'limited'],
        default='limited',
        help='Interface mode: web, terminal, advanced, enhanced, quest, or limited (default: limited)',
    )
    parser.add_argument(
        '--port', type=int, default=8000, help='Port for web interface (default: 8000)'
    )
    parser.add_argument(
        '--width', type=int, default=21, help='Width of the maze (default: 21)'
    )
    parser.add_argument(
        '--height', type=int, default=21, help='Height of the maze (default: 21)'
    )
    parser.add_argument(
        '--complexity',
        type=float,
        default=0.8,
        help='Complexity of the maze, 0-1 (default: 0.8)',
    )
    parser.add_argument(
        '--density',
        type=float,
        default=0.7,
        help='Density of the maze, 0-1 (default: 0.7)',
    )
    parser.add_argument(
        '--difficulty',
        choices=['easy', 'medium', 'hard'],
        default='medium',
        help='Game difficulty level (default: medium)',
    )
    parser.add_argument(
        '--auto',
        action='store_true',
        help='Start in auto mode (advanced/enhanced terminal only)',
    )
    parser.add_argument(
        '--show-solution',
        action='store_true',
        help='Show solution path (advanced/enhanced terminal only)',
    )
    parser.add_argument(
        '--show-inventory',
        action='store_true',
        help='Show inventory (enhanced/quest terminal only)',
    )
    parser.add_argument(
        '--show-quest',
        action='store_true',
        help='Show quest panel (quest terminal only)',
    )
    parser.add_argument(
        '--show-fog',
        action='store_true',
        help='Show fog of war (limited vision mode only)',
    )

    args = parser.parse_args()

    # Set environment variables for web mode
    if args.mode == 'web':
        os.environ['PORT'] = str(args.port)
        os.environ['MAZE_WIDTH'] = str(args.width)
        os.environ['MAZE_HEIGHT'] = str(args.height)
        os.environ['MAZE_COMPLEXITY'] = str(args.complexity)
        os.environ['MAZE_DENSITY'] = str(args.density)

        # Import and run web interface
        from web_interface import app

        app.run(host='0.0.0.0', port=args.port, debug=True)

    elif args.mode == 'terminal':
        # Import and run terminal interface
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from terminal_interface import main

        main()

    elif args.mode == 'advanced':
        # Import and run advanced terminal interface
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from advanced_terminal_interface import main

        main()

    elif args.mode == 'enhanced':
        # Import and run enhanced terminal interface
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from enhanced_terminal_interface import main

        main()

    elif args.mode == 'quest':
        # Import and run quest terminal interface
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from quest_terminal_interface import main

        main()

    else:  # limited vision mode
        # Import and run limited vision interface
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from limited_vision_interface import main

        main()


if __name__ == '__main__':
    main()
