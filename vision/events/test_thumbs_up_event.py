import cv2

from vision.providers.mediapipe_hands_provider import MediaPipeHandsProvider
from vision.events.gesture_detector import GestureDetector
from vision.events.thumbs_up_filter import ThumbsUpFilter
from vision.events.event_engine import HandsTogetherEventEngine


def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    hands_provider = MediaPipeHandsProvider()
    detector = GestureDetector()
    thumbs_up_filter = ThumbsUpFilter(
        confirm_frames=6,
        release_frames=6,
    )
    event_engine = HandsTogetherEventEngine()

    print("👍 Thumbs Up Event Test")
    print("Show a thumbs-up gesture.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = hands_provider.process(frame)

            raw_detected = detector.detect_thumbs_up(result.hands)
            stable_detected = thumbs_up_filter.update(raw_detected)

            event = event_engine.update_gesture(
                "thumbs_up",
                stable_detected,
            )

            if event:
                print(f"🎯 EVENT: {event}")

            cv2.putText(
                frame,
                f"Thumbs Up: {stable_detected}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Thumbs Up Event Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        hands_provider.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()