from argparse import ArgumentParser

try:
    from os import path, remove
    filename = "log.log"
    if path.exists(filename):
        remove(filename)
except PermissionError:
    pass

SERVER_IP = "fe80::9c48:7cda:800:9f84%4"
SERVER_TCPPORT = 5000
WIDTH = 1200
HEIGHT = int((WIDTH * (9 / 16)))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-s', '--server', action='store_true')
    args = parser.parse_args()

    if args.server:
        from server.servercontroller import ServerController

        server = ServerController(SERVER_IP, SERVER_TCPPORT)
        server.run_server()

    else:
        from client.gamecontroller import GameController

        game = GameController(WIDTH, HEIGHT, SERVER_IP, SERVER_TCPPORT)
        game.run_game()
