from ..lambda_calculus.lambda_ast import LambdaExpr, Abstr, Apply, AndOpr, Const, Var


def _conj(expr: Abstr) -> Abstr: 
    assert isinstance(expr.body, AndOpr)

    conj_pred = None
    for op in expr.body.operands:
        assert isinstance(op, Apply) and isinstance(op.functor, Const)
        if op.functor.symbol == "conj" and len(op.arguments) == 3:
            conj_pred = op
            break
    if conj_pred == None: 
        raise Exception("No \'conj\' predicate matched in expr {}".format(expr))
    head, dep_1, dep_2 = conj_pred.arguments
    new_body_operands = []
    replaced = False
    for op in expr.body.operands: 
        assert isinstance(op, Apply) and isinstance(op.functor, Const)
        if op == conj_pred:
            continue
        elif op.functor.symbol.startswith("arg") and len(op.arguments) == 2 and op.arguments[1] == head:
            replaced = True
            new_body_operands.extend([
                Apply(op.functor, op.arguments[0], dep_1), 
                Apply(op.functor, op.arguments[0], dep_2)
            ])
        else: 
            new_body_operands.append(op)
    if not replaced: 
        raise Exception("No \'arg'\ predicate matched in expr {}".format(expr))
    
    return Abstr(expr.parameters, AndOpr(*new_body_operands))


class PostProcessor:
    def __init__(self) -> None:
        pass

    def process_by_dep(self, dep_label: str, expr: Abstr) -> Abstr:
        expr = self.flatten_and_validate(expr)

        def case(l: str):
            return dep_label == l
        
        if case("conj"): 
            return _conj(expr)
        
        raise Exception("No post-processing step defined for depedency relation {}".format(dep_label))
    
    """TODO: separate flatten and validate
    """
    def flatten_and_validate(self, expr: LambdaExpr): 
        """Shape of the result lambda expression: 
            Le. F(x) & F1(y) & ... 
            a Lambda with one parameter, f-predicates are all grounded
        """
        assert isinstance(expr, Abstr)
        assert len(expr.parameters) == 1
        assert isinstance(expr.body, AndOpr)
        expr = Abstr(expr.parameters, expr.body.flatten())
        for b in expr.body.operands: 

            assert isinstance(b, Apply)
            assert isinstance(b.functor, Const)
            for arg in b.arguments:
                assert isinstance(arg, Var)
        return expr
        