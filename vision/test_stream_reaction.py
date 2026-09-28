import os

import cv2
from dotenv import load_dotenv

from vision.providers.mediapipe_hands_provider import MediaPipeHandsProvider
from vision.events.gesture_detector import GestureDetector
from vision.events.temporal_filter import TemporalGestureFilter
from vision.events.event_engine import HandsTogetherEventEngine
from obs.obs_client import OBSClient

from reactions.reaction_engine import ReactionEngine

load_dotenv()
def main():
    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        print("❌ Could not open camera.")
        return

    hands_provider = MediaPipeHandsProvider()
    detector = GestureDetector()

    temporal_filter = TemporalGestureFilter(
        confirm_frames=8,
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

    print("🎥 Stream Reaction AI")
    print("🙏 Make the prayer gesture to trigger the reaction.")
    print("Press Q to quit.")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("❌ Failed to read camera frame.")
                break

            # -------------------------
            # 1. Hand detection
            # -------------------------
            hand_result = hands_provider.process(frame)

            # -------------------------
            # 2. Gesture detection
            # -------------------------
            prayer_detected = detector.detect_prayer(
                hand_result.hands
            )

            # -------------------------
            # 3. Temporal stabilization
            # -------------------------
            stable_prayer = temporal_filter.update(
                prayer_detected
            )

            # -------------------------
            # 4. Semantic event
            # -------------------------
            event = event_engine.update(
                stable_prayer
            )

            # -------------------------
            # 5. Reaction
            # -------------------------
            if event:
                print(f"🎯 EVENT: {event}")

                reaction_engine.trigger(event)

            # -------------------------
            # 6. Show camera
            # -------------------------
            status = "PRAYER DETECTED" if stable_prayer else "Waiting..."

            cv2.putText(
                frame,
                status,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Stream Reaction Camera", frame)

            # Keep reaction alive
            reaction_engine.show()

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break

    finally:
        camera.release()
        hands_provider.close()

        cv2.destroyAllWindows()
        obs_client.disconnect()


if __name__ == "__main__":
    main()