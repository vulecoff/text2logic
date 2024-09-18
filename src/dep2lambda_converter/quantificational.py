from ..lambda_calculus.lambda_ast import Abstr, Var, AndOpr, Apply, Const, ImpliesOpr, Exists, ForAll, Neg
from ..u_dep.dep_tree import DepTree
from warnings import warn


# Implements UD version 2


def quant_converter(node: DepTree):
    def case(label: str):
        return node.label() == label
    if node.is_word():
        if node.is_event():
            return Abstr(
                [Var('f')], 
                Exists([Var('e')], 
                       AndOpr(Apply(Const(node.label()), Var('e')), Apply(Var('f'), Var('e'))))
            )
        elif node.is_individual():
            return Abstr([Var('f')], Apply(Var('f'), Const(node.label())))
        return Abstr(
            [Var('x')],
                Apply(Const(node.label()), Var('x')), 
        )
        
    if case("det:univ"):
        return  Abstr([Var('f'), Var('_'), Var("P")], ForAll(
            [Var('x')], ImpliesOpr(
                Apply(Var('f'), Var('x')), Apply(Var('P'), Var('x'))
            )
        ))
    elif case('det:exis'):
        return  Abstr([Var('f'), Var('_'), Var("P")], Exists(
            [Var('x')], AndOpr(
                Apply(Var('f'), Var('x')), Apply(Var('P'), Var('x'))
            )
        ))
    elif case("nsubj"):
        return Abstr([Var('P'), Var('Q'), Var('f')], Apply(
                    Var('Q'), Abstr([Var('x')], Apply(
                        Var('P'), Abstr([Var('e')], AndOpr(
                            Apply(Var('f'), Var('e')), Apply(Const('ag'), Var('e'), Var('x'))
                        ))
                    ))
                ))
    elif case("obj"):
        return Abstr([Var('P'), Var('Q'), Var('f')], Apply(
                    Var('Q'), Abstr([Var('x')], Apply(
                        Var('P'), Abstr([Var('e')], AndOpr(
                            Apply(Var('f'), Var('e')), Apply(Const('th'), Var('e'), Var('x'))
                        ))
                    ))
                ))
    elif case("neg"):
        return Abstr([Var('P'), Var('_'), Var('f')], Neg(Apply(Var('P'), Var('f'))))
    elif case("advmod"):
        return Abstr([Var('P'), Var('Q'), Var('f')], Apply(
            Var('P'), Abstr([Var('e')], AndOpr(
                Apply(Var('Q'), Var('e')), 
                Apply(Var('f'), Var('e'))
            ))
        ))
    elif case("conj"):
        return Abstr([Var('P'), Var('Q'), Var('f')], AndOpr(
            Apply(Var('P'), Var('f')), 
            Apply(Var('Q'), Var('f'))
        ))
    elif case("aux") or case("cc") or case('cop'):
        # identity
        return Abstr([Var('P'), Var('Q')], Var('P'))
    raise Exception("Unimplemented dependency \'{}\'".format(node.label()))
