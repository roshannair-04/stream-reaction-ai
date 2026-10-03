from dataclasses import dataclass


@dataclass
class EventEngineConfig:
    cooldown_frames: int = 60


class HandsTogetherEventEngine:
    def __init__(self, config=None):
        self.config = config or EventEngineConfig()

        self.cooldown_remaining = 0
        self.active = False
        self.armed = True

    def update_gesture(
        self,
        gesture_name: str,
        stable_detected: bool,
    ) -> str | None:

        if self.cooldown_remaining > 0:
            self.cooldown_remaining -= 1

        # Gesture is currently being held
        if stable_detected:

            # Already fired for this gesture
            if not self.armed:
                return None

            # Fire once
            if self.cooldown_remaining == 0:
                self.active = True
                self.armed = False
                return gesture_name

            return None

        # Gesture has been released
        self.active = False

        # Re-arm only after release
        if self.cooldown_remaining == 0:
            self.armed = True

        return None

    def update(self, stable_prayer: bool) -> str | None:
        return self.update_gesture(
            "prayer",
            stable_prayer,
        )
