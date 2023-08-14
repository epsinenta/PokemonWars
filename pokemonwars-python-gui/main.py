import argparse
import asyncio
from functools import partial

import aiorun

import settings
from classes.game_context import GameContext
from elements.login import Login
from elements.transcation_pending_overlay import TransactionPendingOverlay


async def main():
    parser = argparse.ArgumentParser(description='Pokemon_Wars')
    parser.add_argument("-d", "--debug",
                        help='Logs some useful information',    action="store_true")
    args = parser.parse_args()
    if args.debug:
        settings.DEBUG = True
        print("Debug on")
        print("Какой дебаг? Багов не бывает.")
    await GameContext(partial(TransactionPendingOverlay, Login)).run()
    asyncio.get_event_loop().stop()


if __name__ == '__main__':
    aiorun.run(main(), stop_on_unhandled_errors=True)
