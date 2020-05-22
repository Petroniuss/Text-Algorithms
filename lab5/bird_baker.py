import aho_corasick
import numpy as np

# Note that functions in this module assume numpy arrays


def bird_baker(Y, X):
    """
        Naive implementation which does not use kmp 
        for traversing array with states found by aho-corasick machine.
        But in return it allows us to pass non-rectangular matrices as Y and X.

        Arguments:
            Y - 2d array with text/img,
            X - 2d array with pattern
        Returns:
            generator of upper left indices (tuple) of matched pattern
    """
    n1 = len(Y)
    m1 = len(X)
    T = [np.empty(len(Y[i]), dtype=np.int32) for i in range(n1)]
    root = aho_corasick.preprocess(X)
    final = root.get_final_states()

    # Constucting array with states
    for j in range(n1):
        row = Y[j]
        r = root
        for i, v in enumerate(row):
            s = r.get_node(v)
            while s == aho_corasick.UNDEFINED:
                r = r.get_fail()
                s = r.get_node(v)
            r = s

            T[j][i] = r.id

    # Naive traversing
    m2 = len(X[m1 - 1])
    for j in range(m1 - 1, n1):
        n2 = len(Y[j])
        for i in range(m2 - 1, n2):
            k = m1 - 1
            row, col = j, i
            while k >= 0:
                dt = m2 - len(X[k])
                col = i - dt
                if row >= 0 and col >= 0 and col < len(Y[row]) and \
                        T[row][col] in final[k]:
                    k -= 1
                    row -= 1
                else:
                    break

            if k == -1:
                yield (j - m1 + 1, i - m2 + 1)


# # DOES NOT WORK!
# def pre_kmp(X):
#     """
#         Precomputes next array for kmp algorithm vertically.
#     """
#     print('pre!')
#     m1, m2 = X.shape
#     f = np.empty(m1)
#     i, j = 0, -1
#     f[i] = j
#     while i < m1:
#         while (j > -1) and (not np.array_equal(X[i], X[j])):
#             j = f[j]

#         i += 1
#         j += 1
#         if np.array_equal(X[i], X[j]):
#             f[i] = f[j]
#         else:
#             f[i] = j

#     return f


# def bird_baker(Y, X):
#     """
#         This function implements bird&baker alogrithm for two-dimensional
#         pattern matching.

#         Note that it assumes that Y, X are rectangular matrices!

#         Arguments:
#             Y - 2d array with text/img,
#             X - 2d array with pattern
#         Returns:
#             generator of upper left indices (tuple) of matched pattern
#     """
#     Y = np.array(Y)
#     X = np.array(X)

#     root = aho_corasick.preprocess(X)
#     f = pre_kmp(X)
#     a = np.zeros(Y.shape[0], dtype=np.int32)
#     m1, m2 = X.shape

#     for row in range(Y.shape[0]):
#         r = root
#         for col, v in enumerate(Y[row]):
#             s = r.get_node(v)
#             while s == aho_corasick.UNDEFINED:
#                 r = r.get_fail()
#                 s = r.get_node(v)
#             r = s
#             output = r.get_output()
#             if output != aho_corasick.UNDEFINED:
#                 for pattern_idx in output:
#                     x = X[pattern_idx]
#                     k = a[col]
#                     while k > 0 and X[k] != x:
#                         k = f[k]
#                     a[column] = k + 1
#                     if k >= m1 - 1:
#                         yield (row - m1 + 1, col - m2 + 1)
#             else:
#                 a[col] = 0
