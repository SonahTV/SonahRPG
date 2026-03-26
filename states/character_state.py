"""Character sheet state -- stats, skills, and equipment tabs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from engine.state import GameState

if TYPE_CHECKING:
    from rich.console import RenderableType

    from engine.game import Game


class CharacterState(GameState):
    """Fullscreen character sheet with three tabs: Stats, Skills, Equipment.

    In the Skills tab the player can spend skill points to learn new abilities.
    """

    def __init__(self, game: Game) -> None:
        super().__init__(game)
        self.tab = "stats"  # "stats", "skills", "equipment"
        self.skill_selected = 0

    # -- input ---------------------------------------------------------

    def handle_input(self, key: str) -> None:
        if key in ("escape", "c"):
            self.game.state_manager.pop()
        elif key == "1":
            self.tab = "stats"
        elif key == "2":
            self.tab = "skills"
        elif key == "3":
            self.tab = "equipment"
        elif self.tab == "skills":
            if key == "up":
                self.skill_selected = max(0, self.skill_selected - 1)
            elif key == "down":
                self.skill_selected += 1
            elif key == "enter":
                self._learn_skill()

    def _learn_skill(self) -> None:
        from systems.skills import SkillSystem

        player = self.game.player
        skill_sys = SkillSystem(self.game)
        learnable = skill_sys.get_learnable_skills(player)
        if learnable and 0 <= self.skill_selected < len(learnable):
            success, msg = skill_sys.learn_skill(
                player, learnable[self.skill_selected]["name"]
            )
            self.game.add_log(msg)

    # -- update --------------------------------------------------------

    def update(self, dt: float) -> None:
        pass

    # -- render --------------------------------------------------------

    def render(self) -> RenderableType:
        from rich.console import Group
        from rich.panel import Panel
        from rich.text import Text
        from ui.hotbar import Hotbar
        from ui.renderer import GameRenderer

        player = self.game.player

        # Tab header
        header = Text("  ")
        for tab_name, tab_key in [("Stats", "1"), ("Skills", "2"), ("Equipment", "3")]:
            if tab_name.lower() == self.tab:
                header.append(f" [{tab_key}] {tab_name} ", style="bold black on white")
            else:
                header.append(f" [{tab_key}] {tab_name} ", style="dim")
            header.append("  ")

        content = Text()

        if self.tab == "stats":
            self._render_stats(player, content)
        elif self.tab == "skills":
            self._render_skills(player, content)
        elif self.tab == "equipment":
            self._render_equipment(player, content)

        main_panel = Panel(
            Group(header, content),
            title=f"[bold]{player.name}[/bold]",
            border_style="bright_cyan",
        )

        # Hotbar
        hotbar = Hotbar()
        if self.tab == "skills":
            actions = [
                ("Up/Down", "Select"),
                ("Enter", "Learn"),
                ("1/2/3", "Tabs"),
                ("Esc", "Back"),
            ]
        else:
            actions = [("1/2/3", "Tabs"), ("Esc", "Back")]
        hotbar_panel = hotbar.render(actions)

        return GameRenderer().create_fullscreen_layout(main_panel, hotbar_panel)

    # -- tab renderers -------------------------------------------------

    @staticmethod
    def _render_stats(player, content: Text) -> None:
        content.append(
            f"\n  {player.name} -- Level {player.level} {player.player_class}\n\n",
            style="bold bright_white",
        )
        stats_data = [
            ("STR", player.stats.STR, "Physical power, melee damage"),
            ("DEX", player.stats.DEX, "Agility, crit chance, dodge"),
            ("INT", player.stats.INT, "Spell power, max MP"),
            ("WIS", player.stats.WIS, "Healing, MP regen"),
            ("CON", player.stats.CON, "Vitality, max HP, defense"),
            ("CHA", player.stats.CHA, "Shop prices, quest rewards"),
        ]
        for stat_name, val, desc in stats_data:
            content.append(f"  {stat_name}: ", style="bold")
            content.append(f"{val:>3}", style="bright_white")
            content.append(f"  {desc}\n", style="dim")

        content.append(
            f"\n  HP: {player.current_hp}/{player.max_hp}  ", style="bold red"
        )
        content.append(f"MP: {player.current_mp}/{player.max_mp}\n", style="bold blue")
        content.append(
            f"  ATK: {player.attack}  DEF: {player.defense}\n", style="bold"
        )
        content.append(
            f"  Crit: {player.crit_chance}%  Dodge: {player.dodge_chance}%\n"
        )
        content.append(
            f"  XP: {player.xp}/{player.xp_to_next}  Skill Points: {player.skill_points}\n",
            style="green",
        )

    def _render_skills(self, player, content: Text) -> None:
        from systems.skills import SkillSystem

        skill_sys = SkillSystem(self.game)
        learnable = skill_sys.get_learnable_skills(player)
        known = skill_sys.get_available_skills(player)

        content.append(
            f"\n  Known Skills (Skill Points: {player.skill_points}):\n\n",
            style="bold",
        )
        for skill in known:
            content.append(f"  + {skill['name']}", style="bold bright_green")
            mp = skill.get("mp_cost", 0)
            mult = skill.get("damage_multiplier", 0)
            content.append(f"  MP:{mp} DMG:{mult}x", style="dim")
            content.append(f"  {skill.get('description', '')}\n", style="dim italic")

        if learnable:
            content.append("\n  Learnable Skills:\n\n", style="bold yellow")
            # Clamp skill_selected
            self.skill_selected = min(self.skill_selected, len(learnable) - 1)
            for i, skill in enumerate(learnable):
                cursor = "> " if i == self.skill_selected else "  "
                style = "bold bright_white" if i == self.skill_selected else ""
                content.append(f"  {cursor}{skill['name']}", style=style)
                content.append(
                    f"  Lv.{skill['level_required']} MP:{skill['mp_cost']}",
                    style="dim",
                )
                content.append(
                    f"  {skill.get('description', '')}\n", style="dim italic"
                )

    @staticmethod
    def _render_equipment(player, content: Text) -> None:
        slots = [
            ("Weapon", player.equipment.weapon),
            ("Armor", player.equipment.armor),
            ("Helmet", player.equipment.helmet),
            ("Boots", player.equipment.boots),
            ("Ring", player.equipment.ring),
            ("Amulet", player.equipment.amulet),
        ]
        content.append("\n  Equipment:\n\n", style="bold")
        for slot_name, item in slots:
            content.append(f"  {slot_name}: ", style="bold")
            if item:
                content.append(f"{item.get('name', 'Unknown')}\n", style="bright_white")
                bonuses = item.get("bonuses", {})
                if bonuses:
                    stat_str = ", ".join(
                        f"{k}:+{v}" for k, v in bonuses.items() if v > 0
                    )
                    if stat_str:
                        content.append(f"    {stat_str}\n", style="dim green")
            else:
                content.append("Empty\n", style="dim")

    def render_pygame(self, screen, font, renderer) -> None:
        """Render character sheet to Pygame."""
        import pygame
        from pygame_ui.colors import get_rgb
        from pygame_ui.pg_hotbar import PgHotbar

        w, h = renderer.screen_width, renderer.screen_height - renderer.hotbar_height
        surface = pygame.Surface((w, h))
        surface.fill((10, 10, 20))

        player = self.game.player
        y = 8

        # Tab header
        x = 20
        for tab_name, tab_key in [("Stats", "1"), ("Skills", "2"), ("Equipment", "3")]:
            if tab_name.lower() == self.tab:
                text = f" [{tab_key}] {tab_name} "
                surf = font.render_text(text, (0, 0, 0), (200, 200, 200))
            else:
                text = f" [{tab_key}] {tab_name} "
                surf = font.render_text(text, get_rgb("grey50"))
            surface.blit(surf, (x, y))
            x += surf.get_width() + 16
        y += font.char_height * 2

        # Content based on tab
        if self.tab == "stats":
            lines = [
                (f"  {player.name} -- Lv.{player.level} {player.player_class}", "bright_white"),
                ("", "white"),
                (f"  STR: {player.stats.STR}  DEX: {player.stats.DEX}  INT: {player.stats.INT}", "bright_white"),
                (f"  WIS: {player.stats.WIS}  CON: {player.stats.CON}  CHA: {player.stats.CHA}", "bright_white"),
                ("", "white"),
                (f"  HP: {player.current_hp}/{player.max_hp}  MP: {player.current_mp}/{player.max_mp}", "bright_white"),
                (f"  ATK: {player.attack}  DEF: {player.defense}", "bright_white"),
                (f"  Crit: {player.crit_chance}%  Dodge: {player.dodge_chance}%", "white"),
                (f"  XP: {player.xp}/{player.xp_to_next}  SP: {player.skill_points}", "green"),
            ]
        elif self.tab == "equipment":
            slots = [
                ("Weapon", player.equipment.weapon),
                ("Armor", player.equipment.armor),
                ("Helmet", player.equipment.helmet),
                ("Boots", player.equipment.boots),
                ("Ring", player.equipment.ring),
                ("Amulet", player.equipment.amulet),
            ]
            lines = [("  Equipment:", "bright_white"), ("", "white")]
            for sname, item in slots:
                iname = item.get("name", "Empty") if item else "Empty"
                color = "bright_white" if item else "grey50"
                lines.append((f"  {sname}: {iname}", color))
        else:
            lines = [(f"  Skills (SP: {player.skill_points}):", "bright_white"), ("", "white")]
            for skill_name in player.known_skills:
                lines.append((f"  + {skill_name}", "bright_green"))

        for text, color in lines:
            if text:
                surface.blit(font.render_text(text, get_rgb(color)), (20, y))
            y += font.char_height

        pygame.draw.rect(surface, get_rgb("bright_cyan"), surface.get_rect(), 1)

        hotbar = PgHotbar()
        hotbar_surf = hotbar.render(
            [("1/2/3", "Tabs"), ("Esc", "Back")],
            font, renderer.hotbar_rect.width, renderer.hotbar_rect.height,
        )
        renderer.draw_fullscreen_layout(screen, surface, hotbar_surf)
