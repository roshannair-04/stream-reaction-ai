import cv2

from vision.providers.mediapipe_hands_provider import (
    MediaPipeHandsProvider,
)
from vision.events.gesture_detector import GestureDetector
from vision.events.wave_detector import WaveDetector
from vision.events.wave_filter import WaveFilter
from vision.events.event_engine import HandsTogetherEventEngine


def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    hands_provider = MediaPipeHandsProvider()
    detector = GestureDetector()
    wave_detector = WaveDetector()
    wave_filter = WaveFilter(release_frames=12)
    event_engine = HandsTogetherEventEngine()

    print("👋 Wave Event Test")
    print("Wave your open hand left and right.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = hands_provider.process(frame)

            open_hand = detector.detect_wave(
                result.hands
            )

            raw_wave = wave_detector.update(
                result.hands,
                open_hand,
            )

            stable_wave = wave_filter.update(
                raw_wave
            )

            event = event_engine.update_gesture(
                "wave",
                stable_wave,
            )

            if event:
                print(f"🎯 EVENT: {event}")

            cv2.putText(
                frame,
                f"Open Hand: {open_hand}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Wave Event: {stable_wave}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(
                "Wave Event Test",
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