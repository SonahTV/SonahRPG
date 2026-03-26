"""SonahRPG entry point.

Usage:
    python main.py             # Auto-detect: Pygame if available, else terminal
    python main.py --terminal  # Force terminal mode (Rich)
    python main.py --pygame    # Force Pygame mode
"""

import sys


def _is_frozen() -> bool:
    """True if running as a PyInstaller bundle."""
    return getattr(sys, "frozen", False)


def _can_use_terminal() -> bool:
    """Check if a terminal/console is available for Rich rendering."""
    try:
        # If stdout isn't connected to anything, terminal mode won't work
        if sys.stdout is None or not hasattr(sys.stdout, "write"):
            return False
        # On Windows, check if we have a console
        import msvcrt  # noqa: F401
        return True
    except (ImportError, OSError):
        return False


def main() -> None:
    force_terminal = "--terminal" in sys.argv
    force_pygame = "--pygame" in sys.argv or "--gui" in sys.argv

    if force_terminal:
        use_pygame = False
    elif force_pygame:
        use_pygame = True
    elif _is_frozen():
        # Packaged .exe → always use Pygame (no terminal available)
        use_pygame = True
    else:
        # Running from source → try terminal, fall back to Pygame
        use_pygame = not _can_use_terminal()

    if use_pygame:
        from engine.pygame_game import PygameGame
        from states.main_menu import MainMenuState

        game = PygameGame()
        game.state_manager.push(MainMenuState(game))
        game.run()
    else:
        from engine.game import Game
        from states.main_menu import MainMenuState

        game = Game()
        game.state_manager.push(MainMenuState(game))
        game.run()


if __name__ == "__main__":
    main()
