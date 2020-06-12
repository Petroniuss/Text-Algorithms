from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
import string

ConcatOp = '\u2022'
OperatorSet = {'\u2022', '|', '*', '+', '?'}


def compile(regex):
    """
        Compiles given regex => converts to Nondeterministic Finite Automaton (NFA).

        Usage: after compiling regex you can use .matches(foo).
    """
    parsed = initial_parse(regex)
    postfix = to_postfix(parsed)

    return to_NFA(postfix)


class NFAState:
    id_gen = 0

    def __init__(self, is_accepting):
        self.is_accepting = is_accepting
        self.transitions = {}
        self.epsilon_transitions = []
        self.dot_transition = None
        self.id = NFAState.id_gen + 1

        NFAState.id_gen += 1

    def add_eps_transition(self, to):
        self.epsilon_transitions.append(to)

    def add_transition(self, symbol, to):
        self.transitions[symbol] = to

    def add_dot_transition(self, to):
        self.dot_transition = to

    def __str__(self):
        return f'q#{self.id}, is_accepting: {self.is_accepting}, transitions: {self.transitions.keys()}'

    def __repr__(self):
        return str(self)

    def __hash__(self):
        return self.id


def add_next_state(state, nexxt, visited):
    """
        Procedure for discarding epsilon-transitions used by NFA.search.
    """
    if len(state.epsilon_transitions) > 0:
        for st in state.epsilon_transitions:
            if st not in visited:
                visited.add(st)
                add_next_state(st, nexxt, visited)
    else:
        nexxt.append(state)


@dataclass
class NFA:
    start: NFAState
    end: NFAState

    def matches(self, pattern):
        current = []
        add_next_state(self.start, current, set())

        for v in pattern:
            nexxt = []
            for state in current:
                if v in state.transitions:
                    add_next_state(state.transitions[v], nexxt, set())
                elif state.dot_transition is not None:
                    add_next_state(state.dot_transition, nexxt, set())

            current = nexxt

        return any([state.is_accepting for state in current])

    @staticmethod
    def from_eps() -> NFA:
        start = NFAState(False)
        end = NFAState(True)

        start.add_eps_transition(end)

        return NFA(start, end)

    @staticmethod
    def from_symbol(symbol) -> NFA:
        start = NFAState(False)
        end = NFAState(True)

        start.add_transition(symbol, end)

        return NFA(start, end)

    @staticmethod
    def from_dot() -> NFA:
        start = NFAState(False)
        end = NFAState(True)

        start.add_dot_transition(end)

        return NFA(start, end)

    def concat(self, other: NFA) -> NFA:
        self.end.add_eps_transition(other.start)
        self.end.is_accepting = False

        return NFA(self.start, other.end)

    def union(self, other: NFA) -> NFA:
        start = NFAState(False)
        start.add_eps_transition(self.start)
        start.add_eps_transition(other.start)

        end = NFAState(True)
        self.end.add_eps_transition(end)
        other.end.add_eps_transition(end)

        self.end.is_accepting = False
        other.end.is_accepting = False

        return NFA(start, end)

    def closure(self) -> NFA:
        start = NFAState(False)
        end = NFAState(True)

        start.add_eps_transition(end)
        start.add_eps_transition(self.start)
        self.end.add_eps_transition(self.start)
        self.end.add_eps_transition(end)

        self.end.is_accepting = False

        return NFA(start, end)

    def one_or_more(self) -> NFA:
        start = NFAState(False)
        end = NFAState(True)

        start.add_eps_transition(self.start)
        self.end.add_eps_transition(self.start)
        self.end.add_eps_transition(end)

        self.end.is_accepting = False

        return NFA(start, end)

    def zero_or_one(self) -> NFA:
        start = NFAState(False)
        end = NFAState(True)

        start.add_eps_transition(end)
        start.add_eps_transition(self.start)
        self.end.add_eps_transition(end)

        self.end.is_accepting = False

        return NFA(start, end)


