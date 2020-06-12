from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
import string

# TODO:
#   - initial parse:
#       - add implicit concatenation operators (bullet -> \u2022)
#       - convert [foo] to (..|..|..|)
#   - convert given expression to postfix notation -> The Shunting-Yard Algorithm
#   - convert postifx expression to NFA
#   - implement efficient searching..


@dataclass
class Operator:
    char: str


# I could get rid of these..
ConcatOp = Operator('\u2022')  # both
UnionOp = Operator('|')  # either one
ClosureOp = Operator('*')  # zero or more
PlusOp = Operator('+')  # one or more
QuestOp = Operator('?')  # zero or one

OperatorSet = {'\u2022', '|', '*', '+', '?'}


def compile(regex):
    parsed = initial_parse(regex)
    postfix = to_postfix(parsed)

    return to_NFA(postfix)


class NFAState:
    def __init__(self, is_accepting):
        self.is_accepting = is_accepting
        self.transitions = {}
        self.epsilon_transitions = []
        self.dot_transition = None

    def add_eps_transition(self, to):
        self.epsilon_transitions.append(to)

    def add_transition(self, symbol, to):
        self.transitions[symbol] = to

    def add_dot_transition(self, to):
        self.dot_transition = to


def add_next_state(state, nexxt, visited):
    """
        Procedure for discarding eps transitions used NFA.search.
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
                if v in state.transitions or state.dot_transition is not None:
                    add_next_state(state, nexxt, set())

            current = nexxt

        for state in current:
            if state.is_accepting:
                return True

        return False

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


def ord_between(start, end):
    """
        Creates set of all characters in between start and end (between in ascii table sense).
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
            if expr[i + 1] == 'd':
                accepted |= set(string.digits)
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
    concat_chr = ConcatOp.char

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
        The Shunting-Yard Algorithm

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
                    and (operator_stack[-1] != ConcatOp.char or v == ConcatOp.char):
                popped = operator_stack.pop()
                postifx.append(popped)

            operator_stack.append(v)
        else:
            postifx.append(v)

    while len(operator_stack) > 0:
        popped = operator_stack.pop()
        postifx.append(popped)

    return ''.join(postifx)
