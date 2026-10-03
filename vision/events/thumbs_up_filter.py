from vision.events.temporal_filter import TemporalGestureFilter


class ThumbsUpFilter:
    def __init__(
        self,
        confirm_frames: int = 6,
        release_frames: int = 6,
    ):
        self.filter = TemporalGestureFilter(
            confirm_frames=confirm_frames,
            release_frames=release_frames,
        )

    def update(self, detected: bool) -> bool:
        return self.filter.update(detected)