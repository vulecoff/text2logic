from ..lambda_calculus.lambda_ast import Abstr, Var, AndOpr, Apply, Const
from .dep_tree import DepTree

def node_to_lambda(node: DepTree):
    if node.is_word():
        return Abstr([Var('x')], Apply(Const(node.prefixed_label()), Var('x')))
    def case(label: str):
        return node.prefixed_label() == label
    if case("l-nsubj"):
        return Abstr(
            [Var('f'), Var('g'), Var('z')], 
            AndOpr(
                Apply(Var('f'), Var('z')), 
                Apply(Var('g'), Var('x')),
                Apply(Const('arg1'), Var('z'), Var('x'))
            )
        )
    elif case('l-dobj'):
        return Abstr(
            [Var('f'), Var('g'), Var('z')], 
            AndOpr(
                Apply(Var('f'), Var('z')), 
                Apply(Var('g'), Var('x')),
                Apply(Const('arg2'), Var('z'), Var('x'))
            )
        )
    elif case('l-punct'):
        return Abstr([Var('f'), Var('g'), Var('x')], Apply(Var('f'), Var('x')))
    elif case('l-mark'):
        return Abstr(
            [Var('f'), Var('g'), Var('e1')],
            AndOpr(
                Apply(Var('f'), Var('e2')),
                Apply(Var('arg2'), Var('e1'), Var('e2'))
            )
        )
    raise Exception("Label {} is not implemented".format(node.prefixed_label()))


class Dep2Lambda: 

    def __init__(self) -> None:
        pass

    def get(self, node: DepTree):
        return node_to_lambda(node)