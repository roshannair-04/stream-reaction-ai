import os
import time
import cv2
from dotenv import load_dotenv

from vision.providers.mediapipe_hands_provider import MediaPipeHandsProvider
from vision.events.gesture_detector import GestureDetector
from vision.events.wave_detector import WaveDetector
from vision.events.wave_filter import WaveFilter
from vision.events.event_engine import HandsTogetherEventEngine

from reactions.reaction_engine import ReactionEngine
from obs.obs_client import OBSClient


def main():
    load_dotenv()

    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    hands_provider = MediaPipeHandsProvider()
    detector = GestureDetector()
    wave_detector = WaveDetector()
    wave_filter = WaveFilter(release_frames=12)
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

    print("🎬 Wave Full Pipeline Test")
    print("Wave your open hand left and right.")
    print("Press Q to quit.")

    try:
        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = hands_provider.process(frame)

            open_hand = detector.detect_wave(result.hands)

            raw_wave = wave_detector.update(
                result.hands,
                open_hand,
            )

            stable_wave = wave_filter.update(raw_wave)

            event = event_engine.update_gesture(
                "wave",
                stable_wave,
            )

            if event:
                print(f"🎯 EVENT: {event}")

                reaction_engine.trigger(event)

            reaction_engine.show()

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

            cv2.imshow("Wave Full Pipeline", frame)

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