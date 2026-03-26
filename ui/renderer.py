from rich.layout import Layout
from rich.panel import Panel
from rich.console import Console, Group, RenderableType
from rich.text import Text
from rich.table import Table


class GameRenderer:
    """Main renderer that composes the game layout using Rich layouts."""

    def __init__(self):
        self.console = Console()

    def create_exploration_layout(
        self,
        map_renderable: RenderableType,
        stats_renderable: RenderableType,
        minimap_renderable: RenderableType,
        log_renderable: RenderableType,
        hotbar_renderable: RenderableType,
    ) -> Layout:
        """Create the main exploration UI layout.

        ┌──────────────────────────────┬──────────────┐
        │         MAP VIEW             │  STATS       │
        │    (75% width)               │  MINIMAP     │
        │                              │  (25% width) │
        ├──────────────────────────────┴──────────────┤
        │  LOG (height=8)                             │
        ├─────────────────────────────────────────────┤
        │  HOTBAR (height=3)                          │
        └─────────────────────────────────────────────┘
        """
        layout = Layout()
        layout.split_column(
            Layout(name="main", ratio=3),
            Layout(name="log", size=8),
            Layout(name="hotbar", size=3),
        )
        layout["main"].split_row(
            Layout(name="map", ratio=3),
            Layout(name="sidebar", ratio=1, minimum_size=25),
        )
        layout["sidebar"].split_column(
            Layout(name="stats", ratio=2),
            Layout(name="minimap", ratio=1),
        )

        layout["map"].update(map_renderable)
        layout["stats"].update(stats_renderable)
        layout["minimap"].update(minimap_renderable)
        layout["log"].update(log_renderable)
        layout["hotbar"].update(hotbar_renderable)

        return layout

    def create_combat_layout(
        self,
        combat_renderable: RenderableType,
        stats_renderable: RenderableType,
        log_renderable: RenderableType,
        hotbar_renderable: RenderableType,
    ) -> Layout:
        """Create combat UI layout - combat view replaces map+minimap."""
        layout = Layout()
        layout.split_column(
            Layout(name="main", ratio=3),
            Layout(name="log", size=10),
            Layout(name="hotbar", size=3),
        )
        layout["main"].split_row(
            Layout(name="combat", ratio=3),
            Layout(name="stats", ratio=1, minimum_size=25),
        )

        layout["combat"].update(combat_renderable)
        layout["stats"].update(stats_renderable)
        layout["log"].update(log_renderable)
        layout["hotbar"].update(hotbar_renderable)

        return layout

    def create_fullscreen_layout(
        self,
        content_renderable: RenderableType,
        hotbar_renderable: RenderableType = None,
    ) -> Layout:
        """Create fullscreen layout (for menus, inventory, character screen)."""
        if hotbar_renderable:
            layout = Layout()
            layout.split_column(
                Layout(name="content", ratio=1),
                Layout(name="hotbar", size=3),
            )
            layout["content"].update(content_renderable)
            layout["hotbar"].update(hotbar_renderable)
            return layout
        return Layout(content_renderable)

    def render(self, layout: Layout) -> None:
        """Clear screen and print the given layout."""
        self.console.clear()
        self.console.print(layout)
