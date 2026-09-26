from dataclasses import dataclass

import cv2
import mediapipe as mp


@dataclass
class HandResult:
    hands: list[dict]
    detected: bool


class MediaPipeHandsProvider:
    def __init__(self) -> None:
        self.hands_model = mp.solutions.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame) -> HandResult:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.hands_model.process(rgb_frame)

        if not result.multi_hand_landmarks:
            return HandResult(
                hands=[],
                detected=False,
            )

        detected_hands = []

        for hand_landmarks, handedness in zip(
            result.multi_hand_landmarks,
            result.multi_handedness,
        ):
            landmarks = [
                {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                }
                for landmark in hand_landmarks.landmark
            ]

            detected_hands.append(
                {
                    "label": handedness.classification[0].label,
                    "landmarks": landmarks,
                }
            )

        return HandResult(
            hands=detected_hands,
            detected=True,
        )

    def close(self) -> None:
        self.hands_model.close()
