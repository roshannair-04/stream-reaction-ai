import cv2

from vision.providers.mediapipe_hands_provider import (
    MediaPipeHandsProvider,
)
from vision.events.gesture_detector import GestureDetector


def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    hands_provider = MediaPipeHandsProvider()
    detector = GestureDetector()

    print("👋 Wave Detector Test")
    print("Show an open hand.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = hands_provider.process(frame)

            detected = detector.detect_wave(
                result.hands
            )

            cv2.putText(
                frame,
                f"Open Hand: {detected}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(
                "Wave Detector Test",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        hands_provider.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()