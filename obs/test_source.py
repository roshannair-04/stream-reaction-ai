import os

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

        print("🎵 Playing Reaction Audio...")
        client.play_media_source(
            scene_name="Scene",
            source_name="Reaction Audio",
        )

        print("✅ OBS audio test complete.")

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()