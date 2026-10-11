import cv2

from vision.providers.mediapipe_provider import MediaPipePoseProvider
from vision.events.shock_detector import ShockDetector


def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    pose_provider = MediaPipePoseProvider()
    detector = ShockDetector()

    print("😱 Shock Detector Test")
    print("Put both hands on your head.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = pose_provider.process(frame)

            shock = detector.detect(result.landmarks)

            cv2.putText(
                frame,
                f"Shock: {shock}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Shock Detector Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        pose_provider.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()