__all__ = [
    'Puzzle',
    'get_aoc_session',
    'register_aoc_session',
]


from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo
import colorful as cf
import logging
import os
import requests
import warnings


logging.basicConfig(format='[%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# Advent of Code begins at midnight EST
current_time = datetime.now(ZoneInfo('US/Eastern'))
aoc_url = 'https://adventofcode.com'
aoc_session_path = os.path.expanduser('~/.config/aoc/.aoc_session')

def get_aoc_session():
    try:
        with open(aoc_session_path, 'r') as f:
            return f.read().strip()
    except OSError:
        pass

    try:
        return os.environ['AOC_SESSION']
    except KeyError:
        raise KeyError('AOC_SESSION environment variable is not present on your system. Please'
                       f' either export one or save the session inside {aoc_session_path!r}.')

def register_aoc_session(session):
    magic_session_prefix = '53616c7465645f5f'
    if not session.startswith(magic_session_prefix):
        warnings.warn(f"Session token does not begin with '{magic_session_prefix}...',"
                      ' perhaps it is invalid?')

    os.makedirs(os.path.dirname(aoc_session_path), exist_ok=True)
    with open(aoc_session_path, 'w') as f:
        f.write(session)

def coerce(val):
    """Used internally by Puzzle.submit() to coerce non-str values upon submitting"""
    if isinstance(val, int):
        return str(val)
    if not isinstance(val, str):
        raise AOCError(f'Cannot coerce value of type {val.__class__}: {val}')
    return val


class AOCError(Exception):
    pass


class Puzzle:
    cached_input_template = 'input-%(year)04d-day%(day)02d.txt'
    part1_done_dir = '.finished-part1'

    def __init__(self, year=None, day=None, session=None,
                 cached_input_template=cached_input_template):
        # If no year/day is specified, assume the current time
        if year is None:
            year = current_time.year
        if day is None:
            day = current_time.day
        if session is None:
            session = get_aoc_session()

        if year < 2015 or year > current_time.year:
            raise ValueError(f'year must be between 2015 and {current_time.year}')
        if not 1 <= day <= 25:
            raise ValueError('day must be between 1 and 25')

        self.day = day
        self.year = year
        self.session = session
        self.cached_input_template = cached_input_template

        self.req_session = requests.Session()
        self.req_session.cookies['session'] = self.session
        self.req_session.headers['User-Agent'] = 'aoc-tools by hlyndon20@gmail.com'

    @property
    def data(self):
        mapping = {'year': self.year, 'day': self.day}
        cached_input_filename = self.cached_input_template % mapping
        try:
            # Attempt to read from the cached file first, to avoid extra requests
            with open(cached_input_filename, 'r') as f:
                data = f.read()
            is_cached = len(data) != 0
        except OSError:
            is_cached = False

        if not is_cached:
            aoc_input_url = f'{aoc_url}/{self.year}/day/{self.day}/input'
            resp = self.req_session.get(aoc_input_url)
            match resp.status_code:
                case 302:
                    raise AOCError(f'Your session token has likely expired.')
                case 404:
                    raise AOCError(f"Input data not found. Check if your day's puzzle is correct.")
                case 400:
                    raise AOCError('Failed to fetch input data. Perhaps your session token is invalid?')
                case code if code != 200:
                    raise AOCError(f'Failed to fetch input data (HTTP {resp.status_code}).')

            data = resp.text
            with open(cached_input_filename, 'w') as f:
                log.warning(f'Input for day {self.day} is not cached, saving data to {cached_input_filename!r}...')
                f.write(data)

        return data

    def submit(self, answer, part=None):
        if answer is None:
            exit()

        if part is None:
            part = 1 + os.path.isdir(self.part1_done_dir)

        if not 1 <= part <= 2:
            raise ValueError('part argument must either be 1 or 2')

        if answer in ('', b'', 'None', b'None'):
            raise AOCError(f'Cowardly refusing to submit non-answer: {answer!r}')
        answer = coerce(answer)

        prompt = input(cf.white(f'Are you sure you want to submit [y/N]: {answer}\n>>> '))
        if prompt != 'y':
            exit()

        aoc_submit_url = f'{aoc_url}/{self.year}/day/{self.day}/answer'
        data = {
            'level': part,
            'answer': answer,
        }
        resp = self.req_session.post(aoc_submit_url, data=data)
        soup = BeautifulSoup(resp.text, 'html.parser')
        message = soup.article.text

        if "That's the right answer" in message:
            print(cf.green(message))
            if not os.path.isdir(self.part1_done_dir):
                os.mkdir(self.part1_done_dir)
        elif "That's not the right answer" in message:
            print(cf.red(message))
        else:
            print(cf.yellow(message))
        exit()

    __call__ = submit