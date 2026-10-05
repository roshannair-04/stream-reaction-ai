from collections import deque


class WaveDetector:
    def __init__(
        self,
        window_size: int = 12,
        min_displacement: float = 0.12,
        min_direction_changes: int = 2,
    ):
        self.positions = deque(maxlen=window_size)
        self.min_displacement = min_displacement
        self.min_direction_changes = min_direction_changes

    def reset(self):
        self.positions.clear()

    def update(self, hands, open_hand: bool) -> bool:
        if not hands or not open_hand:
            self.reset()
            return False

        # Use the first detected hand.
        landmarks = hands[0]["landmarks"]

        # Wrist position.
        x = landmarks[0]["x"]

        self.positions.append(x)

        if len(self.positions) < self.positions.maxlen:
            return False

        # Calculate movement between consecutive positions.
        deltas = []

        for i in range(1, len(self.positions)):
            delta = self.positions[i] - self.positions[i - 1]

            if abs(delta) > 0.01:
                deltas.append(delta)

        if len(deltas) < 3:
            return False

        # Count direction changes.
        direction_changes = 0

        previous_direction = 0

        for delta in deltas:
            direction = 1 if delta > 0 else -1

            if (
                previous_direction != 0
                and direction != previous_direction
            ):
                direction_changes += 1

            previous_direction = direction

        # Total horizontal displacement.
        total_range = (
            max(self.positions)
            - min(self.positions)
        )

        if (
            total_range >= self.min_displacement
            and direction_changes >= self.min_direction_changes
        ):
            self.reset()
            return True

        return False