def to_NFA(expr):
    """
        Converts previously parsed postfix exprresion to NFA.
    """
    if expr == '':
        return NFA.from_eps()

    stack = []
    for token in expr:
        if token == '*':
            stack.append(stack.pop().closure())
        elif token == '+':
            stack.append(stack.pop().one_or_more())
        elif token == '?':
            stack.append(stack.pop().zero_or_one())
        elif token == '|':
            right = stack.pop()
            left = stack.pop()
            stack.append(left.union(right))
        elif token == '\u2022':
            right = stack.pop()
            left = stack.pop()
            stack.append(left.concat(right))
        elif token == '.':
            stack.append(NFA.from_dot())
        else:
            stack.append(NFA.from_symbol(token))

    return stack.pop()

# -------------------------------- INITIAL PARSING ---------------------------------------------------------


def ord_between(start, end):
    """
        Creates set of all characters between start and end (between in ascii table sense).
    """
    st_ord, end_ord = ord(start), ord(end)
    if end_ord < st_ord:
        raise Exception('Invalid interval!')

    st = set()
    for i in range(st_ord, end_ord + 1):
        st.add(chr(i))

    return st


def parse_bracket(expr):
    """
        Converts characters inside square brackets (expr) to union.
        For example 'a-c12' => '(a|b|c|1|2)'

        Character classes supported:
            - \d <=> 0-9
            Todo: check for other character classes!

        Note that input shouldn't contain square brackets!
    """
    if len(expr) < 2:
        return '(' + expr + ')'

    left, i = None, 0
    accepted = set()
    while i < len(expr):
        v = expr[i]
        # character class
        if v == '\\':
            # escape character
            if i + 1 >= len(expr) or expr[i + 1] == '\\':
                accepted.add(v)
            # digit class
            elif expr[i + 1] == 'd':
                accepted |= set(string.digits)
            # word class
            elif expr[i + 1] == 'w':
                accepted |= set(string.ascii_letters + string.digits + '_')
            # whitespace class
            elif expr[i + 1] == 's':
                accepted |= set(string.whitespace)
            i += 2
        # interval
        elif v == '-':
            if i == len(expr) - 1 or i == 0:
                accepted.add('-')
            else:
                left = expr[i - 1]
            i += 1
        # any other character
        else:
            # add interval
            if left is not None:
                right = v
                accepted |= ord_between(left, right)
                left = None
            # add one character
            else:
                accepted.add(v)

            i += 1

    # construct union
    union = []
    for v in accepted:
        union.extend([v, '|'])

    return '(' + ''.join(union[:-1]) + ')'


def initial_parse(expr):
    """
        Adds implicit concat symbols (bullet \u2022) and transforms all square brackets into unions.

        For example: 12[a-c]* => 1$2$(a|b|c)*
            where $ stands for union character \u2022.
    """
    op_set = set(['+', '*', '?', ')', '|'])
    concat_chr = ConcatOp

    parsed = []
    i, n = 0, len(expr)
    while i < n:
        v = expr[i]

        if v == '[':
            j = i + 1
            while j < n and expr[j] != ']':
                j += 1

            if j == n:
                raise Exception('Invalid bracket!')
            else:
                if i != 0:
                    parsed.append(concat_chr)
                parsed.extend(list(parse_bracket(expr[i + 1:j])))
                i = j + 1

        elif v in op_set:
            parsed.append(v)
            i += 1
        else:
            if i != 0 and expr[i - 1] not in set(['(', '|']):
                parsed.append(concat_chr)
            parsed.append(v)
            i += 1

    return ''.join(parsed)


def to_postfix(expr):
    """
        'The Shunting-Yard Algorithm'

        Converts previously parsed expression to postifx notation.

        Note, there might be a bug in here!
    """
    postifx, operator_stack = [], []

    for v in expr:
        if v == '(':
            operator_stack.append(v)
        elif v == ')':
            while len(operator_stack) > 0 and operator_stack[-1] != '(':
                popped = operator_stack.pop()
                postifx.append(popped)

            operator_stack.pop()

        elif v in OperatorSet:
            while len(operator_stack) > 0 and operator_stack[-1] != '(' \
                    and (operator_stack[-1] != ConcatOp or v == ConcatOp):
                popped = operator_stack.pop()
                postifx.append(popped)

            operator_stack.append(v)
        else:
            postifx.append(v)

    while len(operator_stack) > 0:
        popped = operator_stack.pop()
        postifx.append(popped)

    return ''.join(postifx)
