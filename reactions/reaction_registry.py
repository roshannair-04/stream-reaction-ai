from dataclasses import dataclass


@dataclass
class Reaction:
    event: str
    image_path: str | None = None
    audio_path: str | None = None
    duration: float = 3.0
    volume: float = 1.0
    enabled: bool = True


REACTIONS = {
    "prayer": Reaction(
        event="prayer",
        image_path="reactions/assets/prayer.png",
        audio_path="reactions/assets/prayer.mp3",
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