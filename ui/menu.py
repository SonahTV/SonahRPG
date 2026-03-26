from rich.panel import Panel
from rich.text import Text
from rich.console import Group


class Menu:
    """Generic menu component for navigable selections."""

    def __init__(self, title: str, options: list[str], descriptions: list[str] = None):
        self.title = title
        self.options = options
        self.descriptions = descriptions or [""] * len(options)
        self.selected_index = 0

    def move_up(self) -> None:
        """Move selection up, wrapping around to bottom."""
        if self.options:
            self.selected_index = (self.selected_index - 1) % len(self.options)

    def move_down(self) -> None:
        """Move selection down, wrapping around to top."""
        if self.options:
            self.selected_index = (self.selected_index + 1) % len(self.options)

    def get_selected(self) -> str:
        """Return the currently selected option string."""
        if not self.options:
            return ""
        return self.options[self.selected_index]

    def get_selected_index(self) -> int:
        """Return the currently selected index."""
        return self.selected_index

    def set_options(self, options: list[str], descriptions: list[str] = None) -> None:
        """Replace the menu options and reset selection."""
        self.options = options
        self.descriptions = descriptions or [""] * len(options)
        self.selected_index = 0

    def render(self) -> Panel:
        """Render the menu with current selection highlighted."""
        text = Text()
        text.append("\n")

        if not self.options:
            text.append("    No options available\n", style="dim italic")
        else:
            for i, (option, desc) in enumerate(zip(self.options, self.descriptions)):
                if i == self.selected_index:
                    text.append(f"  > {option}", style="bold bright_white on blue")
                else:
                    text.append(f"    {option}", style="white")

                if desc:
                    text.append(f"  {desc}", style="dim italic")

                text.append("\n\n")

        return Panel(
            text,
            title=f"[bold]{self.title}[/bold]",
            border_style="bright_blue",
            padding=(1, 2),
        )
