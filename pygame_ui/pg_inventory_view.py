"""Pygame inventory view — item list with rarity coloring and detail panel."""

import pygame
from pygame_ui.colors import get_rgb
from pygame_ui.font_manager import FontManager

RARITY_COLORS = {
    "common": "white", "uncommon": "green", "rare": "bright_blue",
    "epic": "bright_magenta", "legendary": "bright_yellow",
}

TYPE_ICONS = {
    "equipment": "[E]",
    "consumable": "[C]",
    "junk": "[$]",
    "gold": "[G]",
}


class PgInventoryView:
    def render(self, inventory: list[dict], selected_index: int, equipment: object,
               font: FontManager, width: int, height: int) -> pygame.Surface:
        surface = pygame.Surface((width, height))
        surface.fill((10, 10, 20))

        y = 8
        title = font.render_text(" Inventory ", get_rgb("bright_white"))
        surface.blit(title, (width // 2 - title.get_width() // 2, y))
        y += font.char_height + 4

        # Item count
        count_text = f" {len(inventory)}/20 items"
        surface.blit(font.render_text(count_text, get_rgb("grey50")), (8, y))
        y += font.char_height + 8

        if not inventory:
            empty = font.render_text("  Your pack is empty.", get_rgb("grey50"))
            surface.blit(empty, (8, y))
            y += font.char_height * 2
            hint = font.render_text("  Explore the dungeon and press [G] to pick up items.", get_rgb("grey42"))
            surface.blit(hint, (8, y))
        else:
            # Split: left = item list, right = detail panel
            list_width = width // 2 - 20
            detail_x = width // 2 + 10
            detail_width = width // 2 - 20

            # --- Left: item list ---
            list_y = y
            max_visible = (height - list_y - 30) // (font.char_height + 2)

            # Scroll offset
            scroll = max(0, selected_index - max_visible + 3)

            for idx in range(scroll, min(len(inventory), scroll + max_visible)):
                item = inventory[idx]
                name = item.get("name", "Unknown")
                rarity = item.get("rarity", "common")
                item_type = item.get("type", "")
                color_name = RARITY_COLORS.get(rarity, "white")
                icon = TYPE_ICONS.get(item_type, "   ")

                if idx == selected_index:
                    # Highlight bar
                    pygame.draw.rect(
                        surface, (30, 25, 50),
                        (4, list_y, list_width, font.char_height),
                    )
                    prefix = "> "
                    color = get_rgb(color_name)
                else:
                    prefix = "  "
                    # Dim non-selected items slightly
                    base = get_rgb(color_name)
                    color = (base[0] * 2 // 3, base[1] * 2 // 3, base[2] * 2 // 3)

                # Icon
                icon_surf = font.render_text(icon, get_rgb("grey42"))
                surface.blit(icon_surf, (8, list_y))

                # Name
                text = f"{prefix}{name}"
                # Truncate if too long
                max_name_chars = (list_width - font.char_width * 6) // font.char_width
                if len(text) > max_name_chars:
                    text = text[:max_name_chars - 2] + ".."
                text_surf = font.render_text(text, color)
                surface.blit(text_surf, (8 + font.char_width * 4, list_y))

                list_y += font.char_height + 2

            # Scroll indicator
            if len(inventory) > max_visible:
                total = len(inventory)
                bar_h = max(10, int((max_visible / total) * (list_y - y)))
                bar_y = y + int((scroll / total) * (list_y - y))
                pygame.draw.rect(
                    surface, (40, 35, 60),
                    (list_width + 2, bar_y, 3, bar_h),
                )

            # --- Right: detail panel ---
            if 0 <= selected_index < len(inventory):
                item = inventory[selected_index]
                detail_y = y

                # Panel background
                pygame.draw.rect(
                    surface, (15, 12, 25),
                    (detail_x, detail_y, detail_width, height - detail_y - 60),
                )
                pygame.draw.rect(
                    surface, (40, 35, 60),
                    (detail_x, detail_y, detail_width, height - detail_y - 60), 1,
                )

                dy = detail_y + 8
                pad = detail_x + 10

                # Item name in rarity color
                rarity = item.get("rarity", "common")
                name = item.get("name", "Unknown")
                name_color = get_rgb(RARITY_COLORS.get(rarity, "white"))
                surface.blit(font.render_text(name, name_color), (pad, dy))
                dy += font.char_height

                # Rarity + type
                item_type = item.get("type", "unknown")
                rarity_text = f"{rarity.title()} {item_type.title()}"
                surface.blit(font.render_text(rarity_text, get_rgb("grey50")), (pad, dy))
                dy += font.char_height + 8

                # Separator
                sep_w = detail_width - 20
                pygame.draw.line(surface, (40, 35, 55), (pad, dy), (pad + sep_w, dy))
                dy += 6

                # Description
                desc = item.get("description", "")
                if desc:
                    max_chars = (detail_width - 20) // font.char_width
                    words = desc.split()
                    lines: list[str] = []
                    cur = ""
                    for word in words:
                        if len(cur) + len(word) + 1 > max_chars:
                            lines.append(cur)
                            cur = word
                        else:
                            cur = f"{cur} {word}" if cur else word
                    if cur:
                        lines.append(cur)
                    for line in lines:
                        surface.blit(font.render_text(line, get_rgb("white")), (pad, dy))
                        dy += font.char_height
                    dy += 6

                # Stat bonuses for equipment
                bonuses = item.get("bonuses", {})
                if bonuses:
                    pygame.draw.line(surface, (40, 35, 55), (pad, dy), (pad + sep_w, dy))
                    dy += 6
                    for stat, val in bonuses.items():
                        if val > 0:
                            stat_display = stat.replace("_", " ").title()
                            color = (100, 220, 100)  # green for positive
                            surface.blit(
                                font.render_text(f"+{val} {stat_display}", color),
                                (pad, dy),
                            )
                            dy += font.char_height
                    dy += 4

                # Effect for consumables
                effect = item.get("effect", "")
                value = item.get("value", 0)
                if effect and item_type == "consumable":
                    pygame.draw.line(surface, (40, 35, 55), (pad, dy), (pad + sep_w, dy))
                    dy += 6
                    effect_text = {
                        "heal": f"Restores {value} HP",
                        "restore_mp": f"Restores {value} MP",
                        "cure": "Removes negative effects",
                        "buff_str": f"+{value} STR for 3 turns",
                        "buff_dex": f"+{value} DEX for 3 turns",
                        "buff_int": f"+{value} INT for 3 turns",
                    }.get(effect, f"Effect: {effect}")
                    surface.blit(
                        font.render_text(effect_text, (100, 180, 255)),
                        (pad, dy),
                    )
                    dy += font.char_height + 4

                # Gold value
                gold_val = item.get("gold_value", 0)
                if gold_val > 0:
                    surface.blit(
                        font.render_text(f"Value: {gold_val}g", get_rgb("yellow")),
                        (pad, dy),
                    )
                    dy += font.char_height + 8

                # Action hint based on type
                pygame.draw.line(surface, (40, 35, 55), (pad, dy), (pad + sep_w, dy))
                dy += 6
                if item_type == "equipment":
                    surface.blit(
                        font.render_text("Press [E] to equip", (100, 200, 100)),
                        (pad, dy),
                    )
                elif item_type == "consumable":
                    surface.blit(
                        font.render_text("Press [U] to use", (100, 180, 255)),
                        (pad, dy),
                    )
                elif item_type == "junk":
                    surface.blit(
                        font.render_text(f"Press [U] to sell ({gold_val}g)", get_rgb("yellow")),
                        (pad, dy),
                    )

        # Bottom: equipped gear summary
        eq_y = height - 50
        pygame.draw.line(surface, (40, 35, 55), (8, eq_y), (width - 8, eq_y))
        eq_y += 6
        if equipment:
            wpn = getattr(equipment, "weapon", None)
            arm = getattr(equipment, "armor", None)
            wpn_name = wpn.get("name", "None") if wpn else "None"
            arm_name = arm.get("name", "None") if arm else "None"
            surface.blit(
                font.render_text(f"Weapon: {wpn_name}", get_rgb("white")), (8, eq_y),
            )
            surface.blit(
                font.render_text(f"Armor: {arm_name}", get_rgb("white")),
                (width // 2, eq_y),
            )

        pygame.draw.rect(surface, get_rgb("bright_cyan"), surface.get_rect(), 1)
        return surface
