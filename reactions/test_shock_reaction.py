from dotenv import load_dotenv
import os
import time

from obs.obs_client import OBSClient
from reactions.reaction_engine import ReactionEngine

load_dotenv()

obs_client = OBSClient(
    host=os.getenv("OBS_HOST", "localhost"),
    port=int(os.getenv("OBS_PORT", "4455")),
    password=os.getenv("OBS_PASSWORD", ""),
)

try:
    obs_client.connect()

    engine = ReactionEngine(
        obs_client=obs_client,
        obs_scene="Scene",
        local_preview=False,
    )

    print("🔥 Triggering Shock reaction...")
    engine.trigger("shock")

    while engine.current_reaction is not None:
        engine.show()
        time.sleep(0.05)

    print("✅ Shock reaction finished.")

finally:
    obs_client.disconnect()
