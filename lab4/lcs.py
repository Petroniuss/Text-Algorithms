import sys
import numpy as np


def lcs_table(x, y):
    """
        Returns table construced by dynamic algorithm for finding lcs.
    """
    m, n = len(x), len(y)
    dp = np.empty((m + 1, n + 1))

    dp[0] = np.zeros(n + 1)
    dp[:, 0] = np.zeros(m + 1)

    for j in range(1, m + 1):
        for i in range(1, n + 1):
            if x[j - 1] == y[i - 1]:
                dp[j, i] = 1 + dp[j - 1, i - 1]
            else:
                dp[j, i] = max(dp[j - 1, i], dp[j, i - 1])

    return dp


def lcs(x, y, dp=None, join=False):
    """
        Returns longest common subsequence for given strings
        or sequences of comparable elements: x and y.
        join - boolean which specifies whether to join lcs into one element.
    """
    if dp is None:
        dp = lcs_table(x, y)

    seq = []
    ptrs = [[-1, 0],
            [0, -1]]
    xs = np.empty(2)
    j, i = len(x), len(y)
    while j != 0 and i != 0:
        if x[j - 1] == y[i - 1]:
            seq.append(x[j - 1])
            j, i = j - 1, i - 1
        else:
            for k in range(2):
                xs[k] = dp[j + ptrs[k][1], i + ptrs[k][0]]
            k = np.argmax(xs)
            j, i = j + ptrs[k][1], i + ptrs[k][0]

    seq.reverse()
    if not join:
        return seq
    return "".join(seq)


def diff_files(original, new):
    x, y = None, None
    with open(original, "r", encoding='UTF-8') as file:
        x = file.read().splitlines()

    with open(new, "r", encoding='UTF-8') as file:
        y = file.read().splitlines()

    print(diff(x, y))


def lcs_length_files(original, new):
    """
        Prints length of lcs for given files. Note that here I could have provided more memory efficient solution,
        since I don't need whole table (which is needed when reconstructing lcs and I only care about length)
        but it works for the assignment so I am keeping it that way ;)
    """
    x, y = None, None
    with open(original, "r", encoding='UTF-8') as file:
        x = file.read()

    with open(new, "r", encoding='UTF-8') as file:
        y = file.read()

    lcs_len = len(lcs(x, y, join=True))
    print(
        f'Length of longest common subsequence for {original} with {len(x)} characters and {new} with {len(y)} characters is {lcs_len}')


def diff(x, y):
    """
        Diff two sequences of comparable elements (hopefully strings but since this is Python who knows with what it might work :)). 

        Note that I am using ansi escape codes to get colored output, so if terminal (or whatever reads stdout) does not handle them, output might be messy.
    """
    output = []
    j, i = 0, 0
    for common in lcs(x, y):
        start_i, start_j = i + 1, j + 1
        changes = []
        if j < len(x) and x[j] != common:
            while j < len(x) and x[j] != common:
                changes.append('< ' + x[j] + '\n')
                j = j + 1
            changes.append(ANSI.STOP)

            if len(changes) == 2:
                output.append(
                    f'{start_j}d{start_i}{ANSI.RED}\n')
            else:
                output.append(
                    f'{start_j},{start_j + len(changes) - 2}d{start_i}{ANSI.RED}\n')
            output.extend(changes)
        j = j + 1

        changes = []
        if i < len(y) and y[i] != common:
            while i < len(y) and y[i] != common:
                changes.append('> ' + y[i] + '\n')
                i = i + 1
            changes.append(ANSI.STOP)

            if len(changes) == 2:
                output.append(
                    f'{start_j - 1}a{start_i}{ANSI.GREEN}\n')
            else:
                output.append(
                    f'{start_j - 1}a{start_i},{start_i + len(changes) - 2}{ANSI.GREEN}\n')
            output.extend(changes)
        i = i + 1

    start_i, start_j = i + 1, j + 1
    changes = []
    if j < len(x):
        while j < len(x):
            changes.append('< ' + x[j] + '\n')
            j = j + 1
        changes.append(ANSI.STOP)

        if len(changes) == 2:
            output.append(
                f'{start_j}d{start_i}{ANSI.RED}\n')
        else:
            output.append(
                f'{start_j},{start_j + len(changes) - 2}d{start_i}{ANSI.RED}\n')
        output.extend(changes)

    changes = []
    if i < len(y):
        while i < len(y):
            changes.append('> ' + y[i] + '\n')
            i = i + 1
        changes.append(ANSI.STOP)

        if len(changes) == 2:
            output.append(
                f'{start_j - 1}a{start_i}{ANSI.GREEN}\n')
        else:
            output.append(
                f'{start_j - 1}a{start_i},{start_i + len(changes) - 2}{ANSI.GREEN}\n')
        output.extend(changes)

    return ''.join(output)


def diff_line(x, y):
    "This function `diffs` two lines"
    top, bottom = [], []
    j, i = 0, 0
    for common in lcs(x, y, join=True):
        while j < len(x) and x[j] != common:
            top.append(x[j])
            bottom.append('-')
            j = j + 1
        j = j + 1

        while i < len(y) and y[i] != common:
            top.append(y[i])
            bottom.append('+')
            i = i + 1
        i = i + 1

        top.append(common)
        bottom.append(' ')
        j = j + 1
        i = i + 1

    while j < len(x):
        top.append(x[j])
        bottom.append('-')
        j = j + 1

    while i < len(y):
        top.append(y[i])
        bottom.append('+')
        i = i + 1

    lines = '<' + x + '\n>' + y + '\n'
    top = ' ' + ''.join(top)
    bottom = ' ' + ''.join(bottom)
    result = lines + top + '\n' + bottom + '\n'

    return result


class ANSI:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    STOP = '\033[0m'


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(ANSI.BLUE + 'Please pass two valid text files.' + ANSI.STOP)
        exit()

    original = sys.argv[1]
    new = sys.argv[2]

    print(ANSI.BLUE + '@@ Diff @@' + ANSI.STOP)
    diff_files(original, new)
