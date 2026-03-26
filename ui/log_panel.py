from rich.panel import Panel
from rich.text import Text


class LogPanel:
    """Scrolling combat/event log that displays recent messages."""

    def render(self, log_messages: list[str], max_lines: int = 6) -> Panel:
        """Render the last N log messages in a panel.

        Messages can contain Rich markup for coloring.
        Most recent messages appear at the bottom.
        Empty lines pad the top if fewer messages than max_lines.
        """
        if log_messages is None:
            log_messages = []

        recent = log_messages[-max_lines:] if len(log_messages) > max_lines else list(log_messages)
        text = Text()

        # Pad with empty lines at the top if fewer messages
        pad_count = max_lines - len(recent)
        for _ in range(pad_count):
            text.append("\n")

        for i, msg in enumerate(recent):
            try:
                rendered = Text.from_markup(f" {msg}")
            except Exception:
                # If markup parsing fails, render as plain text
                rendered = Text(f" {msg}")
            text.append_text(rendered)
            if i < len(recent) - 1 or pad_count == 0:
                text.append("\n")

        return Panel(text, title="[bold]Log[/bold]", border_style="yellow")
