#!/usr/bin/env python3
import argparse
import os
import sys


def main():
    """Main entry point for the maze game."""
    parser = argparse.ArgumentParser(description='Luxury Maze Adventure')
    parser.add_argument(
        '--mode',
        choices=['web', 'terminal', 'advanced'],
        default='advanced',
        help='Interface mode: web, terminal, or advanced (default: advanced)',
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
        '--auto',
        action='store_true',
        help='Start in auto mode (advanced terminal only)',
    )
    parser.add_argument(
        '--show-solution',
        action='store_true',
        help='Show solution path (advanced terminal only)',
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

    else:  # advanced terminal mode
        # Import and run advanced terminal interface
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from advanced_terminal_interface import main

        main()


if __name__ == '__main__':
    main()
