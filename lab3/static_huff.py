from heapq import heappop, heappush
from bitarray import bitarray


# ----------------------------------------- FILE FORMAT -----------------------------------------|
# 1. Number of bits obtained from huffman encoding.                                              |
# 2. Number of encoded characters.                                                               |
# 3. Table: letter - (1 byte) => encoding's size (1 byte) => actual encoding (1/2/3... bytes)    |
# 4. Rest are bits obtained from huffman encoding.                                               |
# ----------------------------------------- FILE FORMAT -----------------------------------------|
def compress_file(filename, save_to):
    text = None
    with open(filename, "r") as file:
        text = file.read()

    with open(save_to, 'wb') as file:
        bits, root = encode(text)
        codes = bit_codes(root)

        file.write(len(bits).to_bytes(4, byteorder='big', signed=False))
        file.write(len(codes).to_bytes(4, byteorder='big', signed=False))

        for letter, code in codes.items():
            letter_byte = bitarray()
            letter_byte.frombytes(letter.encode())
            enc_size = len(code)

            letter_byte.tofile(file)
            file.write(enc_size.to_bytes(1, byteorder='big', signed=False))
            code.tofile(file)

        bits.tofile(file)


def decompress_file(filename, save_to):
    text = None
    with open(filename, "rb") as file:
        root = Node(-1)
        no_bits = int.from_bytes(file.read(4), byteorder='big', signed=True)
        no_chars = int.from_bytes(file.read(4), byteorder='big', signed=True)

        for _ in range(no_chars):
            letter_bits = bitarray()
            letter_bits.fromfile(file, 1)
            letter = letter_bits.tobytes().decode()

            enc_size = int.from_bytes(
                file.read(1), byteorder='big', signed=True)

            bytes_to_read = ((enc_size - 1) // 8) + 1
            code = bitarray()
            code.fromfile(file, bytes_to_read)
            code = code[:enc_size]

            appendLeaf(root, code, letter)

        bits = bitarray()
        bits.fromfile(file)
        bits = bits[:no_bits]
        text = decode(bits, root)

    with open(save_to, "w") as file:
        file.write(text)


# When decoding we reconstruct huffman tree.
def appendLeaf(root, code, letter):
    current = root
    for bit in code:
        if not bit:
            if current.leftKid is None:
                current.leftKid = Node(0)
            current = current.leftKid
        else:
            if current.rightKid is None:
                current.rightKid = Node(1)
            current = current.rightKid

    # When in leaf do as leaves do.
    current.letter = letter
# -------------------------------------------- FILE ---------------------------------------------|


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

    return encoded, root


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
        return self.leftKid == None and self.rightKid == None

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
