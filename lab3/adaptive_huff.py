from bitarray import bitarray
import pickle

# FIXME serialization might not work correctly!!!


# ------------- FILE UTILS -----------
def compress_file(filename, save_to):
    bits = None
    with open(filename, "r") as file:
        text = file.read()
        bits = encode(text)

    with open(save_to, 'wb') as file:
        pickle.dump(bits)


def decompress_file(filename, save_to):
    text = None
    with open(filename, "rb") as file:
        bits = pickle.load(file)
        text = decode(bits)

    with open(save_to, "w") as file:
        file.write(text)
# -------------------------------------


def encode(text, N=53):
    bits = bitarray()
    tree = Tree(N)
    for letter in text:
        if letter in tree.leaves:
            bits += tree.get_code(letter)

            node = tree.leaves[letter]
            tree.update(node)
        else:
            code = tree.get_code('NYT')
            code.frombytes(letter.encode())
            bits += code

            tree.spawn(letter)

    return bits


def decode(bits, N=53):
    tree = Tree(N)
    decoded = ''
    i, current = 0, tree.root
    while i < len(bits):
        if current.is_leaf():
            letter = None
            if current.char == 'NYT':
                byte = bits[i:i+8]
                letter = byte.tobytes().decode()
                i += 8

                tree.spawn(letter)
            else:
                letter = current.char

                node = tree.leaves[letter]
                tree.update(node)

            decoded += letter
            current = tree.root
        else:
            if not bits[i]:
                current = current.leftKid
            else:
                current = current.rightKid

            i += 1

    # In case we finished in leaf.
    if current.is_leaf():
        letter = current.char

        node = tree.leaves[letter]
        tree.update(node)

        decoded += letter
        current = tree.root

    return decoded


def adaptive_huffman(text, N=53):
    tree = Tree(N)
    for letter in text:
        if letter in tree.leaves:
            node = tree.leaves[letter]
            tree.update(node)
        else:
            tree.spawn(letter)

    return tree

# --------------------------------- UTILITIES -----------------------------------


class Tree:
    def __init__(self, N):
        NYT = Node(w=0, n=N, char='NYT')

        self.root = NYT
        self.leaves = {'NYT': NYT}
        self.weight_class = {0: set([NYT]), 1: set()}
        self.N = N - 1

    def get_NYT(self):
        return self.leaves['NYT']

    def get_code(self, letter):
        """ Used when encoding. """
        if letter not in self.leaves:
            raise Exception("Sth went terribly wrong!")

        node = self.leaves[letter]
        code = bitarray()
        while node.parent is not None:
            parent = node.parent
            if parent.leftKid == node:
                code.append(0)
            else:
                code.append(1)
            node = parent
        code.reverse()

        return code

    def spawn(self, letter):
        NYT = self.get_NYT()

        right = Node(w=1, n=self.N, parent=NYT, char=letter)
        left = Node(w=0, n=self.N - 1, parent=NYT, char='NYT')
        self.N -= 2

        NYT.char = None
        NYT.leftKid = left
        NYT.rightKid = right

        self.leaves[letter] = right
        self.leaves['NYT'] = left

        self.weight_class[0].add(left)
        self.weight_class[1].add(right)

        self.update(NYT)

    def update(self, node):
        # We do not swap node with its parent.
        if node.parent != None and node.parent.w != node.w:
            max_n_node = node
            for class_node in self.weight_class[node.w]:
                if class_node.n > max_n_node.n:
                    max_n_node = class_node

            # Swap nodes if property is violated.
            if max_n_node != node:
                self.swap(node, max_n_node)

        # Update weights.
        self.weight_class[node.w].remove(node)
        node.w += 1

        if node.w not in self.weight_class:
            self.weight_class[node.w] = set()
        self.weight_class[node.w].add(node)

        # And propagate it further.
        if node.parent != None:
            self.update(node.parent)

    def swap(self, node, max_node):
        # swap node numbers.
        node.n, max_node.n = max_node.n, node.n

        # swap nodes.
        node_parent = node.parent
        max_parent = max_node.parent

        # We distinguish two cases:
        #   - both nodes have the same parent
        #   - or they do not
        if node_parent != max_parent:
            # node is left child
            if node_parent.leftKid == node:
                node_parent.leftKid = max_node
            else:
                node_parent.rightKid = max_node
            max_node.parent = node_parent

            # max_node is left child
            if max_parent.leftKid == max_node:
                max_parent.leftKid = node
            else:
                max_parent.rightKid = node
            node.parent = max_parent

        else:
            if node_parent.leftKid == node:
                node_parent.leftKid = max_node
                node_parent.rightKid = node
            else:
                node_parent.leftKid = node
                node_parent.rightKid = max_node

    def __repr__(self):
        return '-' * 5 + 'HUFFMAN TREE' + '-' * 5 + \
            '\n' + str(self.root)


class Node:
    def __init__(self, w, n, char=None, leftKid=None, rightKid=None, parent=None):
        self.w = w
        self.n = n
        self.leftKid = leftKid
        self.rightKid = rightKid
        self.parent = parent
        self.char = char

    def __str__(self):
        return self.str_repr_util()

    def __repr__(self):
        me = f'#{{ W={self.w}, N={self.n} }}'
        if self.is_leaf():
            me += f' => {self.char}'

        return me

    def str_repr_util(self, spaces=1):
        me = f'#{{ W={self.w}, N={self.n} }}'

        if self.is_leaf():
            me += f' => {self.char}'
        else:
            left = self.leftKid.str_repr_util(spaces + 1)
            right = self.rightKid.str_repr_util(spaces + 1)
            me += '\n' + (' ' * spaces) + '0 -> ' + left
            me += '\n' + (' ' * spaces) + '1 -> ' + right

        return me

    def is_leaf(self):
        return self.leftKid == None
