from pathlib import Path
import time

import cv2
import pygame

from reactions.reaction_registry import Reaction, get_reaction
from obs.obs_client import OBSClient


class ReactionEngine:
    def __init__(
        self,
        obs_client: OBSClient | None = None,
        obs_scene: str = "Scene",
        local_preview: bool = True,
    ) -> None:
        self.obs_client = obs_client
        self.obs_scene = obs_scene
        self.local_preview = local_preview

        self.current_reaction: Reaction | None = None
        self.reaction_started_at: float | None = None

        pygame.mixer.init()

    def trigger(self, event: str) -> None:
        reaction = get_reaction(event)

        if reaction is None:
            print(f"No reaction configured for event: {event}")
            return

        self.current_reaction = reaction
        self.reaction_started_at = time.time()

        print(f"🔥 REACTION: {reaction.event}")

        # -------------------------
        # OBS output
        # -------------------------
        if self.obs_client is not None:
            self.obs_client.set_source_visibility(
                self.obs_scene,
                "Prayer Reaction",
                True,
            )

        # -------------------------
        # Audio
        # -------------------------
        if reaction.audio_path:
            audio_path = Path(reaction.audio_path)

            print(f"   Audio: {audio_path}")

            if audio_path.exists():
                pygame.mixer.music.load(str(audio_path))
                pygame.mixer.music.set_volume(reaction.volume)
                pygame.mixer.music.play()
            else:
                print(f"Audio file not found: {audio_path}")

        # -------------------------
        # Local preview info
        # -------------------------
        if reaction.image_path:
            print(f"   Image: {reaction.image_path}")

    def show(self) -> None:
        if self.current_reaction is None:
            return

        if self.reaction_started_at is None:
            return

        elapsed = time.time() - self.reaction_started_at

        if elapsed >= self.current_reaction.duration:
            self.clear()
            return

        # Local OpenCV preview
        if not self.local_preview:
            return

        image_path = self.current_reaction.image_path

        if not image_path:
            return

        path = Path(image_path)

        if not path.exists():
            print(f"Reaction image not found: {path}")
            self.clear()
            return

        image = cv2.imread(str(path))

        if image is None:
            print(f"Could not load reaction image: {path}")
            self.clear()
            return

        cv2.imshow("Stream Reaction", image)

    def clear(self) -> None:
        # -------------------------
        # Stop audio
        # -------------------------
        pygame.mixer.music.stop()

        # -------------------------
        # Hide OBS source
        # -------------------------
        if self.obs_client is not None:
            self.obs_client.set_source_visibility(
                self.obs_scene,
                "Prayer Reaction",
                False,
            )

        # -------------------------
        # Reset reaction state
        # -------------------------
        self.current_reaction = None
        self.reaction_started_at = None

        if self.local_preview:
            cv2.destroyWindow("Stream Reaction")