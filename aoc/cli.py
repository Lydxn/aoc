from aoc.api import AOCError, Puzzle, aoc_session_path, register_aoc_session
from argparse import ArgumentParser
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import colorful as cf
import os
import time

def run_session(args):
    session = args.token
    if session is None:
        session = input('Provide your AOC session token > ')
    if os.path.exists(aoc_session_path):
        confirmation_message = (
            f'The file {aoc_session_path!r} already exists.\n'
            'Are you sure you want to overwrite it with a new session? [y/N] '
        )
        prompt = input(confirmation_message)
        if prompt != 'y':
            return
    register_aoc_session(session)

template = r"""
from aoc import *

samples = [r'''

''']

samples = list(filter(None, map(str.strip, samples)))
day = template.exec({}, {}, samples=samples)
ans = None

_I: xstr = day.data.rstrip('\n')
_L = _I.lines

day(ans)
""".strip()

def run_template(args):
    year = int(args.year[0])
    day = int(args.day[0])
    filename = args.file

    with open(filename, 'w') as f:
        f.write(template.format(year, day))

def run_countdown(_):
    zone = ZoneInfo('US/Eastern')
    current_time = datetime.now(zone)
    start_time = current_time + timedelta(1)
    start_time = start_time.replace(
        hour=0, minute=0, second=0, microsecond=0)

    year, day = start_time.year, start_time.day
    print(cf.white(f'Counting down from Advent of Code {year}, Day {day}...'))

    record_interval = timedelta(seconds=1)
    last_recorded_time = current_time

    while True:
        if current_time - last_recorded_time >= record_interval:
            last_recorded_time = current_time
            time_left = start_time - current_time
            seconds = time_left.seconds
            hours, rem = divmod(seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            print(cf.white('%02d:%02d:%02d' % (hours, minutes, seconds)))

        if current_time > start_time or 1:
            # try grabbing input 3 times before giving up
            for _ in range(3):
                puzzle = Puzzle(year, day)
                try:
                    print(puzzle.data.rstrip('\n'))
                    break
                except AOCError as e:
                    print(cf.red(str(e)))
                    print(cf.red(f'Failed to fetch input, trying again...'))
                time.sleep(0.2)
            break

        current_time = datetime.now(zone)

def main():
    description = 'A command-line toolchain for competing in Advent of Code.'
    parser = ArgumentParser(description=description)
    subparsers = parser.add_subparsers(required=True)

    session_parser = subparsers.add_parser('session',
        help='save your session token to a config path')
    session_parser.add_argument('token', nargs='?', default=None,
        help='session token for authenticating with AoC')
    session_parser.set_defaults(func=run_session)

    template_parser = subparsers.add_parser('template',
        help='generate an AoC template')
    template_parser.add_argument('year', nargs=1)
    template_parser.add_argument('day', nargs=1)
    template_parser.add_argument('file', nargs='?', default='solve.py')
    template_parser.set_defaults(func=run_template)

    countdown_parser = subparsers.add_parser('countdown',
        help='countdown until day starts and dump the input')
    countdown_parser.set_defaults(func=run_countdown)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()