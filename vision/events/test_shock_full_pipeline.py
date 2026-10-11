import os
import cv2
from dotenv import load_dotenv

from vision.providers.mediapipe_provider import MediaPipePoseProvider
from vision.events.shock_detector import ShockDetector
from vision.events.shock_filter import ShockFilter
from vision.events.event_engine import HandsTogetherEventEngine

from reactions.reaction_engine import ReactionEngine
from obs.obs_client import OBSClient


def main():
    load_dotenv()

    camera = cv2.VideoCapture(1)

    if not camera.isOpened():
        raise RuntimeError("Could not open camera.")

    pose_provider = MediaPipePoseProvider()
    detector = ShockDetector()
    shock_filter = ShockFilter(
        confirm_frames=6,
        release_frames=8,
    )
    event_engine = HandsTogetherEventEngine()

    obs_client = OBSClient(
        host=os.getenv("OBS_HOST", "localhost"),
        port=int(os.getenv("OBS_PORT", "4455")),
        password=os.getenv("OBS_PASSWORD", ""),
    )

    reaction_engine = None

    try:
        obs_client.connect()

        reaction_engine = ReactionEngine(
            obs_client=obs_client,
            obs_scene="Scene",
            local_preview=False,
        )

        print("🎬 Shock Full Pipeline Test")
        print("Put both hands on your head and hold.")
        print("The Shock GIF and audio should trigger automatically.")
        print("Remove your hands to re-arm the detector.")
        print("Press Q to quit.")

        while True:
            ok, frame = camera.read()

            if not ok:
                print("Failed to read camera frame.")
                break

            result = pose_provider.process(frame)

            raw_shock = detector.detect(result.landmarks)
            stable_shock = shock_filter.update(raw_shock)

            event = event_engine.update_gesture(
                "shock",
                stable_shock,
            )

            if event:
                print(f"🎯 EVENT: {event}")
                reaction_engine.trigger(event)

            reaction_engine.show()

            cv2.putText(
                frame,
                f"Raw Shock: {raw_shock}",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            cv2.putText(
                frame,
                f"Stable Shock: {stable_shock}",
                (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            cv2.imshow("Shock Full Pipeline", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        if reaction_engine is not None:
            reaction_engine.clear()

        pose_provider.close()
        camera.release()
        cv2.destroyAllWindows()

        if obs_client.client is not None:
            obs_client.disconnect()


if __name__ == "__main__":
    main()
