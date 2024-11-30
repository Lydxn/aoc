from aoc.helpers import comb, search, succ
import ast
import regex


def mint(arr):
    """Shortcut for converting a list of strings to a list of numbers."""
    return xlist(map(ast.literal_eval, arr))


class FixedTypeMeta(type):
    """A metaclass that monkeypatches methods to properly return its subtype."""

    def __new__(cls, name, bases, attrs):
        obj = super().__new__(cls, name, bases, attrs)
        base = obj.__base__
        for meth_name in obj.__patchmethods__:
            func = getattr(base, meth_name, None)
            if func is None:
                continue
            def wrapper(self, *args, _base_func=func, **kwargs):
                result = _base_func(self, *args, **kwargs)
                return obj(result) if isinstance(result, base) else result
            wrapper.__qualname__ = obj.__name__ + '.' + meth_name
            setattr(obj, meth_name, wrapper)
        return obj


class xstr(str, metaclass=FixedTypeMeta):
    """An extension of the built-in `str` type for concise input parsing."""

    __patchmethods__ = [
        '__add__', '__format__', '__getitem__', '__mod__', '__mul__', '__rmul__',
        'capitalize', 'casefold', 'center', 'encode', 'expandtabs', 'format',
        'format_map', 'join', 'ljust', 'lower', 'lstrip', 'removeprefix',
        'removesuffix', 'replace', 'rjust', 'rstrip', 'strip', 'swapcase',
        'title', 'translate', 'upper', 'zfill',
    ]

    def partition(self, sep):
        a, b, c = super().partition(sep)
        return (xstr(a), xstr(b), xstr(c))

    def rpartition(self, sep):
        a, b, c = super().rpartition(sep)
        return (xstr(a), xstr(b), xstr(c))

    def rsplit(self, sep=None, maxsplit=-1):
        return xlist(super().rsplit(sep, maxsplit))

    def split(self, sep=None, maxsplit=-1):
        return xlist(super().split(sep, maxsplit))

    def splitlines(self, keepends=False):
        return xlist(super().splitlines(keepends))

    def __iter__(self):
        return (xstr(c) for c in super().__iter__())

    """Non-standard string utility functions"""

    def adj(self, k=2):
        """Same as comb(k, 1)."""
        return self.comb(k, 1)

    @property
    def b(self):
        """Encode the string as UTF-8 bytestring."""
        return self.encode()

    @property
    def blocks(self):
        """Return a list of tokens separated each by two newlines."""
        return self.split('\n\n')

    def comb(self, *args, **kwargs):
        """Wrapper around the comb() function."""
        return comb(self, *args, **kwargs)

    def e(self, **locals):
        """Evaluate the string as Python code."""
        return eval(self, {}, locals)

    def ew(self, *args, **kwargs):
        """An alias of str.endswith()."""
        return self.endswith(*args, **kwargs)

    def gmi(self, pattern, flags=0):
        """Find all matches (re.Match) to the specified pattern."""
        return xlist(regex.finditer(pattern, self, flags))

    def gm(self, pattern, flags=0):
        """Find all matches to the specified pattern."""
        return xlist(regex.findall(pattern, self, flags))

    @property
    def grid(self):
        """Convert a 2D grid into a 2D list of chars"""
        return xlist(map(xlist, self.lines))

    def gs(self, pattern, repl, count=0, flags=0):
        """Find and replace all occurrences of the specified pattern with the replacement."""
        return xstr(regex.sub(pattern, repl, self, count, flags))

    @property
    def ints(self):
        """Find all *unsigned* integers matching the regex /\d+/, and cast to int()."""
        return mint(self.gm(r'\d+'))

    @property
    def lc(self):
        """An alias of str.lower()."""
        return self.lower()

    @property
    def lines(self):
        """Return a list of lines."""
        return self.s('\n')

    def m(self, pattern, flags=0):
        """Find a single match to the specified pattern."""
        m = regex.search(pattern, self, flags)
        return m.groups() if m is not None else None

    def p(self, format, **kwargs):
        """An alias of parse.search()."""
        return search(format, self, **kwargs)

    def r(self, *args, **kwargs):
        """An alias of str.replace()."""
        return self.replace(*args, **kwargs)

    def s(self, *args, **kwargs):
        """An alias of str.split()."""
        return self.split(*args, **kwargs)

    @property
    def sints(self):
        """Find all *signed* integers matching the regex /-?\d+/, and cast to int()."""
        return mint(self.gm(r'-?\d+'))

    @property
    def succ(self):
        """An alias of succ()."""
        return succ(self)

    def sw(self, *args, **kwargs):
        """An alias of str.startswith()."""
        return self.startswith(*args, **kwargs)

    @property
    def tc(self):
        """An alias of str.title()."""
        return self.title()

    @property
    def uc(self):
        """An alias of str.upper()."""
        return self.upper()

    @property
    def words(self):
        """Find all words matching the regex /\w+/."""
        return self.gm(r'\w+')


