"""Optional sound effects and music manager using Pygame mixer."""

from __future__ import annotations
import os
import pygame


class SoundManager:
    """Handles background music and sound effects.

    Gracefully does nothing if audio initialization fails or files are missing.
    """

    def __init__(self) -> None:
        self._initialized = False
        self._music_volume = 0.5
        self._sfx_volume = 0.7
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self._assets_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "assets", "sounds"
        )

    def init(self) -> None:
        """Initialize the audio system."""
        try:
            pygame.mixer.init()
            self._initialized = True
        except Exception:
            self._initialized = False

    def play_music(self, track_name: str, loop: bool = True) -> None:
        """Play background music track."""
        if not self._initialized:
            return
        path = os.path.join(self._assets_dir, track_name)
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception:
            pass

    def stop_music(self) -> None:
        """Stop background music."""
        if self._initialized:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass

    def play_sfx(self, sfx_name: str) -> None:
        """Play a sound effect."""
        if not self._initialized:
            return
        if sfx_name not in self._sfx_cache:
            path = os.path.join(self._assets_dir, sfx_name)
            if not os.path.exists(path):
                return
            try:
                self._sfx_cache[sfx_name] = pygame.mixer.Sound(path)
            except Exception:
                return
        try:
            sound = self._sfx_cache[sfx_name]
            sound.set_volume(self._sfx_volume)
            sound.play()
        except Exception:
            pass

    def set_music_volume(self, volume: float) -> None:
        self._music_volume = max(0.0, min(1.0, volume))
        if self._initialized:
            pygame.mixer.music.set_volume(self._music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, volume))

    def cleanup(self) -> None:
        """Clean up audio resources."""
        if self._initialized:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
