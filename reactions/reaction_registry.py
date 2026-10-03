from dataclasses import dataclass


@dataclass
class Reaction:
    event: str
    image_path: str | None = None
    audio_path: str | None = None

    image_source: str = "Prayer Reaction"
    audio_source: str = "Reaction Audio"

    duration: float = 3.0
    volume: float = 1.0
    enabled: bool = True


REACTIONS = {
    "prayer": Reaction(
        event="prayer",
        image_path="reactions/assets/prayer.png",
        audio_path="reactions/assets/prayer.mp3",
        image_source="Prayer Reaction",
        audio_source="Reaction Audio",
        duration=3.0,
        volume=1.0,
    ),

    "thumbs_up": Reaction(
    event="thumbs_up",
    image_path="reactions/assets/thumbs_up.jpg",
    audio_path="reactions/assets/thumbs_up.mp3",
    image_source="Thumbs Up Reaction",
    audio_source="Thumbs Up Audio",
    duration=3.0,
    volume=1.0,
),
}


def get_reaction(event: str) -> Reaction | None:
    reaction = REACTIONS.get(event)

    if reaction is None:
        return None

    if not reaction.enabled:
        return None

    return reaction
