"""
Functions to process and evaluate Lambda Expressions
"""
from .lambda_ast import LambdaExpr, Var, Const, AndOpr, Abstr, Apply, ImpliesOpr, Exists, ForAll
from copy import deepcopy
from typing import Union, List

invalid_expr_msg = "Unexpected expression type {} for {}"

def free_vars(expr: LambdaExpr):
    """
    Get all free variables inside an expression
    """
    if isinstance(expr, Var):
        return {expr.symbol}
    elif isinstance(expr, AndOpr):
        res = set()
        for o in expr.operands:
            res = res | free_vars(o)
        return res
    elif isinstance(expr, Abstr):
        return free_vars(expr.body) - set(list(map(str, expr.parameters)))
    elif isinstance(expr, Apply):
        res = free_vars(expr.functor)
        for a in expr.arguments:
            res = res | free_vars(a)
        return res
    elif isinstance(expr, Const):
        return set()
    elif isinstance(expr, ForAll) or isinstance(expr, Exists):
        return free_vars(expr.formula) - set(list(map(str, expr.vars)))
    elif isinstance(expr, ImpliesOpr): 
        return free_vars(expr.lhs) | free_vars(expr.rhs)
    
    raise Exception(invalid_expr_msg.format(type(expr), expr))
    return None

def bound_vars(expr: LambdaExpr):
    """
    Return all bound variables
    """
    if isinstance(expr, Var) or isinstance(expr, Const):
        return set()
    elif isinstance(expr, AndOpr):
        res = set()
        for o in expr.operands:
            res = res | free_vars(o)
        return res
    elif isinstance(expr, Abstr):
        return free_vars(expr.body) | set(list(map(str, expr.parameters)))
    elif isinstance(expr, Apply):
        res = free_vars(expr.functor)
        for a in expr.arguments:
            res = res | free_vars(a)
        return res
    elif isinstance(expr, ForAll) or isinstance(expr, Exists):
        return free_vars(expr.formula) | set(list(map(str, expr.vars)))
    elif isinstance(expr, ImpliesOpr): 
        return free_vars(expr.lhs) | free_vars(expr.rhs)
    
    raise Exception(invalid_expr_msg.format(type(expr), expr))
    return None

def used_vars(expr: LambdaExpr):
    """ Variable names that are actually used, 
        not including Exists/ForAll/Abstr var declarations
        TODO: bound + free = used. All = used + unused
    """
    if isinstance(expr, Var):
        return {expr.symbol}
    elif isinstance(expr, AndOpr):
        res = set()
        for o in expr.operands:
            res = res | used_vars(o)
        return res
    elif isinstance(expr, Abstr):
        return used_vars(expr.body)
    elif isinstance(expr, Apply):
        res = used_vars(expr.functor)
        for a in expr.arguments:
            res = res | used_vars(a)
        return res
    elif isinstance(expr, Const):
        return set()
    elif isinstance(expr, ForAll) or isinstance(expr, Exists):
        return used_vars(expr.formula)
    elif isinstance(expr, ImpliesOpr): 
        return used_vars(expr.lhs) | used_vars(expr.rhs)
    
    raise Exception(invalid_expr_msg.format(type(expr), expr))
    return None

