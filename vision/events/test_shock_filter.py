import cv2

from vision.providers.mediapipe_provider import MediaPipePoseProvider
from vision.events.shock_detector import ShockDetector
from vision.events.shock_filter import ShockFilter


def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    pose_provider = MediaPipePoseProvider()
    detector = ShockDetector()
    shock_filter = ShockFilter(
        confirm_frames=6,
        release_frames=8,
    )

    print("😱 Shock Filter Test")
    print("Put both hands on your head and hold.")
    print("Then remove them and wait for release.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = pose_provider.process(frame)

            raw_shock = detector.detect(result.landmarks)
            stable_shock = shock_filter.update(raw_shock)

            cv2.putText(
                frame,
                f"Raw Shock: {raw_shock}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Stable Shock: {stable_shock}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Shock Filter Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        pose_provider.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()