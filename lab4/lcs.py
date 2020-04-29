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


def lcs(x, y, dp=None):
    """
        Returns longest common subsequence for given strings: x and y.
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
    return "".join(seq)


def diff_line(x, y):
    top = []
    bottom = []
    j, i = 0, 0
    for common in lcs(x, y):
        while x[j] != common:
            top.append(x[j])
            bottom.append('-')
            j = j + 1
        while y[i] != common:
            top.append(y[i])
            bottom.append('+')
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
