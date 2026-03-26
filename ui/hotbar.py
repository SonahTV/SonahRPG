from rich.panel import Panel
from rich.text import Text


class Hotbar:
    """Bottom hotbar showing available commands/keybindings."""

    def render(self, actions: list[tuple[str, str]], context: str = "") -> Panel:
        """Render the hotbar with available actions.

        Args:
            actions: List of (key, description) tuples, e.g.
                     [("W/A/S/D", "Move"), ("I", "Inventory"), ("C", "Character"), ("ESC", "Menu")]
            context: Optional context string shown dimmed on the right side.
        """
        if not actions:
            return Panel(Text("  No actions available", style="dim"), border_style="dim")

        text = Text("  ")
        for i, (key, desc) in enumerate(actions):
            text.append(f"[{key}]", style="bold bright_yellow")
            text.append(f" {desc}", style="white")
            if i < len(actions) - 1:
                text.append("  ", style="dim")

        if context:
            text.append(f"  | {context}", style="dim italic")

        return Panel(text, border_style="dim")
