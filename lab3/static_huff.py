from heapq import heappop, heappush
from bitarray import bitarray


def static_huffman(text):
    counts = count_frequencies(text)
    heap = []

    for letter, count in counts.items():
        node = Node(count, letter=letter)
        heappush(heap, node)

    while (len(heap) > 1):
        n1, n2 = heappop(heap), heappop(heap)
        combined_v = n1.v + n2.v
        new_node = Node(combined_v, n1, n2)
        n1.parent, n2.parent = new_node, new_node

        heappush(heap, new_node)

    return heappop(heap)


def encode(text, root=None):
    if not root:
        root = static_huffman(text)

    codes = bit_codes(root)
    encoded = bitarray()
    for letter in text:
        encoded += codes[letter]

    return encoded


def decode(bits, root):
    decoded = ''
    current = root
    for bit in bits:
        if bit:
            current = current.rightKid
        else:
            current = current.leftKid

        if current.is_leaf():
            decoded += current.letter
            current = root

    return decoded


# ------------------ Utilties ----------------------
class Node:
    def __init__(self, v, leftKid=None, rightKid=None, letter=None):
        self.leftKid, self.rightKid = leftKid, rightKid
        self.parent = None
        self.v = v

        if letter:
            self.letter = letter

    def is_leaf(self):
        return self.leftKid == None

    def __lt__(self, other):
        return self.v < other.v

    def __repr__(self):
        if self.parent:
            return self.str_repr_util()

        return '-' * 5 + 'HUFFMAN TREE' + '-' * 5 + '\n' + self.str_repr_util()

    def str_repr_util(self, spaces=1):
        me = f'#{self.v}'

        if not self.leftKid:
            me += f' => {self.letter}'
        else:
            left = self.leftKid.str_repr_util(spaces + 1)
            right = self.rightKid.str_repr_util(spaces + 1)
            me += '\n' + (' ' * spaces) + '0 -> ' + left
            me += '\n' + (' ' * spaces) + '1 -> ' + right

        return me


def count_frequencies(text):
    counts = {}
    for letter in text:
        if letter in counts:
            counts[letter] += 1
        else:
            counts[letter] = 1

    return counts


def bit_codes(root):
    codes = {}
    bit_codes_util(root, '', codes)

    return codes


def bit_codes_util(node, prev, codes):
    if node.is_leaf():
        codes[node.letter] = bitarray(prev)
    else:
        bit_codes_util(node.leftKid, prev + '0', codes)
        bit_codes_util(node.rightKid, prev + '1', codes)
