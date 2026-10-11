from math import hypot


class ShockDetector:
    """
    Detect a hands-on-head shock pose.

    Both wrists must be sufficiently close to the head region.
    """

    NOSE = 0
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_EAR = 7
    RIGHT_EAR = 8

    def _distance(self, a, b):
        return hypot(
            a["x"] - b["x"],
            a["y"] - b["y"],
        )

    def _head_center(self, landmarks):
        nose = landmarks[self.NOSE]
        left_ear = landmarks[self.LEFT_EAR]
        right_ear = landmarks[self.RIGHT_EAR]

        return {
            "x": (nose["x"] + left_ear["x"] + right_ear["x"]) / 3,
            "y": (nose["y"] + left_ear["y"] + right_ear["y"]) / 3,
        }

    def _head_scale(self, landmarks):
        return self._distance(
            landmarks[self.LEFT_EAR],
            landmarks[self.RIGHT_EAR],
        )

    def detect(self, pose_landmarks):
        if not pose_landmarks:
            return False

        head = self._head_center(pose_landmarks)
        scale = self._head_scale(pose_landmarks)

        if scale <= 0:
            return False

        left_wrist = pose_landmarks[self.LEFT_WRIST]
        right_wrist = pose_landmarks[self.RIGHT_WRIST]

        left_distance = self._distance(left_wrist, head)
        right_distance = self._distance(right_wrist, head)

        # Normalize by head width so this works at different distances.
        left_ratio = left_distance / scale
        right_ratio = right_distance / scale

        return (
            left_ratio < 1.8
            and right_ratio < 1.8
        )