def alpha_reduce(expr: LambdaExpr, to_replace: str, replacement: str) -> Union[Abstr, Exists, ForAll]: 
    """
    Replace all free occurrences of var to_replace inside expr
    """
    def _alpha_reduce(expr: LambdaExpr, to_replace: str, replacement: str): 
        """ Original Lambda split into Lx.expr : expr is body, x is lambda identity 
        """
        if isinstance(expr, Var):
            if expr.symbol == to_replace: 
                return Var(replacement)
            else: 
                return Var(expr.symbol)
        elif isinstance(expr, Apply): 
            return Apply(
                _alpha_reduce(expr.functor, to_replace, replacement),
                *[_alpha_reduce(arg, to_replace, replacement) for arg in expr.arguments]
            )
        elif isinstance(expr, Abstr):
            if to_replace in list(map(str, expr.parameters)):  # TODO: requires more test here
                # all occurrences of to_replace will be bound in expr -- skipped
                return deepcopy(expr)
            else:    
                return Abstr(deepcopy(expr.parameters), _alpha_reduce(expr.body, to_replace, replacement))
        elif isinstance(expr, Exists) or isinstance(expr, ForAll): # same as Abstr
            if to_replace in list(map(str, expr.vars)):  
                return deepcopy(expr)
            else:    
                cls = Exists if isinstance(expr, Exists) else ForAll
                return cls(deepcopy(expr.vars), _alpha_reduce(expr.formula, to_replace, replacement))
        elif isinstance(expr, Const):
            return deepcopy(expr)
        elif isinstance(expr, AndOpr):
            return AndOpr(*[_alpha_reduce(o, to_replace, replacement) for o in expr.operands])
        elif isinstance(expr, ImpliesOpr):
            return ImpliesOpr(
                _alpha_reduce(expr.lhs, to_replace, replacement),
                _alpha_reduce(expr.rhs, to_replace, replacement)
            )
        
        raise Exception(invalid_expr_msg.format(type(expr), expr))
        return None
        
    if isinstance(expr, Abstr):
        params = deepcopy(expr.parameters)
        param_names = list(map(str, params))
        if to_replace not in param_names: 
            raise Exception("Variable to_replace {} is not in expression parameters {}.".format(to_replace, expr))
        
        replace_idx = param_names.index(to_replace)
        params[replace_idx] = Var(replacement)
        return Abstr(params, _alpha_reduce(expr.body, to_replace, replacement))
    elif isinstance(expr, Exists) or isinstance(expr, ForAll):
        vars = deepcopy(expr.vars)
        var_names = list(map(str, vars))
        if to_replace not in var_names: 
            raise Exception("Variable to_replace {} is not in expression parameters {}.".format(to_replace, expr))
        replace_idx = var_names.index(to_replace)
        var_names[replace_idx] = Var(replacement)
        cls = Exists if isinstance(expr, Exists) else ForAll
        return cls(var_names, _alpha_reduce(expr.formula, to_replace, replacement))

    raise Exception("Invalid Expr Type {}. Expected Abstr/Exists/ForAll, but get {}".format(expr, type(format)))


def _substitute(expr: LambdaExpr, to_replace: str, arg: LambdaExpr):
    """
    Lx.expr) arg
    Alpha conversion by priming variable_name x -> x'
    """
    if isinstance(expr, Var): 
        if expr.symbol == to_replace: 
            return deepcopy(arg)
        else: 
            return deepcopy(expr)
    elif isinstance(expr, Const):
        return deepcopy(expr)
    elif isinstance(expr, Abstr):
        _, lambda_id = expr.split()
        param_symbols = [e.symbol for e in expr.parameters]
        if to_replace in param_symbols: # to_replace is bound. Skip substituting
            return deepcopy(expr)
        else: 
            if lambda_id not in free_vars(arg):
                return Abstr(deepcopy(expr.parameters), _substitute(expr.body, to_replace, arg)) 
            else: # name conflict
                reduced = alpha_reduce(expr, lambda_id, lambda_id + "\'")
                return Abstr(reduced.parameters, _substitute(reduced.body, to_replace, arg))
    elif isinstance(expr, Exists) or isinstance(expr, ForAll):
        lambda_id = expr.vars[0].symbol
        var_symbols = [e.symbol for e in expr.vars]
        if to_replace in var_symbols: 
            return deepcopy(expr)
        else: 
            cls = Exists if isinstance(expr, Exists) else ForAll
            if lambda_id not in free_vars(arg):
                return cls(deepcopy(expr.vars), _substitute(expr.formula, to_replace, arg))
            else: 
                reduced = alpha_reduce(expr, lambda_id,lambda_id + "\'")
                return cls(reduced.vars, _substitute(reduced.formula, to_replace, arg))
    elif isinstance(expr, AndOpr):
        return AndOpr(*[_substitute(o, to_replace, arg) for o in expr.operands])
    elif isinstance(expr, Apply):
        return Apply(_substitute(expr.functor, to_replace, arg), *[_substitute(a,to_replace, arg) for a in expr.arguments])
    elif isinstance(expr, ImpliesOpr):
        return ImpliesOpr(
            _substitute(expr.lhs, to_replace, arg),
            _substitute(expr.rhs, to_replace, arg)
        )
    
    raise Exception(invalid_expr_msg.format(type(expr), expr))
    return None

   
