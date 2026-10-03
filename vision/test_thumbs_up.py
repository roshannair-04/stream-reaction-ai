import cv2

from vision.providers.mediapipe_hands_provider import MediaPipeHandsProvider
from vision.events.gesture_detector import GestureDetector
from vision.events.thumbs_up_filter import ThumbsUpFilter


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

    print("👍 Thumbs Up Detector")
    print("Show a thumbs-up gesture.")
    print("Press Q to quit.")

    last_state = None

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = hands_provider.process(frame)

            raw_detected = detector.detect_thumbs_up(result.hands)
            detected = thumbs_up_filter.update(raw_detected)

            if detected != last_state:
                print(
                    f"👍 THUMBS UP STABLE: {detected} "
                    f"(raw={raw_detected})"
                )
                last_state = detected

            cv2.putText(
                frame,
                f"Thumbs Up: {detected}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Thumbs Up Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        hands_provider.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
