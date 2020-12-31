"""
safe_eval: Takes in a string and preforms math operations on it
This provides many safe checks in order to try and prevent any non math operations.
"""

import ast
import operator as op

_operators = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.BitXor: op.xor,
    ast.USub: op.neg
}


def safe_eval(expr: str) -> int:
    """Evaluates an expression safely"""
    return _eval(ast.parse(expr, mode='eval').body)


def _eval(node):
    """Recursive loop to do math on the expression"""
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return _operators[type(node.op)](_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        return _operators[type(node.op)](_eval(node.operand))
    else:
        raise TypeError(node)
