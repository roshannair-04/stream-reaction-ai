from collections import deque


class TemporalGestureFilter:
    """
    Smooth a noisy boolean gesture signal over time.

    A gesture becomes active after enough positive frames.
    A gesture remains active through a small number of
    missed/negative frames.
    """

    def __init__(
        self,
        confirm_frames: int = 8,
        release_frames: int = 6,
    ) -> None:
        self.confirm_frames = confirm_frames
        self.release_frames = release_frames

        self.positive_frames = 0
        self.negative_frames = 0

        self.active = False

    def update(self, detected: bool) -> bool:
        if detected:
            self.positive_frames += 1
            self.negative_frames = 0

            if (
                not self.active
                and self.positive_frames >= self.confirm_frames
            ):
                self.active = True

        else:
            self.negative_frames += 1

            # IMPORTANT:
            # Don't immediately destroy our positive history.
            # A couple of bad MediaPipe frames are tolerated.
            if self.negative_frames >= self.release_frames:
                self.active = False
                self.positive_frames = 0
                self.negative_frames = 0

        return self.active