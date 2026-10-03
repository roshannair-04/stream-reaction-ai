from math import hypot


class GestureDetector:
    LEFT_WRIST = 15
    RIGHT_WRIST = 16

    # MediaPipe hand landmark indices
    WRIST = 0

    THUMB_TIP = 4
    INDEX_TIP = 8
    MIDDLE_TIP = 12
    RING_TIP = 16
    PINKY_TIP = 20

    MCP_POINTS = [5, 9, 13, 17]

    FINGER_TIPS = [8, 12, 16, 20]

    PALM_POINTS = [0, 5, 9, 13, 17]

    # ---------------------------------------------------------
    # Existing pose-based detector
    # ---------------------------------------------------------

    def detect_hands_together(self, landmarks: list[dict]) -> bool:
        if len(landmarks) < 17:
            return False

        left_wrist = landmarks[self.LEFT_WRIST]
        right_wrist = landmarks[self.RIGHT_WRIST]

        if left_wrist["visibility"] < 0.5:
            return False

        if right_wrist["visibility"] < 0.5:
            return False

        distance = hypot(
            left_wrist["x"] - right_wrist["x"],
            left_wrist["y"] - right_wrist["y"],
        )

        return distance < 0.18

    # ---------------------------------------------------------
    # Basic geometry
    # ---------------------------------------------------------

    def _distance(self, a: dict, b: dict) -> float:
        return hypot(
            a["x"] - b["x"],
            a["y"] - b["y"],
        )

    def _palm_center(self, landmarks: list[dict]) -> tuple[float, float]:
        x = sum(
            landmarks[i]["x"]
            for i in self.PALM_POINTS
        ) / len(self.PALM_POINTS)

        y = sum(
            landmarks[i]["y"]
            for i in self.PALM_POINTS
        ) / len(self.PALM_POINTS)

        return x, y

    def _hand_scale(self, landmarks: list[dict]) -> float:
        """
        Estimate the size of the hand using
        wrist -> middle MCP.
        """

        return self._distance(
            landmarks[0],
            landmarks[9],
        )

    # ---------------------------------------------------------
    # Palm distance
    # ---------------------------------------------------------

    def palm_distance(self, hands: list[dict]) -> float | None:
        if len(hands) < 2:
            return None

        hand_a = hands[0]["landmarks"]
        hand_b = hands[1]["landmarks"]

        center_a = self._palm_center(hand_a)
        center_b = self._palm_center(hand_b)

        center_distance = hypot(
            center_a[0] - center_b[0],
            center_a[1] - center_b[1],
        )

        scale_a = self._hand_scale(hand_a)
        scale_b = self._hand_scale(hand_b)

        average_scale = (scale_a + scale_b) / 2

        if average_scale <= 0:
            return None

        return center_distance / average_scale

    # ---------------------------------------------------------
    # Wrist distance
    # ---------------------------------------------------------

    def wrist_distance(self, hands: list[dict]) -> float | None:
        if len(hands) < 2:
            return None

        hand_a = hands[0]["landmarks"]
        hand_b = hands[1]["landmarks"]

        distance = self._distance(
            hand_a[self.WRIST],
            hand_b[self.WRIST],
        )

        average_scale = (
            self._hand_scale(hand_a)
            + self._hand_scale(hand_b)
        ) / 2

        if average_scale <= 0:
            return None

        return distance / average_scale

    # ---------------------------------------------------------
    # Corresponding landmark alignment
    # ---------------------------------------------------------

    def landmark_alignment(self, hands: list[dict]) -> float | None:
        """
        Compare corresponding landmarks between both hands.

        Lower = hands are more geometrically aligned.
        """

        if len(hands) < 2:
            return None

        hand_a = hands[0]["landmarks"]
        hand_b = hands[1]["landmarks"]

        important_points = [
            0,   # wrist
            5,   # index MCP
            9,   # middle MCP
            13,  # ring MCP
            17,  # pinky MCP
            4,   # thumb tip
            8,   # index tip
            12,  # middle tip
            16,  # ring tip
            20,  # pinky tip
        ]

        distances = []

        for index in important_points:
            distances.append(
                self._distance(
                    hand_a[index],
                    hand_b[index],
                )
            )

        average_distance = sum(distances) / len(distances)

        average_scale = (
            self._hand_scale(hand_a)
            + self._hand_scale(hand_b)
        ) / 2

        if average_scale <= 0:
            return None

        return average_distance / average_scale

    # ---------------------------------------------------------
    # Finger alignment
    # ---------------------------------------------------------

    def finger_alignment(self, hands: list[dict]) -> float | None:
        """
        Specifically compare fingertip positions.

        Lower = fingertips are aligned.
        """

        if len(hands) < 2:
            return None

        hand_a = hands[0]["landmarks"]
        hand_b = hands[1]["landmarks"]

        distances = []

        for index in self.FINGER_TIPS:
            distances.append(
                self._distance(
                    hand_a[index],
                    hand_b[index],
                )
            )

        average_distance = sum(distances) / len(distances)

        average_scale = (
            self._hand_scale(hand_a)
            + self._hand_scale(hand_b)
        ) / 2

        if average_scale <= 0:
            return None

        return average_distance / average_scale

    def finger_extension_score(
        self,
        hands: list[dict],
    ) -> float | None:
        """
        Estimate how extended the fingers are.

        Higher = fingers are extended.
        Lower = fingers are curled/folded.
        """

        if len(hands) < 2:
            return None

        scores = []

        for hand in hands:
            landmarks = hand["landmarks"]

            # Finger chains:
            # MCP -> PIP -> DIP -> TIP
            fingers = [
                (5, 6, 7, 8),      # index
                (9, 10, 11, 12),   # middle
                (13, 14, 15, 16),  # ring
                (17, 18, 19, 20),  # pinky
            ]

            extended = 0

            for mcp, pip, dip, tip in fingers:
                mcp_to_tip = self._distance(
                    landmarks[mcp],
                    landmarks[tip],
                )

                mcp_to_pip = self._distance(
                    landmarks[mcp],
                    landmarks[pip],
                )

                # A reasonably extended finger should have
                # a substantially larger MCP→TIP distance.
                if mcp_to_tip > mcp_to_pip * 1.7:
                    extended += 1

            scores.append(extended / 4.0)

        return sum(scores) / len(scores)

    # ---------------------------------------------------------
    # Convert normalized distance → score
    # ---------------------------------------------------------

    def _proximity_score(
        self,
        distance: float | None,
        good: float,
        bad: float,
    ) -> float:

        if distance is None:
            return 0.0

        if distance <= good:
            return 1.0

        if distance >= bad:
            return 0.0

        return 1.0 - (
            (distance - good)
            / (bad - good)
        )

    # ---------------------------------------------------------
    # Prayer score
    # ---------------------------------------------------------

    def prayer_score(
        self,
        hands: list[dict],
    ) -> dict:

        if len(hands) < 2:
            return {
                "score": 0.0,
                "palm": None,
                "wrist": None,
                "alignment": None,
                "fingers": None,
                "extension": None,
            }

        palm = self.palm_distance(hands)
        wrist = self.wrist_distance(hands)
        alignment = self.landmark_alignment(hands)
        fingers = self.finger_alignment(hands)
        extension = self.finger_extension_score(hands)

        palm_score = self._proximity_score(
            palm,
            good=0.8,
            bad=2.0,
        )

        wrist_score = self._proximity_score(
            wrist,
            good=1.0,
            bad=2.5,
        )

        alignment_score = self._proximity_score(
            alignment,
            good=0.8,
            bad=2.0,
        )

        finger_score = self._proximity_score(
            fingers,
            good=0.8,
            bad=2.0,
        )

        # Weighted combination.
        #
        # Palm + landmark alignment are the strongest
        # signals. Wrist/finger alignment provide support.
        score = (
            palm_score * 0.30
            + alignment_score * 0.30
            + finger_score * 0.25
            + wrist_score * 0.15
        )

        return {
            "score": score,
            "palm": palm,
            "wrist": wrist,
            "alignment": alignment,
            "fingers": fingers,
            "extension": extension,
        }

    # ---------------------------------------------------------
    # Prayer detector
    # ---------------------------------------------------------

    def detect_prayer(
        self,
        hands: list[dict],
    ) -> bool:
        """
        Strict prayer detector.

        Requires:
        - two hands
        - close wrists
        - close palms
        """

        if len(hands) < 2:
            return False

        palm = self.palm_distance(hands)
        wrist = self.wrist_distance(hands)

        if palm is None or wrist is None:
            return False

        # These are normalized by hand size.
        #
        # We intentionally make this strict.
        # Temporal smoothing will happen later in the event engine.
        if wrist > 1.5:
            return False

        if palm > 1.4:
            return False

        return True
    # ---------------------------------------------------------
    # Single-finger state
    # ---------------------------------------------------------

    def _is_finger_extended(
        self,
        landmarks: list[dict],
        tip_index: int,
        pip_index: int,
    ) -> bool:
        """
        Check whether a finger is reasonably extended based on
        the fingertip being farther from the wrist than the PIP joint.
        """

        wrist = landmarks[self.WRIST]
        tip = landmarks[tip_index]
        pip = landmarks[pip_index]

        tip_distance = self._distance(wrist, tip)
        pip_distance = self._distance(wrist, pip)

        return tip_distance > pip_distance * 1.1

    def _is_finger_folded(
        self,
        landmarks: list[dict],
        tip_index: int,
        pip_index: int,
    ) -> bool:
        """
        Check whether a finger is reasonably folded.
        """

        wrist = landmarks[self.WRIST]
        tip = landmarks[tip_index]
        pip = landmarks[pip_index]

        tip_distance = self._distance(wrist, tip)
        pip_distance = self._distance(wrist, pip)

        return tip_distance < pip_distance * 1.15

    # ---------------------------------------------------------
    # Thumbs-up detector
    # ---------------------------------------------------------

    def detect_thumbs_up(
        self,
        hands: list[dict],
    ) -> bool:
        """
        Detect a thumbs-up gesture on any detected hand.

        Requires, on at least one hand:
        - thumb extended
        - thumb pointing up
        - index/middle/ring/pinky folded
        """

        if len(hands) == 0:
            return False

        for hand in hands:
            landmarks = hand["landmarks"]

            # Thumb should be extended.
            thumb_tip = landmarks[self.THUMB_TIP]
            thumb_mcp = landmarks[2]
            wrist = landmarks[self.WRIST]

            thumb_extended = (
                self._distance(wrist, thumb_tip)
                > self._distance(wrist, thumb_mcp) * 1.2
            )

            if not thumb_extended:
                continue

            # Thumb should point mostly upward (within ~45° of vertical),
            # so sideways thumbs with a slight upward tilt are rejected.
            # Image y grows downward, so "up" means negative dy.
            dx = thumb_tip["x"] - thumb_mcp["x"]
            dy = thumb_tip["y"] - thumb_mcp["y"]

            thumb_points_up = -dy > abs(dx)

            if not thumb_points_up:
                continue

            # Other four fingers should be folded.
            index_folded = self._is_finger_folded(landmarks, 8, 6)
            middle_folded = self._is_finger_folded(landmarks, 12, 10)
            ring_folded = self._is_finger_folded(landmarks, 16, 14)
            pinky_folded = self._is_finger_folded(landmarks, 20, 18)

            if (
                index_folded
                and middle_folded
                and ring_folded
                and pinky_folded
            ):
                return True

        return False
