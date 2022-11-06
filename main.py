import argparse
import asyncio

from worker import Worker


async def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("userid", help="user id")
    arg_parser.add_argument("password", help="password")
    arg_parser.add_argument("-i", "--ip", help="ip address for 'X-Forwarded-For' header")
    arg_parser.add_argument("--no-error", help="If true, print error message and exit with code 0 when error occurs. "
                                               "If you don't want to be disturbed by Github's email, "
                                               "set it to True.", action="store_true")
    arg_parser.add_argument("--use-webvpn", help="If true, will use webvpn to bypass ip restriction.",
                            action="store_true")
    arg_parser.add_argument("--debug", help="If true, will print debug message. Don't use it in public repository.",
                            action="store_true")

    worker = Worker(**vars(arg_parser.parse_args()))
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
