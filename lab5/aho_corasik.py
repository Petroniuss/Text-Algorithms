from collections import deque

# ----------------------
# Data structure
# ----------------------


class Accepting:
    def __init__(self, i):
        self.i = i

    def __str__(self):
        return f'Accepting({self.i})'

    def __repr__(self):
        return self.__str__()


class NotAccepting:
    def __str__(self):
        return 'NoT Accepting'

    def __repr__(self):
        return self.__str__()


class Undefined:
    pass


UNDEFINED = Undefined()
NOT_ACCEPTING = NotAccepting()


class Node:
    def __init__(self, v, id):
        self.children_dict = {}
        self.id = id
        self.v = v
        self.output = NOT_ACCEPTING
        self.fail = self

    def get_node(self, v):
        if v in self.children_dict:
            return self.children_dict[v]
        else:
            return UNDEFINED

    def get_chidren(self):
        return self.children_dict.values()

    def put_edge(self, v, id):
        newChild = Node(v, id)
        self.children_dict[v] = newChild

        return newChild

    def put_fail(self, fail_node):
        self.fail = fail_node

    def get_fail(self):
        return self.fail

    def add_accepting(self, other):
        """ Note that other should be an accepting state! """
        if self.output == NOT_ACCEPTING:
            self.output = set()
        self.output |= other.output

    def set_accepting(self, i):
        self.output = set([Accepting(i)])

    def is_accepting(self):
        return self.output != NOT_ACCEPTING

    def __str__(self):
        return '---Node---\n' + self.str_rec(spaces=0) + '-' * 64 + '\n'

    def __repr__(self):
        return self.__str__()

    def str_rec(self, spaces):
        s = ' ' * spaces + \
            f'Node#{self.id}, v = {self.v}, output = {self.output}, fail = {self.fail.id}'
        s += '\n'
        if self.get_chidren():
            for kid in self.get_chidren():
                s += kid.str_rec(spaces + 1)

        return s


class Root(Node):
    """ Root contains self-loop so that when it fails to match it goes back to itself"""

    def __init__(self):
        super().__init__('ROOT', 0)

    def get_node(self, character):
        if character in self.children_dict:
            return self.children_dict[character]
        else:
            return self

    def get_fail(self):
        return self

    def __str__(self):
        return '---Root---\n' + self.str_rec(spaces=0) + '-' * 64 + '\n'

# ----------------------
# Actual implementation
# ----------------------


def pre_aho_corasik(patterns):
    """
        Preprocessing for Aho-Corasik algorithm.
    """
    # Add self-loop for all characters
    root = Root()
    id = 1

    # Enter each pattern
    for i, pattern in enumerate(patterns):
        id = enter(i, id, pattern, root)

    # Add failure links
    complete(root)

    return root


def enter(pattern_idx, id, pattern, root):
    """ Enters patterns into trie """

    m = len(pattern)
    r = root
    i = 0
    # Follow exisitng edges
    while i < m:
        s = r.get_node(pattern[i])
        if s == UNDEFINED or s == r:
            break
        r = s
        i += 1

    # Create new edges
    while i < m:
        s = r.put_edge(pattern[i], id)
        id += 1
        r = s
        i += 1

    # Set last state as accepting
    r.set_accepting(pattern_idx)
    return id


def complete(root):
    """ Adds failure links """
    q = deque()
    l = root.get_chidren()
    for r in l:
        q.append(r)
        r.put_fail(root)

    while q:
        r = q.popleft()
        l = r.get_chidren()
        for p in l:
            c = p.v
            q.append(p)
            s = r.get_fail()
            u = s.get_node(c)
            while u == UNDEFINED:
                s = s.get_fail()
                u = s.get_node(c)
            p.put_fail(u)
            # Here we could add another accepting state! FIXME
            if u.is_accepting():
                p.add_accepting(u)


def aho_corasik(y, patterns):
    # Preprocessing
    r = pre_aho_corasik(patterns)
    # Searching
    for v in y:
        s = r.get_node(v)
        while s == UNDEFINED:
            r = r.get_fail()
            s = r.get_node(v)
        r = s

    return r
