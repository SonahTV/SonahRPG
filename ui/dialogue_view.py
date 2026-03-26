from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.table import Table


class DialogueView:
    """NPC dialogue rendering with portrait, text, and selectable options."""

    def render(
        self,
        npc_name: str,
        npc_art: str,
        dialogue_text: str,
        options: list[str] = None,
        selected_option: int = 0,
    ) -> Panel:
        """Render NPC dialogue with portrait and text.

        Shows NPC ASCII art, name, dialogue text, and selectable response options.
        The currently selected option is highlighted.

        Args:
            npc_name: Display name of the NPC.
            npc_art: ASCII art string for the NPC portrait.
            dialogue_text: The dialogue text to display.
            options: Optional list of player response options.
            selected_option: Index of the currently highlighted option.
        """
        parts = []

        # NPC portrait and name section
        portrait_text = Text()

        if npc_art:
            # Split art into lines and render
            for line in npc_art.split("\n"):
                portrait_text.append(f" {line}\n", style="bright_cyan")

        portrait_text.append(f"\n {npc_name}\n", style="bold bright_white")

        # Use a grid to lay out portrait on left and dialogue on right
        dialogue_section = Text()
        dialogue_section.append("─" * 40 + "\n", style="dim")
        dialogue_section.append(f"\n {dialogue_text}\n", style="italic")

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=2)
        grid.add_row(Panel(portrait_text, border_style="dim cyan"), dialogue_section)
        parts.append(grid)

        # Response options
        if options:
            options_text = Text("\n")
            for i, opt in enumerate(options):
                if i == selected_option:
                    options_text.append(f"  > {opt}\n", style="bold bright_yellow")
                else:
                    options_text.append(f"    {opt}\n", style="white")
            options_text.append("\n")
            parts.append(options_text)

        # Hint
        hint = Text("  ")
        if options:
            hint.append("[UP/DOWN]", style="bold bright_yellow")
            hint.append(" Select  ")
            hint.append("[ENTER]", style="bold bright_yellow")
            hint.append(" Confirm  ")
        hint.append("[ESC]", style="bold bright_yellow")
        hint.append(" Leave")
        parts.append(hint)

        return Panel(
            Group(*parts),
            title="[bold cyan]Dialogue[/bold cyan]",
            border_style="cyan",
        )
