from ..lambda_calculus.lambda_ast import Abstr, Var, AndOpr, Apply, Const, ImpliesOpr, Exists, ForAll
from .dep_tree import DepTree
from warnings import warn


def _word(word: str):
    return Abstr([Var('x')], Apply(Const(word), Var('x')))
def _copy(rel: str): 
    return Abstr(
        [Var('f'), Var('g'), Var('z')],
        Exists([Var('x')], AndOpr(
            Apply(Var('f'), Var('z')),
            Apply(Var('g'), Var('x')), 
            Apply(Const(rel), Var('z'), Var('x'))
        ))
    )
def _invert(rel: str):
    return Abstr(
        [Var('f'), Var('g'), Var('z')],
        Exists([Var('x')], AndOpr(
            Apply(Var('f'), Var('z')),
            Apply(Var('g'), Var('x')), 
            Apply(Const(rel), Var('x'), Var('z'))
        ))
    )
def _coord(rel: str):
    return Abstr(
            [Var('f'), Var('g'), Var('z')],
            Exists( [Var('x'), Var('y')], AndOpr(
                Apply(Var('f'), Var('x')), 
                Apply(Var('g'), Var('y')), 
                Apply(Const(rel), Var('z'), Var('x'), Var('y'))
            ))
        )
def _merge():
    return Abstr(
        [Var('f'), Var('g'), Var('z')],
        AndOpr(Apply(Var('f'), Var('z')), Apply(Var('g'), Var('z')))
    )
def _head():
    return Abstr(
        [Var('f'), Var('g'), Var('z')],
        Apply(Var('f'), Var('z'))
    )

# TODO: comment represents things needed to be done in the future
n2l_common_dict = {
    "nsubj": _copy("arg1"),
    "dobj": _copy("arg2"),
    "nsubjpass": _copy("arg2"),
    "iobj": _copy("arg3"),
    "agent": _copy("arg2"),
    "acomp": _copy("arg2"),
    "csubj": _copy("arg1"),
    "csubjpass": _copy("arg2"),
    "attr": _copy("arg2"),
    "expl": _copy("arg1"),

    "relcl": _copy("relcl"),
    "pcomp": _copy("pcomp"),
    "preconj": _copy("preconj"),
    "prep": _copy("prep"),
    "pobj": _copy("pobj"),
    "poss": _copy("belongs"),
    "ccomp": _copy("ccomp"),
    "xcomp": _copy("xcomp"), # NOTE: preprocessed
    "prt": _copy("prt"), # NOTE: preprocessed
    "npadvmod": _copy("npadvmod"),

    "conj": _coord("conj"),
    "compound": _copy("compound"), # NOTE: preprocessed
    "advmod": _coord("advmod"),

    "acl": _invert("acl"),
    "advcl": _invert("advcl"),

    "appos": _merge(),
    "amod": _merge(),
    "nummod": _merge(),

    "cc": _head(),
    "punct": _head(),
    "case": _head(), # combining modifiers
    "nmod": _head(), # with case_maker
    "quantmod": _head(),
    "det": _head(), # quantification
    "predet": _head(),
    "aux": _head(), # combining verb phrases
    "auxpass": _head(),
    "dep": _head(),
    "parataxis": _head(),
    "intj": _head(),
    "mark": _head(),
}
def node_to_lambda(node: DepTree):
    """
    NOTE: exists operation is implicit
    """
    if node.is_word():
        return _word(node.label())
    
    if node.label() in n2l_common_dict:
        return n2l_common_dict[node.label()]
    
    def case(lbl: str): 
        return lbl == node.label()
    
    if case('neg'): 
        return Abstr(
            [Var('f'), Var('g'), Var('z')], 
            AndOpr(
                Apply(Var('f'), Var('z')), Apply(Const("not"), Var('z'))
            )
        )

    # raise Exception("Label {} is not implemented".format(node.label()))
    warn(f"Label {node.label()} is not implemented. Defaults to ignore")
    return _head()


class Dep2Lambda: 
    def __init__(self) -> None:
        pass

    def get(self, node: DepTree):
        return node_to_lambda(node)