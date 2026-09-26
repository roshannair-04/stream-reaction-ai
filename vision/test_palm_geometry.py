import cv2

from events.event_engine import HandsTogetherEventEngine
from events.temporal_filter import TemporalGestureFilter
from providers.mediapipe_hands_provider import MediaPipeHandsProvider
from events.gesture_detector import GestureDetector


def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        print("Could not open camera.")
        return

    hands_provider = MediaPipeHandsProvider()
    detector = GestureDetector()
    gesture_filter = TemporalGestureFilter(
        confirm_frames=8,
        release_frames=6,
    )
    event_engine = HandsTogetherEventEngine()

    print("Prayer gesture diagnostic")
    print()
    print("Try:")
    print("  1. Hands apart")
    print("  2. Hands side-by-side")
    print("  3. Palms touching")
    print("  4. Hands crossed")
    print()
    print("Press Q to quit.")

    while True:
        success, frame = camera.read()

        if not success:
            print("Could not read frame.")
            break

        result = hands_provider.process(frame)

        prayer = detector.prayer_score(result.hands)

        # -------------------------------------------------
        # Draw landmarks
        # -------------------------------------------------

        if result.detected:
            for hand in result.hands:
                for landmark in hand["landmarks"]:
                    x = int(
                        landmark["x"]
                        * frame.shape[1]
                    )

                    y = int(
                        landmark["y"]
                        * frame.shape[0]
                    )

                    cv2.circle(
                        frame,
                        (x, y),
                        3,
                        (0, 255, 0),
                        -1,
                    )

        # -------------------------------------------------
        # Values
        # -------------------------------------------------

        is_prayer = detector.detect_prayer(result.hands)
        stable_prayer = gesture_filter.update(is_prayer)

        event_name = event_engine.update(stable_prayer)

        state = (
            "PRAYER"
            if stable_prayer
            else "NOT PRAYER"
        )

        if event_name:
            print(f"🎯 EVENT: {event_name}")

        def fmt(value):
            if value is None:
                return "--"

            return f"{value:.2f}"

        # -------------------------------------------------
        # Overlay
        # -------------------------------------------------

        cv2.putText(
            frame,
            f"Hands: {len(result.hands)}",
            (20, 35),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Score: {prayer['score']:.2f}",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Palm: {fmt(prayer['palm'])}",
            (20, 105),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Wrist: {fmt(prayer['wrist'])}",
            (20, 135),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Alignment: {fmt(prayer['alignment'])}",
            (20, 165),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Fingers: {fmt(prayer['fingers'])}",
            (20, 195),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"Extension: {fmt(prayer['extension'])}",
            (20, 225),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            state,
            (20, 245),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (0, 255, 0) if state == "PRAYER"
            else (0, 0, 255),
            3,
        )

        if event_name:
            cv2.putText(
                frame,
                f"EVENT: {event_name}",
                (20, 285),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 255),
                3,
            )

        cv2.imshow(
            "Prayer Gesture Diagnostic",
            frame,
        )

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    hands_provider.close()
    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()