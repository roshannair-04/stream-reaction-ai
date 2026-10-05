class WaveFilter:
    def __init__(self, release_frames: int = 12):
        self.release_frames = release_frames

        self.active = False
        self.negative_frames = 0

    def update(self, detected: bool) -> bool:
        # Wave detected.
        if detected:
            self.negative_frames = 0

            # Already fired for this continuous wave.
            if self.active:
                return False

            # Fire once and lock.
            self.active = True
            return True

        # No wave detected.
        if self.active:
            self.negative_frames += 1

            # Re-arm only after enough quiet frames.
            if self.negative_frames >= self.release_frames:
                self.active = False
                self.negative_frames = 0

        return False