def beta_reduce(expr: LambdaExpr, max_iter=100, show_step=False): 
    """Beta reduction in normal order (leftmost-outermost order)""" 

    def _beta_reduce_step(expr: LambdaExpr, leftmost_outermost_reduced: list):
        if isinstance(expr, Var) or isinstance(expr, Const):
            return deepcopy(expr)
        elif isinstance(expr, Abstr):
            return Abstr(deepcopy(expr.parameters), _beta_reduce_step(expr.body, leftmost_outermost_reduced))
        elif isinstance(expr, Apply):
            if isinstance(expr.functor, Abstr) and not leftmost_outermost_reduced[0]:
                leftmost_outermost_reduced[0] = True
                rest, lambda_id = expr.functor.split()
                if len(expr.arguments) == 0:
                    raise Exception("Expression is of type Application but with no arguments: {}".format(expr))
                subs = _substitute(rest, lambda_id, expr.arguments[0])
                if len(expr.arguments) <= 1:
                    return subs
                return Apply(subs, *expr.arguments[1:])
            else: 
                return Apply(_beta_reduce_step(expr.functor, leftmost_outermost_reduced),
                              *[_beta_reduce_step(a, leftmost_outermost_reduced) for a in expr.arguments])
        elif isinstance(expr, AndOpr):
            return AndOpr(*[_beta_reduce_step(o, leftmost_outermost_reduced) for o in expr.operands])
        elif isinstance(expr, ImpliesOpr):
            return ImpliesOpr(
                _beta_reduce_step(expr.lhs, leftmost_outermost_reduced),
                _beta_reduce_step(expr.rhs, leftmost_outermost_reduced)
            )
        elif isinstance(expr, Exists) or isinstance(expr, ForAll):
            cls = Exists if isinstance(expr, Exists) else ForAll
            return cls(deepcopy(expr.vars), _beta_reduce_step(expr.formula, leftmost_outermost_reduced))
        
        raise Exception(invalid_expr_msg.format(type(expr), expr))
        return None
    
    cur = expr
    normal_form = False
    cur_iter = 0
    while not normal_form: 
        leftmost_outermost_reduced = [False]
        if show_step: 
            print(f"Step {cur_iter}: {LambdaExpr.colored_repr(cur)}")
        nxt = _beta_reduce_step(cur, leftmost_outermost_reduced)
        cur_iter += 1
        normal_form = not leftmost_outermost_reduced[0] # if still reducible, continue another try
        if cur_iter >= max_iter:
                break
        cur = nxt
    if not normal_form: 
        raise Exception(f"Maximum iterations for beta-reduction reached for expression: \
                         {expr}. Last executed reduction: {cur}")
    return cur

