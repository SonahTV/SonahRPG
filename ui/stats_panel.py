from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.console import Group
from rich.progress_bar import ProgressBar


class StatsPanel:
    """Renders the player stats sidebar with HP/MP/XP bars, attributes, and gear."""

    def render(self, player) -> Panel:
        """Render player stats panel.

        Shows:
        - Player name and class
        - Level + XP bar
        - HP bar (colored red -> green based on percentage)
        - MP bar (colored blue)
        - Core stats (STR, DEX, INT, WIS, CON, CHA)
        - Attack / Defense
        - Crit% / Dodge%
        - Gold
        - Floor number
        - Active status effects with duration
        - Equipment summary (weapon + armor names)
        """
        text = Text()

        # Name and class
        name = getattr(player, "name", "Hero")
        player_class = getattr(player, "player_class", "Adventurer")
        level = getattr(player, "level", 1)

        text.append(f" {name}\n", style="bold bright_white")
        text.append(f" {player_class} ", style="italic")
        text.append(f"Lv.{level}\n\n", style="bold yellow")

        # HP bar
        current_hp = getattr(player, "current_hp", 0)
        max_hp = getattr(player, "max_hp", 1)
        hp_pct = current_hp / max_hp if max_hp > 0 else 0

        if hp_pct < 0.3:
            hp_color = "bright_red"
        elif hp_pct < 0.6:
            hp_color = "yellow"
        else:
            hp_color = "bright_green"

        hp_filled = int(hp_pct * 15)
        text.append(" HP ", style="bold red")
        text.append("█" * hp_filled, style=hp_color)
        text.append("░" * (15 - hp_filled), style="dim")
        text.append(f" {current_hp}/{max_hp}\n", style="bold")

        # MP bar
        current_mp = getattr(player, "current_mp", 0)
        max_mp = getattr(player, "max_mp", 1)
        mp_pct = current_mp / max_mp if max_mp > 0 else 0
        mp_filled = int(mp_pct * 15)

        text.append(" MP ", style="bold blue")
        text.append("█" * mp_filled, style="bright_blue")
        text.append("░" * (15 - mp_filled), style="dim")
        text.append(f" {current_mp}/{max_mp}\n", style="bold")

        # XP bar
        xp = getattr(player, "xp", 0)
        xp_to_next = getattr(player, "xp_to_next", 100)
        xp_pct = xp / xp_to_next if xp_to_next > 0 else 0
        xp_filled = int(xp_pct * 15)

        text.append(" XP ", style="bold green")
        text.append("█" * xp_filled, style="bright_green")
        text.append("░" * (15 - xp_filled), style="dim")
        text.append(f" {xp}/{xp_to_next}\n\n", style="bold")

        # Core stats
        text.append(" --- Stats ---\n", style="dim")

        player_stats = getattr(player, "stats", None)
        stat_defs = [
            ("STR", "red"),
            ("DEX", "green"),
            ("INT", "blue"),
            ("WIS", "cyan"),
            ("CON", "yellow"),
            ("CHA", "magenta"),
        ]

        for stat_name, color in stat_defs:
            val = 0
            if player_stats is not None:
                if isinstance(player_stats, dict):
                    val = player_stats.get(stat_name, 0)
                else:
                    val = getattr(player_stats, stat_name, 0)

            text.append(f" {stat_name}: ", style=f"bold {color}")
            text.append(f"{val:>3}\n")

        # Combat stats
        attack = getattr(player, "attack", 0)
        defense = getattr(player, "defense", 0)
        crit = getattr(player, "crit_chance", 0)
        dodge = getattr(player, "dodge_chance", 0)

        text.append(f"\n ATK: {attack}  DEF: {defense}\n", style="bold")
        text.append(f" CRT: {crit}%  DDG: {dodge}%\n")

        # Gold and floor
        gold = getattr(player, "gold", 0)
        floor = getattr(player, "floor", 1)
        text.append(f"\n Gold: {gold}\n", style="yellow")
        text.append(f" Floor: {floor}\n")

        # Status effects
        status_effects = getattr(player, "status_effects", None)
        if status_effects:
            text.append("\n --- Effects ---\n", style="dim")
            for se in status_effects:
                if isinstance(se, dict):
                    se_name = se.get("name", "?")
                    se_dur = se.get("duration", 0)
                elif hasattr(se, "name"):
                    se_name = se.name
                    se_dur = getattr(se, "duration", 0)
                else:
                    se_name = str(se)
                    se_dur = 0

                # Determine icon and style based on effect type
                name_lower = se_name.lower()
                if "poison" in name_lower:
                    icon = "●"
                    se_style = "bright_green"
                elif "stun" in name_lower:
                    icon = "◆"
                    se_style = "bright_yellow"
                elif "burn" in name_lower or "fire" in name_lower:
                    icon = "▲"
                    se_style = "bright_red"
                elif "shield" in name_lower or "protect" in name_lower:
                    icon = "●"
                    se_style = "bright_cyan"
                elif se_dur > 0:
                    # Other buffs (positive duration = buff)
                    icon = "+"
                    se_style = "bright_green"
                else:
                    # Other debuffs
                    icon = "-"
                    se_style = "bright_red"

                text.append(f" {icon} ", style=se_style)
                text.append(f"{se_name}", style=se_style)
                text.append(f" ({se_dur}t)\n", style="dim")

        # Equipment
        text.append("\n --- Gear ---\n", style="dim")

        equipment = getattr(player, "equipment", None)
        weapon = None
        armor = None

        if equipment is not None:
            if isinstance(equipment, dict):
                weapon = equipment.get("weapon")
                armor = equipment.get("armor")
            else:
                weapon = getattr(equipment, "weapon", None)
                armor = getattr(equipment, "armor", None)

        weapon_name = "None"
        if weapon is not None:
            if isinstance(weapon, dict):
                weapon_name = weapon.get("name", "Unknown")
            elif hasattr(weapon, "name"):
                weapon_name = weapon.name
            else:
                weapon_name = str(weapon)

        armor_name = "None"
        if armor is not None:
            if isinstance(armor, dict):
                armor_name = armor.get("name", "Unknown")
            elif hasattr(armor, "name"):
                armor_name = armor.name
            else:
                armor_name = str(armor)

        text.append(f" Wpn: {weapon_name}\n", style="white")
        text.append(f" Arm: {armor_name}\n", style="white")

        return Panel(text, title="[bold]Character[/bold]", border_style="cyan", width=28)
