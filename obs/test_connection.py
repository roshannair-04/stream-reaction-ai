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

        scenes = client.get_scene_list()

        print("\n🎬 OBS Scenes:")

        for scene in scenes.scenes:
            print(f"  • {scene['sceneName']}")

    finally:
        client.disconnect()


if __name__ == "__main__":
    main()
