from aoc.api import coerce, Puzzle
from aoc.types import CursedAnnotations, xstr, xlist
import os

class SamplePuzzle:
    def __init__(self, num, data):
        self.num = num
        self.data = data

    def submit(self, answer, _=None):
        if answer is None:
            return
        answer = coerce(answer)
        print(f'Output of sample #{self.num}: {answer}')

    __call__ = submit

def exec(year, day, samples=None):
    if samples is None:
        samples = []

    # cursed stuff
    import __main__, sys
    __main__.__annotations__ = CursedAnnotations([xstr, xlist], __main__.__dict__)

    # 0 = run all, i = run i'th sample
    arg = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    if arg > 0:
        sample = samples[arg - 1]
        return SamplePuzzle(arg, sample)

    # Do a fork/exec over each sample input, and then finally the real input
    for num, sample in enumerate(samples):
        pid = os.fork()
        if pid != 0:
            os.waitpid(pid, 0)
            print('-' * 50)
        else:
            return SamplePuzzle(num + 1, sample)
    return Puzzle(year, day)