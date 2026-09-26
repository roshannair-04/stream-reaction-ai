from dataclasses import dataclass


@dataclass
class EventEngineConfig:
    cooldown_frames: int = 60


class HandsTogetherEventEngine:
    """
    Converts a stable gesture state into a one-shot event.

    The temporal filter is responsible for deciding whether
    the gesture is stable.

    This layer is responsible for:
    - firing only once when the gesture becomes active
    - preventing repeated events
    - waiting for the gesture to be released
    - applying cooldown
    """

    def __init__(
        self,
        config: EventEngineConfig | None = None,
    ) -> None:
        self.config = config or EventEngineConfig()

        self.cooldown_remaining = 0
        self.active = False

    def update(self, stable_prayer: bool) -> str | None:
        """
        Process a stable gesture state.

        Returns:
            'prayer' when a new prayer event occurs.
            None otherwise.
        """

        # -----------------------------------------
        # Cooldown
        # -----------------------------------------

        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1

        # -----------------------------------------
        # Gesture is active
        # -----------------------------------------

        if stable_prayer:

            # Already active.
            # Do not fire another event.
            if self.active:
                return None

            # New gesture + cooldown finished.
            if self.cooldown_remaining == 0:
                self.active = True
                self.cooldown_remaining = (
                    self.config.cooldown_frames
                )

                return "prayer"

        # -----------------------------------------
        # Gesture released
        # -----------------------------------------

        else:
            self.active = False

        return None