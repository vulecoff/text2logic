"""
Functions to process and evaluate Lambda Expressions
"""
from .lambda_ast import LambdaExpr, Var, Const, AndOpr, Abstr, Apply 
from copy import deepcopy

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
    raise Exception(invalid_expr_msg.format(type(expr), expr))
    return None

def alpha_reduce(expr: LambdaExpr, to_replace: str, replacement: str): 
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
            if to_replace in list(map(str, expr.parameters)): 
                # all occurrences of to_replace will be bound in expr -- skipped
                return deepcopy(expr)
            else:    
                return Abstr(deepcopy(expr.parameters), _alpha_reduce(expr.body, to_replace, replacement))
        elif isinstance(expr, Const):
            return deepcopy(expr)
        elif isinstance(expr, AndOpr):
            return AndOpr(*[_alpha_reduce(o, to_replace, replacement) for o in expr.operands])
        
        raise Exception(invalid_expr_msg.format(type(expr), expr))
        return None
    
    if not isinstance(expr, Abstr): 
        raise Exception("Invalid Expr Type {}. Expected Abstr, but get {}".format(expr, type(format)))
    params = deepcopy(expr.parameters)
    param_names = list(map(str, params))
    if to_replace not in param_names: 
        raise Exception("Variable to_replace {} is not in expression parameters {}.".format(to_replace, expr))
    
    replace_idx = param_names.index(to_replace)
    params[replace_idx] = Var(replacement)
    return Abstr(params, _alpha_reduce(expr.body, to_replace, replacement))


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
        if to_replace == lambda_id: # to_replace is bound. Skip substituting
            return deepcopy(expr)
        else: 
            if lambda_id not in free_vars(arg):
                return Abstr(deepcopy(expr.parameters), _substitute(expr.body, to_replace, arg)) 
            else: # name conflict
                reduced = alpha_reduce(expr, lambda_id, lambda_id + "\'")
                return Abstr(reduced.parameters, _substitute(reduced.body, to_replace, arg))
    elif isinstance(expr, AndOpr):
        return AndOpr(*[_substitute(o, to_replace, arg) for o in expr.operands])
    elif isinstance(expr, Apply):
        return Apply(_substitute(expr.functor, to_replace, arg), *[_substitute(a,to_replace, arg) for a in expr.arguments])
    
    raise Exception(invalid_expr_msg.format(type(expr), expr))
    return None

   
def beta_reduce(expr: LambdaExpr, max_iter=100): 
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
        
        raise Exception(invalid_expr_msg.format(type(expr), expr))
        return None
    
    cur = expr
    normal_form = False
    cur_iter = 0
    while not normal_form: 
        leftmost_outermost_reduced = [False]
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

from typing import Callable, Dict
def uniqueify_var_names(expr: LambdaExpr, scoped_id_incrementer: Callable[[], int]):
    """
    Helper function, assign var name inside lambda expr.
    scoped_id_incrementer:
    """
    def _uniqueify_var_names(expr: LambdaExpr, vars_mp: Dict[str, int]):
        if isinstance(expr, Var): 
            name = expr.symbol
            if name not in vars_mp: 
                id = scoped_id_incrementer()
                vars_mp[name] = id
            new_name = f"<{vars_mp[name]}>"
            return Var(new_name)
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
        
        raise Exception(invalid_expr_msg.format(type(expr), expr))
    
    dt = {}
    return _uniqueify_var_names(expr, dt)