def adaptive_huffman_encode(text, N=53):
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
        NYT = Node(w=0, n=N)

        self.root = NYT
        self.leaves = {'NYT': NYT}
        self.weight_class = {0: set([NYT]), 1: set()}
        self.N = N - 1

    def get_NYT(self):
        return self.leaves['NYT']

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

    # FIXME update should increase weight by one!
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
            '\n' + str(self.root) + \
            '\n' + '-' * 22


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
