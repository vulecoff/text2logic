from ..lambda_calculus.lambda_ast import LambdaExpr, Abstr, Apply, AndOpr, Const, Var
from typing import List, Callable

def _find_expr(ls: List[LambdaExpr], condition: Callable[[LambdaExpr], bool]):
    for e in ls: 
        if condition(e):
            return e
    return None

def _find_expr_all(ls: List[LambdaExpr], condition: Callable[[LambdaExpr], bool]) -> List[LambdaExpr]: 
    ret = []
    for e in ls: 
        if condition(e): 
            ret.append(e)
    return ret

def _conj(expr: Abstr) -> Abstr: 
    assert isinstance(expr.body, AndOpr)
    
    target_old = []
    target_transformed = []
    found = 0
    for i in range(len(expr.body.operands)):
        op: Apply = expr.body.operands[i]
        for j in range(i+1, len(expr.body.operands)):
            op2: Apply = expr.body.operands[j]
            if isinstance(op, Apply) and isinstance(op.functor, Const) and op.functor.symbol == "conj" \
                    and isinstance(op2, Apply) and isinstance(op2.functor, Const) and op2.functor.symbol.startswith("arg") and \
                    op2.arguments[1] == op.arguments[0]:
                found += 1
                target_transformed.extend([
                    Apply(op2.functor, op2.arguments[0], op.arguments[1]),
                    Apply(op2.functor, op2.arguments[0], op.arguments[2])
                ])
                target_old.extend([op,op2])
    
    if found == 0: 
        raise Exception("No matching predicates found for \'conj or arg\'")
    elif found > 1:
        raise Exception("Only one pair is expected, but found {}".format(found))
    
    postprocessed = [op for op in expr.body.operands if op not in target_old] + target_transformed
    return Abstr(expr.parameters, AndOpr(*postprocessed))

def _preposition(expr: Abstr) -> Abstr: 
    assert isinstance(expr.body, AndOpr)
    prep: Apply = _find_expr(expr.body.operands, 
                      lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.functor.symbol == "prep"
                      )
    pobj: Apply = _find_expr(expr.body.operands, 
                      lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.functor.symbol == "pobj"
                      )
    prep_word: Apply = _find_expr(expr.body.operands,
                        lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.arguments[0] == prep.arguments[1]
                        )
    if prep == None or pobj == None or prep_word == None: 
        raise Exception(f"Cannot match \'prep, pboj, or prep_word\' in {expr}")
    
    new_body_operands = [op for op in expr.body.operands if op not in [prep, pobj, prep_word]]
    new_body_operands.append(Apply(
        Const("prep." + prep_word.functor.symbol), 
        prep.arguments[0], 
        pobj.arguments[1]))
    return Abstr(expr.parameters, AndOpr(*new_body_operands))


# def _combine_advmod(expr: Abstr) -> Abstr: 
#     dep = "advmod"
#     assert isinstance(expr.body, AndOpr)
#     targ_pred: Apply = _find_expr(expr.body.operands, 
#                            lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.functor.symbol == dep
#                            )
#     if targ_pred == None:
#         raise Exception(f"No \'{dep}\' predicate matched in expr {expr}")
#     root_word: Apply = _find_expr(expr.body.operands,
#                 lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.arguments[1] == targ_pred.arguments[1]
#                            )
#     if root_word == None: 
#         raise Exception(f"No root word found for relation {dep} in expr {expr}")
#     all_targ_preds: List[Apply] = _find_expr_all(expr.body.operands, 
#                 lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and \
#                 x.functor.symbol == dep and  x.arguments[1] == root_word.arguments[1]
#                         )
#     assert len(all_targ_preds) == 1 # NOTE: assume that there is only one advmod connected to the root
#     targ_words_pred = [_find_expr(expr.body.operands, \
#                             lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) \
#                                     and 
#                             )   \
#                        for e in all_targ_preds]
    

class PostProcessor:
    def __init__(self) -> None:
        pass

    def process(self, expr: Abstr) -> Abstr:
        postproc_deps = ["conj", "preposition"]
        for l in postproc_deps:
            while True: 
                t = None
                try: 
                    t = self.process_by_dep(l, expr)
                except Exception as e: 
                    print("Post processing for {} skipped.".format(l))
                    print("Reason: ", e)
                if t != None: 
                    expr = t
                else: 
                    break
        return expr
    
    def process_by_dep(self, dep_label: str, expr: Abstr) -> Abstr:
        expr = self.flatten_and_validate(expr)

        def case(l: str):
            return dep_label == l
        
        if case("conj"): 
            return _conj(expr)
        elif case("preposition"):
            return _preposition(expr)
        
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
        