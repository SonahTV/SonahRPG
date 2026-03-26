"""Audio manager: background music, SFX, and voice narration."""

from __future__ import annotations

import os
import sys
import threading
from typing import Any

import pygame


def _assets_dir() -> str:
    """Resolve the sounds directory, works in dev and PyInstaller."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS  # type: ignore[attr-defined]
    else:
        base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, "assets", "sounds")


class SoundManager:
    """Handles background music, sound effects, and voice narration.

    Gracefully does nothing if audio initialization fails or files are missing.
    """

    def __init__(self) -> None:
        self._initialized = False
        self._music_volume = 0.4
        self._sfx_volume = 0.7
        self._voice_volume = 0.9
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self._assets_dir = _assets_dir()
        self._current_track: str = ""

        # Voice narration (pyttsx3)
        self._tts_engine: Any = None
        self._tts_thread: threading.Thread | None = None
        self._tts_speaking = False
        self._tts_available = False

    def init(self) -> None:
        """Initialize audio and TTS."""
        # Pygame mixer
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            self._initialized = True
        except Exception:
            self._initialized = False

        # Text-to-speech engine
        try:
            import pyttsx3

            self._tts_engine = pyttsx3.init()
            self._tts_engine.setProperty("rate", 145)  # Slightly slow for atmosphere
            self._tts_engine.setProperty("volume", self._voice_volume)
            # Try to find a deep/dramatic voice
            voices = self._tts_engine.getProperty("voices")
            for voice in voices:
                name_lower = voice.name.lower()
                # Prefer male voices for dark fantasy tone
                if "david" in name_lower or "mark" in name_lower or "male" in name_lower:
                    self._tts_engine.setProperty("voice", voice.id)
                    break
            self._tts_available = True
        except Exception:
            self._tts_available = False

    # -- Music -------------------------------------------------------------

    def play_music(self, track_name: str, loop: bool = True) -> None:
        """Play background music track. Skips if already playing this track."""
        if not self._initialized:
            return
        if track_name == self._current_track:
            return  # Already playing
        path = os.path.join(self._assets_dir, track_name)
        if not os.path.exists(path):
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self._current_track = track_name
        except Exception:
            pass

    def play_music_for_state(self, state_name: str) -> None:
        """Auto-select music based on game state."""
        track_map = {
            "MainMenuState": "menu_theme.wav",
            "ExplorationState": "exploration.wav",
            "CombatState": "combat.wav",
            "CinematicState": "cinematic.wav",
            "EndingState": "cinematic.wav",
            "GameOverState": "defeat.wav",
            "LevelUpState": "victory.wav",
            "ShopState": "exploration.wav",
            "DialogueState": "exploration.wav",
        }
        track = track_map.get(state_name)
        if track:
            loop = track not in ("victory.wav", "defeat.wav")
            self.play_music(track, loop=loop)

    def stop_music(self) -> None:
        """Stop background music."""
        if self._initialized:
            try:
                pygame.mixer.music.stop()
                self._current_track = ""
            except Exception:
                pass

    def fade_music(self, ms: int = 1000) -> None:
        """Fade out current music over given milliseconds."""
        if self._initialized:
            try:
                pygame.mixer.music.fadeout(ms)
                self._current_track = ""
            except Exception:
                pass

    # -- SFX ---------------------------------------------------------------

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

    # -- Voice Narration ---------------------------------------------------

    def speak(self, text: str) -> None:
        """Narrate text using TTS in a background thread.

        Non-blocking. If already speaking, the new text queues after.
        Strips Rich markup tags before speaking.
        """
        if not self._tts_available or not self._tts_engine:
            return

        # Strip Rich markup
        import re
        clean = re.sub(r"\[[^\]]*\]", "", text)
        clean = clean.strip()
        if not clean:
            return

        # Lower music while speaking
        if self._initialized:
            try:
                pygame.mixer.music.set_volume(self._music_volume * 0.3)
            except Exception:
                pass

        def _speak_thread():
            try:
                self._tts_speaking = True
                self._tts_engine.say(clean)
                self._tts_engine.runAndWait()
            except Exception:
                pass
            finally:
                self._tts_speaking = False
                # Restore music volume
                if self._initialized:
                    try:
                        pygame.mixer.music.set_volume(self._music_volume)
                    except Exception:
                        pass

        # Only start if not already speaking
        if not self._tts_speaking:
            self._tts_thread = threading.Thread(target=_speak_thread, daemon=True)
            self._tts_thread.start()

    def stop_speaking(self) -> None:
        """Stop any ongoing narration."""
        if self._tts_available and self._tts_engine and self._tts_speaking:
            try:
                self._tts_engine.stop()
            except Exception:
                pass
            self._tts_speaking = False

    @property
    def is_speaking(self) -> bool:
        return self._tts_speaking

    # -- Volume controls ---------------------------------------------------

    def set_music_volume(self, volume: float) -> None:
        self._music_volume = max(0.0, min(1.0, volume))
        if self._initialized:
            try:
                pygame.mixer.music.set_volume(self._music_volume)
            except Exception:
                pass

    def set_sfx_volume(self, volume: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, volume))

    def set_voice_volume(self, volume: float) -> None:
        self._voice_volume = max(0.0, min(1.0, volume))
        if self._tts_engine:
            try:
                self._tts_engine.setProperty("volume", self._voice_volume)
            except Exception:
                pass

    # -- Cleanup -----------------------------------------------------------

    def cleanup(self) -> None:
        """Clean up audio resources."""
        self.stop_speaking()
        if self._initialized:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
