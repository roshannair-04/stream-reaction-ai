import os
from dotenv import load_dotenv

from reactions.reaction_engine import ReactionEngine

from obs.obs_client import OBSClient


def main():
    load_dotenv()
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

    print("👋 Wave Reaction Test")
    print("Triggering wave reaction...")

    reaction_engine.trigger("wave")

    try:
        import time

        start = time.time()

        while time.time() - start < 5.5:
            reaction_engine.show()
            time.sleep(0.05)

    finally:
        reaction_engine.clear()
        obs_client.disconnect()


if __name__ == "__main__":
    main()