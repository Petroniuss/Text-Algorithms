from enum import Enum
from dataclasses import dataclass
import string


@dataclass
class Operator:
    char: str


ConcatOp = Operator('\u2022')  # both
UnionOp = Operator('|')  # either one
ClosureOp = Operator('*')  # zero or more
PlusOp = Operator('+')  # one or more
QuestOp = Operator('?')  # zero or one

OperatorSet = {'\u2022', '|', '*', '+', '?'}

# TODO:
#   - initial parse:
#       - add implicit concatenation operators (bullet -> \u2022)
#       - convert [foo] to (..|..|..|)
#   - convert given expression to postfix notation -> The Shunting-Yard Algorithm
#   - ...


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
        For example 'a-c12' => '(a|b|c|1|2')

        Character classes supported:
            - \d <=> 0-9

        Todo: check for other character classes!
    """
    if len(expr) < 2:
        return '(' + expr + ')'

    left = None
    accepted = set()
    for i, v in enumerate(expr):
        # digit class
        if v == '\d':
            accepted |= set(string.digits)
        # interval
        elif v == '-':
            if i == len(expr) - 1 or i == 0:
                accepted.add('-')
            else:
                left = expr[i - 1]
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
