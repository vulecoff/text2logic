from ..lambda_calculus.lambda_ast import LambdaExpr, Abstr, Apply, AndOpr, Const, Var, Exists
from ..lambda_calculus.lambda_processor import flatten, used_vars
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

def _conj(ls: List[Apply]) -> List[Apply]: 
    """Transform exactly one pair
    """
    
    target_old = []
    target_transformed = []
    for op in ls:
        for op2 in ls:
            op: Apply
            op2: Apply
            if op in target_old or op2 in target_old: 
                assert op in target_old and op2 in target_old
                continue
            if isinstance(op, Apply) and isinstance(op.functor, Const) and op.functor.symbol == "conj" \
                    and isinstance(op2, Apply) and isinstance(op2.functor, Const) and op2.functor.symbol.startswith("arg") and \
                    op2.arguments[1] == op.arguments[0]:

                target_transformed.extend([
                    Apply(op2.functor, op2.arguments[0], op.arguments[1]),
                    Apply(op2.functor, op2.arguments[0], op.arguments[2])
                ])
                postprocessed = [op for op in ls if op not in [op, op2]] + target_transformed
                return postprocessed
    raise Exception("No matching predicates found for \'conj or arg\'")

def _preposition(ls: List[Apply]) -> List[Apply]: 
    prep: Apply = _find_expr(ls, 
                      lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.functor.symbol == "prep"
                      )
    pobj: Apply = _find_expr(ls, 
                      lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.functor.symbol == "pobj"
                      )
    prep_word: Apply = _find_expr(ls,
                        lambda x: isinstance(x, Apply) and isinstance(x.functor, Const) and x.arguments[0] == prep.arguments[1]
                        )
    if prep == None or pobj == None or prep_word == None: 
        raise Exception(f"Cannot match \'prep, pboj, or prep_word\' in {expr}")
    
    ret = [op for op in ls if op not in [prep, pobj, prep_word]]
    ret.append(Apply(
        Const("prep." + prep_word.functor.symbol), 
        prep.arguments[0], 
        pobj.arguments[1]))
    return ret

def _args(ls: List[Apply]) -> List[Apply]:
    # TODO: these two needs to be formalized
    def _arg_idx(s: str):
        if s == "arg1": 
            return 0
        elif s == "arg2":
            return 1
        elif s == "arg3":
            return 2
        raise Exception(f"{s} is not defined")
    def _idx_to_arg(s: int):
        return "arg" + str(s + 1)

    root = None
    root_idx = None
    args = [None, None, None]
    for i, op in enumerate(ls):
        for op2 in ls:
            op: Apply
            op2: Apply
            if isinstance(op, Apply) and isinstance(op.functor, Const) \
                    and isinstance(op2, Apply) and isinstance(op2.functor, Const) and op2.functor.symbol.startswith("arg") and \
                    op2.arguments[0] == op.arguments[0]:
                if root == None: 
                    root = op 
                    root_idx = i
                else: 
                    assert root == op
                
                idx = _arg_idx(op2.functor.symbol)
                if args[idx] != None: 
                    raise Exception("Duplicate of {} in relation to {}".format(op2.functor.symbol, op))
                args[idx] = op2            
        if root != None: 
            break
    if root == None: 
        raise Exception("No matching \'arg\' predicates found.")
    for i in range(len(args)): 
        for j in range(len(args)): 
            if i < j and args[i] == None and args[j] != None:
                raise Exception(f"Found {_idx_to_arg(j)} but not {_idx_to_arg(i)} for root {root}")
                # TODO: allows for anonymous entities
    
    new_root = root
    for n in args: 
        if n == None:
            break
        args: List[Apply]
        new_root = Apply(
            new_root.functor, 
            *[*new_root.arguments, n.arguments[1]]
        )
    postprocessed = [op for op in ls]
    postprocessed[root_idx] = new_root
    postprocessed = [op for op in postprocessed if op not in args]
    return postprocessed
    

class PostProcessor:
    def __init__(self) -> None:
        pass

    def process(self, expr: Abstr) -> Abstr:
        expr = flatten(expr)
        self.validate(expr)

        postproc_deps = ["conj", "preposition", "args"] # in order
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
    
    def process_by_dep(self, dep_label: str, expr: LambdaExpr) -> Abstr: 
        if isinstance(expr, Abstr):
            return Abstr(expr.parameters, 
                         self.process_by_dep(dep_label, expr.body)) 
        elif isinstance(expr, Exists):
            f = self.process_by_dep(dep_label, expr.formula)
            in_use = [v for v in expr.vars if v.symbol in self._tmp_used_vars]
            if len(in_use) == 0:
                return f
            return Exists(in_use, f)
        elif isinstance(expr, AndOpr):
            ret = AndOpr(*self._process_by_dep(dep_label, expr.operands))
            self._tmp_used_vars = used_vars(ret)
            return ret
        
        raise Exception("Unexpected expression structure.")
    def _process_by_dep(self, dep_label: str, ls: List[Apply]) -> List[LambdaExpr]:
        def case(l: str):
            return dep_label == l
        
        if case("conj"): 
            return _conj(ls)
        elif case("preposition"):
            return _preposition(ls)
        elif case("args"): 
            return _args(ls)
        
        raise Exception("No post-processing step defined for depedency relation {}".format(dep_label))
    
    """TODO: Ugly code
    """
    def validate(self, expr: LambdaExpr): 
        """
        assert the shape of result expr that postprocessing steps
        Shape of the result lambda expression: 
            Le. ?xyz F(x) & F1(y) & ... 
            a Lambda with one parameter, f-predicates are all grounded
        """
        assert isinstance(expr, Abstr)
        assert len(expr.parameters) == 1
        if isinstance(expr.body, Apply):
            return
        assert isinstance(expr.body, AndOpr) or \
            isinstance(expr.body, Exists)
        
        expr = expr.body
        while isinstance(expr, Exists):
            expr = expr.formula
        assert isinstance(expr, AndOpr)
        for b in expr.operands: 
            assert isinstance(b, Apply)
            assert isinstance(b.functor, Const)
            for arg in b.arguments:
                assert isinstance(arg, Var)
        