class VectorizedClassMeta(type):
    """Add vectorized computation to the methods of an iterable class"""

    def __new__(cls, name, bases, attrs):
        obj = super().__new__(cls, name, bases, attrs)
        # Vectorize non-dunder methods by default
        vec_class = obj.__vectorclass__
        __vectormethods__ = set(obj.__vectormethods__) | {
            x for x in dir(vec_class)
            if not x.startswith('__')
        }
        for meth_name in __vectormethods__:
            func = getattr(vec_class, meth_name)
            if hasattr(obj, meth_name):
                continue
            if callable(func):
                def wrapper(self, *args, _base_func=func, **kwargs):
                    return obj(_base_func(x, *args, **kwargs) for x in self)
                wrapper.__qualname__ = obj.__name__ + '.' + meth_name
                setattr(obj, meth_name, wrapper)
            elif isinstance(func, property):
                def wrapper(self, *args, _base_func=func.fget, **kwargs):
                    return obj(_base_func(x, *args, **kwargs) for x in self)
                wrapper.__qualname__ = obj.__name__ + '.' + meth_name
                setattr(obj, meth_name, property(wrapper))
        return obj


class xlist(list, metaclass=VectorizedClassMeta):
    """An extension of the built-in `list` type for concise input parsing."""

    __vectorclass__ = xstr
    __vectormethods__ = []

    def __init__(self, iterable=()):
        iterable = (xstr(i) if isinstance(i, str) else i for i in iterable)
        return super().__init__(iterable)

    def __add__(self, other):
        if isinstance(other, list):
            return xlist(super().__add__(other))
        return xlist(x + other for x in self)

    def __mul__(self, other):
        if isinstance(other, list):
            return xlist(super().__mul__(other))
        return xlist(x * other for x in self)

    __radd__ = __add__
    __rmul__ = __mul__

    def adj(self, k=2):
        """Same as comb(k, 1)."""
        return self.comb(k, 1)

    def comb(self, size=1, step=None, partial=False):
        """Wrapper around the comb() function."""
        return xlist(comb(self, size, step, partial))

    def j(self, sep=''):
        """Join a list by a separator."""
        return xstr(sep).join(map(xstr, self))

    def reduce(self, func, default=None):
        if len(self) == 0:
            return self
        if default is None:
            result = self[0]
            for x in self[1:]:
                result = func(result, x)
        else:
            result = default
            for x in self:
                result = func(result, x)
        return result

    @property
    def max(self):
        return max(self)

    @property
    def min(self):
        return min(self)

    @property
    def sum(self):
        if len(self) == 0:
            return self
        result = self[0]
        for x in self[1:]:
            result += x
        return result


class CursedAnnotations(dict):
    """Allow type hints to auto-coerce assigned values!"""

    def __init__(self, types, globals):
        self.types = tuple(types)
        self.globals = globals

    def __setitem__(self, key, value):
        if value in self.types:
            self.globals[key] = value(self.globals[key])