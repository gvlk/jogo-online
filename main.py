from argparse import ArgumentParser

SERVER_IP = "fe80::9c48:7cda:800:9f84%4"
SERVER_PORT = 5000
WIDTH = 800
HEIGHT = int((WIDTH * (9 / 16)))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-s', '--server', action='store_true')
    args = parser.parse_args()

    if args.server:
        from server.servercontroller import ServerController

        server = ServerController(SERVER_IP, SERVER_PORT)
        server.run_server()

    else:
        from client.gamecontroller import GameController

        game = GameController(WIDTH, HEIGHT)
        game.run_game()







