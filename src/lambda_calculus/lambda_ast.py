"""
Abstract Syntax Definition for Lambda Calculus
"""
from copy import deepcopy
from typing import Tuple, List

class LambdaExpr:
    """Abstract class for Lambda Expression"""
    def __init__(self):
        pass 

class Var(LambdaExpr):
    def __init__(self, symbol: str):
        self.symbol: str = symbol
    def __str__(self) -> str:
        return self.symbol
    def __repr__(self) -> str:
        return self.symbol
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Var):
            return self.symbol == other.symbol
        return False

class Const(LambdaExpr):
    def __init__(self, symbol: str):
        self.symbol: str = symbol
    def __str__(self) -> str:
        return self.symbol
    def __repr__(self) -> str:
        return self.symbol
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Const):
            return self.symbol == other.symbol
        return False

class Abstr(LambdaExpr):
    """
    Syntatic-sugar multi-parameters lambda
    Lxyz. xyz
    """
    def __init__(self, parameters: List[Var], body):
        if not isinstance(parameters, list):
            raise Exception("Abstraction's parameters are expected to be a list.")
        if len(parameters) == 0:
            raise Exception("Abstraction's parameters are empty.")
        self.parameters = parameters
        self.body = body
    def __str__(self) -> str:
        return "L{}.{}".format("".join(list(map(str, self.parameters))), str(self.body))
    def __repr__(self) -> str:
        return "(L{}.{})".format("".join(list(map(repr, self.parameters))), repr(self.body))
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Abstr):
            is_eq = True
            if len(self.parameters) != len(other.parameters):
                return False
            for i in range(len(self.parameters)):
                is_eq = is_eq and self.parameters[i].__eq__(other.parameters[i])
                if not is_eq:
                    return False
            return self.body.__eq__(other.body)
        return False

    def split(self) -> Tuple[LambdaExpr, str]:       
        """
        Split a (syntatic-sugar) multi-parameters lambda into 2 lambdas
        Return identity of the lambda and its body
        Lxy.xy --> Lx.Ly.xy
        """
        if len(self.parameters) == 0: 
            raise Exception("Attempting to split a Lambda abstraction with no parameters.")
        if len(self.parameters) > 1:
            return Abstr(deepcopy(self.parameters[1:]), self.body), self.parameters[0].symbol
        else: 
            return self.body, self.parameters[0].symbol

class Apply(LambdaExpr):
    """
    Represents an Application expression
    (functor ..args)
    """
    def __init__(self, functor, *arguments):
        self.functor = functor
        self.arguments = list(arguments)
    def __repr__(self):
        return "({} {})".format(repr(self.functor), " ".join(list(map(repr, self.arguments))))
    def __str__(self): 
        """Predicate-style nice print"""
        return "{}({})".format(str(self.functor), ", ".join(list(map(str, self.arguments))))
    def __eq__(self, other):
        if isinstance(other, Apply):
            is_eq = self.functor.__eq__(other.functor)
            if not is_eq:
                return False
            if len(self.arguments) != len(other.arguments):
                return False
            for i in range(len(self.arguments)):
                is_eq = is_eq and self.arguments[i].__eq__(other.arguments[i])
                if not is_eq:
                    return False
            return True
        return False


"""
TODO: stricter typing for logical operators.
well-formed formula versus mere lambda expr; no static verification for now
Reference: Lambda Logic
"""

class AndOpr(LambdaExpr):
    """
    And operator
    (AND a1 a2 a3...) --> a1 & a2 & a3
    """
    def __init__(self, *args):
        self.operands = list(args)
        if len(self.operands) < 2: 
            raise Exception("And-operator requires at least 2 operands.")
    def __str__(self):
        return " & ".join(list(map(str, self.operands)))
    def __repr__(self):
        return f"AND( {', '.join(list(map(repr, self.operands))) } )"
    def __eq__(self, other: object) -> bool:
        if isinstance(other, AndOpr):
            if len(self.operands) != len(other.operands): 
                return False
            for i in range(len(self.operands)):
                if not self.operands[i].__eq__(other.operands[i]):
                    return False
            return True
        return False


class ImpliesOpr(LambdaExpr): 
    def __init__(self, lhs: LambdaExpr, rhs: LambdaExpr):
        self.lhs = lhs
        self.rhs = rhs

        # self._implies_unicode = u'\u2192'
        self._implies_unicode = "->"
    def __str__(self) -> str:
        return f"{str(self.lhs)} {self._implies_unicode} {str(self.rhs)}"
    def __repr__(self) -> str:
        return f"{repr(self.lhs)} {self._implies_unicode} {repr(self.rhs)}"
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ImpliesOpr):
            return self.lhs.__eq__(other.lhs) and self.rhs.__eq__(other.rhs)
        return False
    
class Exists(LambdaExpr): 
    def __init__(self, vars: List[Var], formula: LambdaExpr):
        self.vars = vars
        self.formula = formula 
        # self._exists_unicode = u'\u2203'
        self._exists_unicode = "?"
    
    def __str__(self) -> str:
        return f"{self._exists_unicode}{''.join(list(map(str, self.vars)))}.{str(self.formula)}"
    
    def __repr__(self) -> str:
        return f"{self._exists_unicode}{''.join(list(map(repr, self.vars)))}.{repr(self.formula)}"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Exists):
            is_eq = True
            if len(self.vars) != len(other.vars):
                return False
            for i in range(len(self.vars)):
                is_eq = is_eq and self.vars[i].__eq__(other.vars[i])
                if not is_eq:
                    return False
            return self.formula.__eq__(other.formula)
        return False


class ForAll(LambdaExpr): 
    """
    should have the same attributes as Exists
    """
    def __init__(self, vars: List[Var], formula: LambdaExpr):
        self.vars = vars
        self.formula = formula 
        # self._forall_unicode = u'\u2200'
        self._forall_unicode = "@"
    
    def __str__(self) -> str:
        return f"{self._forall_unicode}{''.join(list(map(str, self.vars)))}.{str(self.formula)}"
    
    def __repr__(self) -> str:
        return f"{self._forall_unicode}{''.join(list(map(repr, self.vars)))}.{repr(self.formula)}"
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ForAll):
            is_eq = True
            if len(self.vars) != len(other.vars):
                return False
            for i in range(len(self.vars)):
                is_eq = is_eq and self.vars[i].__eq__(other.vars[i])
                if not is_eq:
                    return False
            return self.formula.__eq__(other.formula)
        return False
