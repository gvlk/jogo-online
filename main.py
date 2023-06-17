WIDTH = 800
HEIGHT = int((WIDTH * (9 / 16)))

if __name__ == "__main__":
    from controller import GameController

    GameController(WIDTH, HEIGHT)
