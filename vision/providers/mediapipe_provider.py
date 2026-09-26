from dataclasses import dataclass

import cv2
import mediapipe as mp


@dataclass
class PoseResult:
    landmarks: list[dict]
    detected: bool


class MediaPipePoseProvider:
    def __init__(self) -> None:
        self.pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=0,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )

    def process(self, frame) -> PoseResult:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.pose.process(rgb_frame)

        if not result.pose_landmarks:
            return PoseResult(
                landmarks=[],
                detected=False,
            )

        landmarks = [
            {
                "x": landmark.x,
                "y": landmark.y,
                "z": landmark.z,
                "visibility": landmark.visibility,
            }
            for landmark in result.pose_landmarks.landmark
        ]

        return PoseResult(
            landmarks=landmarks,
            detected=True,
        )

    def close(self) -> None:
        self.pose.close()
