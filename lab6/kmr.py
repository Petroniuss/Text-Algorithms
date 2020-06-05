import math

# Slighly improved implementation of dr Pohl


# def pohl_sort_rename(sequence):
#     last_entry = None
#     index = 0
#     position_to_index = [None] * len(sequence)
#     first_entry = {}

#     for entry in sorted([(e, i) for i, e in enumerate(sequence)]):
#         if (last_entry and last_entry[0] != entry[0]):
#             index += 1
#             first_entry[index] = entry[1]
#         elif last_entry is None:
#             first_entry[0] = entry[1]

#         position_to_index[entry[1]] = index
#         last_entry = entry

#     return (position_to_index, first_entry)


# def pohl_kmr(text, pad_with=chr(0x10ffff)):
#     original_len = len(text)
#     factor = math.floor(math.log2(len(text)))
#     max_len = 2 ** factor
#     padding_len = 2 ** (factor) - 1
#     text += pad_with * padding_len

#     position_to_index, first_entry = pohl_sort_rename(list(text))
#     names = {1: position_to_index}
#     entries = {1: first_entry}

#     for i in range(1, factor):
#         power = 2 ** (i - 1)
#         new_seq = []
#         for j in range(len(names[power]) - power):
#             new_seq.append((names[power][j], names[power][j + power]))

#         position_to_index, first_entry = pohl_sort_rename(new_seq)
#         names[power * 2] = position_to_index
#         entries[power * 2] = first_entry

#     return (names, entries)


# def pohl_search_pattern(pattern, text, break_with=chr(0x10ffff)):
#     m = len(pattern)

#     new_text = pattern + break_with + text
#     names, entries = pohl_kmr(new_text)

#     t = 2 ** math.floor(math.log2(m))

#     name1, name2 = names[t][0], names[t][m - t]
#     for i in range(m + 1, len(new_text)):
#         cand_name1, cand_name2 = names[t][i], names[t][i + m - t]

#         if name1 == cand_name1 and name2 == cand_name2:
#             yield (i - m - 1)


# -----------------------------------------------------------------------

# Tweaked implementation!

# Todos
# 1. Implement radix sort to reduce complexity of sort_rename to O(n)
# 2. Use implemented sort instead of `sorted`
# 3. Implement searching for pattern using basic approach. -> DBF(pat&text)
# 4. Implement hashing which will result in (n^2logn) space complexity --> i guess it's too much.
# 5. Implement searching for pattern using above mentioned hashing.


def sort_rename(sequence, seq_of_chars=False):
    """
        It uses radix sort for tuples.
    """
    last_entry = None
    index = 0
    position_to_index = [None] * len(sequence)
    first_entry = {}

    sorted_entries = None
    if seq_of_chars:
        sorted_entries = sorted([(e, i) for i, e in enumerate(sequence)])
    else:
        to_sort = [(e1, e2, i) for i, (e1, e2) in enumerate(sequence)]
        sorted_entries = radix_sort(to_sort, 3)
        sorted_entries = [((e1, e2), i) for (e1, e2, i) in sorted_entries]

    for entry in sorted_entries:
        if (last_entry and last_entry[0] != entry[0]):
            index += 1
            first_entry[index] = entry[1]
        elif last_entry is None:
            first_entry[0] = entry[1]

        position_to_index[entry[1]] = index
        last_entry = entry

    return (position_to_index, first_entry)


def kmr(text, m=None, pad_with=chr(0x10ffff)):
    """
        Computes dbf up to m if set or else up to max power of two.
    """
    original_len = len(text)
    factor = math.floor(math.log2(len(text)))
    max_len = 2 ** factor
    padding_len = 2 ** (factor) - 1
    text += pad_with * padding_len

    position_to_index, first_entry = sort_rename(list(text), seq_of_chars=True)
    names = {1: position_to_index}
    entries = {1: first_entry}

    if m is None:
        m = factor
    else:
        m = math.floor(math.log2(m)) + 1

    for i in range(1, m):
        power = 2 ** (i - 1)
        new_seq = []
        for j in range(len(names[power]) - power):
            new_seq.append((names[power][j], names[power][j + power]))

        position_to_index, first_entry = sort_rename(new_seq)
        names[power * 2] = position_to_index
        entries[power * 2] = first_entry

    return (names, entries)


def basic_search(pattern, text, break_with=chr(0x10ffff)):
    """
        Basic serching which builds dbf each time resulting in O(nlogm) space and time complexity.
    """
    m = len(pattern)

    new_text = pattern + break_with + text
    names, entries = kmr(new_text, m=m)

    t = 2 ** math.floor(math.log2(m))

    name1, name2 = names[t][0], names[t][m - t]
    for i in range(m + 1, len(new_text)):
        cand_name1, cand_name2 = names[t][i], names[t][i + m - t]

        if name1 == cand_name1 and name2 == cand_name2:
            yield (i - m - 1)


def radix_sort(seq, tuple_len):
    """
        Radix sort for sequences of tuples with fixed len.
    """
    for k in range(tuple_len - 1, -1, -1):
        seq = counting_sort(seq, k)

    return seq


def counting_sort(seq, k):
    """
        Counting sort for tuples with values less than n = len(seq).

        k - sort with regard to k-th element.
    """
    n = len(seq)
    output = [None] * n
    count = [0] * n

    for i in range(n):
        count[seq[i][k]] += 1

    for i in range(1, n):
        count[i] += count[i - 1]

    for i in range(n - 1, -1, -1):
        output[count[seq[i][k]] - 1] = seq[i]
        count[seq[i][k]] -= 1

    return output
