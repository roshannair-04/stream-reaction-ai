import time

from reactions.reaction_engine import ReactionEngine


def main():
    engine = ReactionEngine()

    print("Testing reaction engine.")
    print("Press Q in the reaction window to quit.")

    engine.trigger("prayer")

    while engine.current_reaction is not None:
        engine.show()

        key = __import__("cv2").waitKey(30) & 0xFF

        if key == ord("q"):
            break

        time.sleep(0.01)

    __import__("cv2").destroyAllWindows()

    print("Reaction finished.")


if __name__ == "__main__":
    main()