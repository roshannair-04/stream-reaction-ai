import os
import time

from dotenv import load_dotenv

from obs.obs_client import OBSClient


load_dotenv()


def main():
    client = OBSClient(
    host=os.getenv("OBS_HOST", "localhost"),
    port=int(os.getenv("OBS_PORT", "4455")),
    password=os.getenv("OBS_PASSWORD", ""),
)
    try:
        client.connect()

        scene_name = "Scene"
        source_name = "Prayer Reaction"

        print("🙈 Hiding reaction...")
        client.set_source_visibility(
            scene_name,
            source_name,
            False,
        )

        time.sleep(1)

        print("👀 Showing reaction...")
        client.set_source_visibility(
            scene_name,
            source_name,
            True,
        )

        time.sleep(3)

        print("🙈 Hiding reaction...")
        client.set_source_visibility(
            scene_name,
            source_name,
            False,
        )

        print("✅ OBS source test complete.")

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()