from typing import Dict, Generator
def uniqueify_var_names(expr: LambdaExpr, id_incrementer: Generator[str, None, None]):
    """
    Helper function, assign var name inside lambda expr.
    scoped_id_incrementer:
    """
    def _uniqueify_var_names(expr: LambdaExpr, vars_mp: Dict[str, str]):
        if isinstance(expr, Var): 
            name = expr.symbol
            if name not in vars_mp: 
                id = next(id_incrementer)
                vars_mp[name] = id
            return Var(vars_mp[name])
        elif isinstance(expr, AndOpr):
            return AndOpr(*[_uniqueify_var_names(e, vars_mp) for e in expr.operands])
        elif isinstance(expr, Apply):
            return Apply(
                _uniqueify_var_names(expr.functor, vars_mp), 
                *[_uniqueify_var_names(a, vars_mp) for a in expr.arguments]
            )
        elif isinstance(expr, Abstr):
            return Abstr([_uniqueify_var_names(p, vars_mp) for p in expr.parameters], 
                         _uniqueify_var_names(expr.body, vars_mp))
        elif isinstance(expr, Const):
            return Const(expr.symbol)
        elif isinstance(expr, ImpliesOpr):
            return ImpliesOpr(_uniqueify_var_names(expr.lhs, vars_mp), _uniqueify_var_names(expr.rhs, vars_mp))
        elif isinstance(expr, Exists) or isinstance(expr, ForAll):
            cls = Exists if isinstance(expr, Exists) else ForAll
            return cls(
                [_uniqueify_var_names(v, vars_mp) for v in expr.vars],
                _uniqueify_var_names(expr.formula, vars_mp)
            )
        
        raise Exception(invalid_expr_msg.format(type(expr), expr))
    
    dt = {}
    return _uniqueify_var_names(expr, dt)


def assert_unique_vars(expr: LambdaExpr):
    """Assert that all variables are standardized (no var names are reused)
    """
    if isinstance(expr, Abstr):
        for a in expr.parameters: 
            assert a.symbol not in used_vars(expr.body) or a.symbol in free_vars(expr.body)
        assert_unique_vars(expr.body)
    elif isinstance(expr, ForAll) or isinstance(expr, Exists):
        for a in expr.vars: 
            assert a.symbol not in used_vars(expr.formula) or a.symbol in free_vars(expr.formula)
        assert_unique_vars(expr.formula)
    elif isinstance(expr, Apply):
        assert_unique_vars(expr.functor)
        for arg in expr.arguments: 
            assert_unique_vars(arg)
    elif isinstance(expr, AndOpr):
        for opr in expr.operands: 
            assert_unique_vars(opr)
    elif isinstance(expr, ImpliesOpr): 
        assert_unique_vars(expr.lhs)
        assert_unique_vars(expr.rhs)
    elif isinstance(expr, Const) or isinstance(expr, Var):
        return 
    else: 
        raise Exception(invalid_expr_msg.format(type(expr), expr))


def _flatten_AND(expr: AndOpr) -> list:
    ret = []
    for op in expr.operands: 
        if isinstance(op, AndOpr):
            ret.extend(_flatten_AND(op))
        else: 
            ret.append(op)
    return ret

def _flatten(expr: LambdaExpr):
    """
    TODO: requires heavy testing on Prenex Normal Form
    """
    if isinstance(expr, Abstr):
        return Abstr(expr.parameters, _flatten(expr.body))
    elif isinstance(expr, Apply):
        return Apply(_flatten(expr.functor), *[_flatten(e) for e in expr.arguments])
    elif isinstance(expr, Exists) or isinstance(expr, ForAll):
        cls = Exists if isinstance(expr, Exists) else ForAll
        return cls(expr.vars, _flatten(expr.formula))
    elif isinstance(expr, ImpliesOpr):
        return ImpliesOpr(_flatten(expr.lhs), _flatten(expr.rhs))
    elif isinstance(expr, AndOpr):
        forall_q = []
        exists_q = []
        operands = []
        for op in expr.operands: 
            o = _flatten(op)
            while isinstance(o, Exists) or isinstance(o, ForAll):
                if isinstance(o, Exists):
                    exists_q.extend(o.vars)
                else:   
                    forall_q.extend(o.vars)
                o = o.formula
            if isinstance(o, AndOpr):
                operands.extend(_flatten_AND(o))
            else: 
                operands.append(o)
        ret = AndOpr(*operands)
        if len(exists_q) > 0: 
            ret = Exists(exists_q, ret)
        if len(forall_q) > 0: 
            ret = ForAll(forall_q, ret)
        return ret

    elif isinstance(expr, Const) or isinstance(expr, Var):
        return expr
    
    raise Exception(invalid_expr_msg.format(type(expr), expr))

def flatten(expr: LambdaExpr):
    assert_unique_vars(expr)
    return _flatten(expr)