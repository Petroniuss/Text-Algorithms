import numpy as np
from enum import Enum
import time
from IPython.display import clear_output


def delta(a, b):
    if a == b:
        return 0
    else:
        return 1


def edit_distance(x, y, delta=delta, dp=None):
    """
        Returns edit distance between word x and word y.
    """
    if dp is None:
        dp = edit_table(x, y, delta)

    return dp[len(x), len(y)]


def edit_table(x, y, delta=delta):
    """
        Returns table constructed via dynamic algorithm.
    """
    m, n = len(x), len(y)
    dp = np.empty((m + 1, n + 1))

    for j in range(m + 1):
        dp[j, 0] = j

    for i in range(1, n + 1):
        dp[0, i] = i

    for j in range(1, m + 1):
        for i in range(1, n + 1):
            dp[j, i] = min(
                dp[j - 1, i] + 1,
                dp[j, i - 1] + 1,
                dp[j - 1, i - 1] + delta(x[j - 1], y[i - 1]))

    return dp


class EditOperation(Enum):
    """
        0 - insert letter of y into x,
        1 - delete letter of x,
        2 - replace (or don't) letter of y with letter of x.
    """
    INSERT = 0
    DELETE = 1
    REPLACE = 2


def edit_sequence(x, y, delta=delta):
    """
        Returns one of possibly many minimal edit sequences.
    """
    dp = edit_table(x, y, delta)
    m, n = len(x), len(y)

    ptr = [[1, 0], [0, 1], [1, 1]]
    seq = []
    moves = np.empty(3)
    j, i = m, n
    while i != 0 and j != 0:
        for k in range(3):
            moves[k] = dp[j - ptr[k][1], i - ptr[k][0]]

        k = np.argmin(moves)
        if moves[EditOperation.REPLACE.value] == moves[k]:
            k = EditOperation.REPLACE.value
        j, i = j - ptr[k][1], i - ptr[k][0]

        seq.append(EditOperation(k))

    if i == 0:
        for _ in range(j, 0, -1):
            seq.append(EditOperation.DELETE)

    if j == 0:
        for _ in range(i, 0, -1):
            seq.append(EditOperation.INSERT)

    seq.reverse()
    return seq


def visualize(x, y, delta=delta, sleep_for=.9):
    """
       This function triggers text animation which
       shows step by step how to convert word x into y.
       Parameter sleep_for - can be used to customize speed of text animation.
    """
    dashes = max(len(x), len(y), 24)
    arrow_up = '\u2191'
    distance = 0
    i, j = 0, 0
    operation = 'INIT'

    def frame():
        print('-' * dashes)
        print(y, i * ' ' + arrow_up, sep='\n')
        print(x, j * ' ' + arrow_up, sep='\n')
        print('-' * dashes)
        print(operation)
        clear_output(wait=True)
        time.sleep(sleep_for)

    gen = edit_sequence(x, y, delta=delta)
    frame()
    for edit_operation in gen:
        clear_output(wait=True)
        operation = edit_operation.name
        if edit_operation == EditOperation.REPLACE:
            if y[i] != x[j]:
                distance += 1
                x = x[:j] + '_' + x[j + 1:]
                frame()

                x = x[:j] + y[i] + x[j + 1:]
                frame()

            i, j = i + 1, j + 1
        elif edit_operation == EditOperation.INSERT:
            x = x[:j] + '_' + x[j:]
            frame()

            x = x[:j] + y[i] + x[j + 1:]
            frame()

            i, j = i + 1, j + 1
            distance += 1
        elif edit_operation == EditOperation.DELETE:
            x = x[:j] + '_' + x[j + 1:]
            frame()

            x = x[:j] + x[j + 1:]
            distance += 1

        operation = f'DONE.. edit distance: {distance}'
        frame()
