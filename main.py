# https://github.com/gvlk
# leia o README.md

from settings import *
from argparse import ArgumentParser
from logging import disable, INFO
from common.modules.logger import MyLogger

try:
    from os import path, remove

    filename = "log.log"
    if path.exists(filename):
        remove(filename)
except PermissionError:
    pass


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument('-s', '--server', action='store_true', help='Start server')
    parser.add_argument('-l', '--log-file', action='store_true', help='Log information')
    args = parser.parse_args()

    logger = MyLogger(__name__)
    if not args.log_file:
        disable(INFO)

    if args.server:
        from server.servercontroller import ServerController

        server = ServerController(SERVER_IP, SERVER_TCPPORT, logger.logger)
        server.run_server()

    else:
        from client.gamecontroller import GameController

        game = GameController(WIDTH, HEIGHT, SERVER_IP, SERVER_TCPPORT, logger.logger)
        game.run_game()


if __name__ == "__main__":
    main()
