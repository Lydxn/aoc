from bisect import bisect_left, bisect_right
from collections import *
from functools import *
from heapq import *
from itertools import *
from parse import parse, search
from copy import deepcopy
from math import prod


D4 = [(1, 0), (0, 1), (-1, 0), (0, -1)]
D8 = [(1, 1), (1, 0), (1, -1), (0, -1), (0, 1), (-1, -1), (-1, 0), (-1, 1)]

LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
VOWELS = 'aeiou'
CONSONANTS = 'bcdfghjklmnpqrstvwxyz'

E = enumerate
P = print

def adj(iterable, size=2):
    """Returns a list of adjacent pairs (size=3 for triplets, and etc.)."""
    return comb(iterable, size, 1)

def comb(iterable, size=1, step=None, partial=False):
    """Split an iterable into chunks of a specified size/step."""
    if size <= 0:
        raise ValueError('size argument must be positive')
    if step is None or step == 0:
        step = size
    if step < 0:
        raise ValueError('step argument must be nonnegative')
    if not isinstance(iterable, str):
        iterable = tuple(iterable)
    result = []
    high = len(iterable)
    if not partial:
        high -= size - 1
    for i in range(0, high, step):
        result.append(iterable[i:i+size])
    return result

def eye(n):
    """Returns the n x n identity matrix."""
    return [[0] * i + [1] + [0] * (n - i - 1) for i in range(n)]

def fill(dims, k=0):
    """Returns an n-dimensional array filled with k (or 0s by default)."""
    if len(dims) == 1:
        return [k] * dims[0]
    elif len(dims) == 2:
        return [[k] * dims[1] for _ in range(dims[0])]
    else:
        return [fill(dims[1:]) for _ in range(dims[0])]

def flat(L):
    """Flattens a list recursively"""
    if not hasattr(L, '__iter__'):
        return [L]
    else:
        return list(chain(*map(flat, L)))

def rot(grid, n=1):
    """Rotates a grid 90 degrees clockwise n times"""
    match n & 3:
        case 0:
            return grid
        case 1:
            return list(map(list, zip(*grid[::-1])))  # CW
        case 2:
            return list(x[::-1] for x in grid[::-1])  # 180
        case 3:
            return list(map(list, zip(*grid)))[::-1]  # CCW
    return list(map(list, zip(*grid[::-1])))

def succ(s):
    """Convenience function for Ruby's String#succ."""
    if not s:
        return s
    if any(ord(c) >= 128 for c in s):
        raise ValueError('Cannot encode string with non-ascii characters')

    def succ_one(c):
        if 48 <= c < 58:  # digit
            if c == 57:
                return 48, True
            else:
                return c + 1, False
        elif 65 <= c < 91:
            if c == 90:
                return 65, True
            else:
                return c + 1, False
        elif 97 <= c < 123:
            if c == 122:
                return 97, True
            else:
                return c + 1, False
        else:
            if c == 255:
                return 0, True
            else:
                return c + 1, False

    typ = type(s)
    s = bytearray(s, 'utf-8')

    i = len(s) - 1
    while i >= 0 and not (48 <= s[i] < 58 or 65 <= s[i] < 91 or 97 <= s[i] < 123):
        i -= 1

    if i < 0:
        return typ(s.decode())

    while True:
        if i < 0:
            if 48 <= s[0] < 58:
                s = b'1' + s
            elif 65 <= s[0] < 91:
                s = b'A' + s
            elif 97 <= s[0] < 123:
                s = b'a' + s
            else:
                s = b'\x01' + s
            break

        s[i], is_last = succ_one(s[i])
        if not is_last:
            break
        i -= 1
    return typ(s.decode())