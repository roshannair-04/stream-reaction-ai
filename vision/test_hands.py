import cv2
import mediapipe as mp

from providers.mediapipe_hands_provider import MediaPipeHandsProvider


mp_hands = mp.solutions.hands


def main() -> None:
    camera = cv2.VideoCapture(1) #1 instead of 0 as continuity cam is glitching for some reason
    provider = MediaPipeHandsProvider()

    if not camera.isOpened():
        print("Could not open camera")
        return

    print("Show your hands to the camera. Press Q to quit.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Could not read frame")
                break

            result = provider.process(frame)

            if result.detected:
                height, width = frame.shape[:2]

                for hand in result.hands:
                    points = []

                    for landmark in hand["landmarks"]:
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

                    for connection in mp_hands.HAND_CONNECTIONS:
                        start_idx, end_idx = connection

                        cv2.line(
                            frame,
                            points[start_idx],
                            points[end_idx],
                            (255, 100, 0),
                            2,
                        )

                    label = hand["label"]

                    cv2.putText(
                        frame,
                        label,
                        points[0],
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 255),
                        2,
                    )

                status = f"Hands detected: {len(result.hands)}"
            else:
                status = "Hands detected: 0"

            cv2.putText(
                frame,
                status,
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2,
            )

            cv2.imshow("MediaPipe Hands Test", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        provider.close()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
