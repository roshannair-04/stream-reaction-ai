import os
import cv2
from dotenv import load_dotenv

from vision.providers.mediapipe_hands_provider import MediaPipeHandsProvider
from vision.events.gesture_detector import GestureDetector
from vision.events.thumbs_up_filter import ThumbsUpFilter
from vision.events.event_engine import HandsTogetherEventEngine

from obs.obs_client import OBSClient
from reactions.reaction_engine import ReactionEngine


def main():
    load_dotenv()

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

    obs_client = OBSClient(
        host=os.getenv("OBS_HOST", "localhost"),
        port=int(os.getenv("OBS_PORT", "4455")),
        password=os.getenv("OBS_PASSWORD", ""),
    )

    obs_client.connect()

    reaction_engine = ReactionEngine(
        obs_client=obs_client,
        obs_scene="Scene",
        local_preview=False,
    )

    print("👍 Thumbs Up Reaction Test")
    print("Show a thumbs-up to trigger the reaction.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = hands_provider.process(frame)

            raw_detected = detector.detect_thumbs_up(
                result.hands
            )

            stable_detected = thumbs_up_filter.update(
                raw_detected
            )

            event = event_engine.update_gesture(
                "thumbs_up",
                stable_detected,
            )

            if event:
                print(f"🎯 EVENT: {event}")
                reaction_engine.trigger(event)

            reaction_engine.show()

            cv2.putText(
                frame,
                f"Thumbs Up: {stable_detected}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow(
                "Thumbs Up Reaction Test",
                frame,
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        reaction_engine.clear()
        hands_provider.close()
        obs_client.disconnect()
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()