"""Screen layout manager for Pygame rendering."""

import pygame
from pygame_ui.font_manager import FontManager


class PygameRenderer:
    """Manages screen regions and composition.

    Layout matches the Rich terminal layout:
    ┌──────────────────────────────┬──────────────┐
    │         MAP VIEW             │  STATS       │
    │    (75% width)               │  MINIMAP     │
    │                              │  (25% width) │
    ├──────────────────────────────┴──────────────┤
    │  LOG (height ~130px)                        │
    ├─────────────────────────────────────────────┤
    │  HOTBAR (height ~48px)                      │
    └─────────────────────────────────────────────┘
    """

    def __init__(self, screen_width: int = 1280, screen_height: int = 720):
        self.screen_width = screen_width
        self.screen_height = screen_height

        # Calculate regions
        self.hotbar_height = 48
        self.log_height = 130
        self.sidebar_width = screen_width // 4  # 25%
        self.map_width = screen_width - self.sidebar_width
        self.main_height = screen_height - self.log_height - self.hotbar_height

        # Region rects
        self.map_rect = pygame.Rect(0, 0, self.map_width, self.main_height)
        self.stats_rect = pygame.Rect(self.map_width, 0, self.sidebar_width, self.main_height * 2 // 3)
        self.minimap_rect = pygame.Rect(self.map_width, self.main_height * 2 // 3, self.sidebar_width, self.main_height // 3)
        self.log_rect = pygame.Rect(0, self.main_height, screen_width, self.log_height)
        self.hotbar_rect = pygame.Rect(0, self.main_height + self.log_height, screen_width, self.hotbar_height)

    def draw_exploration_layout(self, screen, map_surface, stats_surface, minimap_surface, log_surface, hotbar_surface):
        """Composite all panels onto the screen."""
        screen.fill((0, 0, 0))
        # Blit each surface into its region, scaling if needed
        self._blit_scaled(screen, map_surface, self.map_rect)
        self._blit_scaled(screen, stats_surface, self.stats_rect)
        self._blit_scaled(screen, minimap_surface, self.minimap_rect)
        self._blit_scaled(screen, log_surface, self.log_rect)
        self._blit_scaled(screen, hotbar_surface, self.hotbar_rect)
        # Draw region borders
        for rect in [self.map_rect, self.stats_rect, self.minimap_rect, self.log_rect, self.hotbar_rect]:
            pygame.draw.rect(screen, (60, 60, 60), rect, 1)

    def draw_combat_layout(self, screen, combat_surface, stats_surface, log_surface, hotbar_surface):
        """Combat layout — combat panel replaces map+minimap."""
        screen.fill((0, 0, 0))
        combat_rect = pygame.Rect(0, 0, self.map_width, self.main_height)
        stats_rect = pygame.Rect(self.map_width, 0, self.sidebar_width, self.main_height)
        self._blit_scaled(screen, combat_surface, combat_rect)
        self._blit_scaled(screen, stats_surface, stats_rect)
        self._blit_scaled(screen, log_surface, self.log_rect)
        self._blit_scaled(screen, hotbar_surface, self.hotbar_rect)
        for rect in [combat_rect, stats_rect, self.log_rect, self.hotbar_rect]:
            pygame.draw.rect(screen, (60, 60, 60), rect, 1)

    def draw_fullscreen_layout(self, screen, content_surface, hotbar_surface=None):
        """Fullscreen layout for menus, cinematics."""
        screen.fill((0, 0, 0))
        content_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height - (self.hotbar_height if hotbar_surface else 0))
        self._blit_scaled(screen, content_surface, content_rect)
        if hotbar_surface:
            self._blit_scaled(screen, hotbar_surface, self.hotbar_rect)

    def _blit_scaled(self, screen, surface, rect):
        """Blit a surface into a rect, scaling if sizes don't match."""
        if surface is None:
            return
        if surface.get_size() != (rect.width, rect.height):
            # Clip instead of scale for pixel-perfect text
            screen.blit(surface, rect.topleft, area=pygame.Rect(0, 0, rect.width, rect.height))
        else:
            screen.blit(surface, rect.topleft)
