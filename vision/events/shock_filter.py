from vision.events.temporal_filter import TemporalGestureFilter


class ShockFilter:
    def __init__(self, confirm_frames=6, release_frames=8):
        self.filter = TemporalGestureFilter(
            confirm_frames=confirm_frames,
            release_frames=release_frames,
        )

    def update(self, detected):
        return self.filter.update(detected)