import cv2
import mediapipe as mp

from providers.mediapipe_provider import MediaPipePoseProvider
from events.gesture_detector import GestureDetector
from events.event_engine import HandsTogetherEventEngine

mp_pose = mp.solutions.pose


def main() -> None:
    camera = cv2.VideoCapture(1)
    provider = MediaPipePoseProvider()
    detector = GestureDetector()
    event_engine = HandsTogetherEventEngine()

    if not camera.isOpened():
        print("Could not open camera")
        return

    print("Bring your hands together and press Q to quit")
    
    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read frame")
                break

            result = provider.process(frame)

            hands_together = False
            event_name = None

            if result.detected:
                hands_together = detector.detect_hands_together(
                    result.landmarks
                )
                event_name = event_engine.update(hands_together)

                height, width = frame.shape[:2]
                points = []

                for landmark in result.landmarks:
                    x = int(landmark["x"] * width)
                    y = int(landmark["y"] * height)
                    points.append((x, y))

                    cv2.circle(
                        frame,
                        (x, y),
                        4,
                        (0, 255, 0),
                        -1,
                    )

                for connection in mp_pose.POSE_CONNECTIONS:
                    start_idx, end_idx = connection

                    if start_idx < len(points) and end_idx < len(points):
                        cv2.line(
                            frame,
                            points[start_idx],
                            points[end_idx],
                            (255, 100, 0),
                            2,
                        )

            status = (
                    f"Raw: {'TRUE' if hands_together else 'FALSE'} | "
                    f"Event: {event_name or 'None'}"
                    )

            cv2.putText(
                frame,
                status,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0) if hands_together else (0, 0, 255),
                2,
            )

            cv2.imshow("Gesture Detection Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        provider.close()
        camera.release()
        cv2.destroyAllWindows()
        


if __name__ == "__main__":
    main()
