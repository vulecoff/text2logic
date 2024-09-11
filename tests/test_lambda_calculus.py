import unittest
from src.lambda_calculus.lambda_ast import Abstr, Var, AndOpr, Const, Apply
from src.lambda_calculus.lambda_processor import beta_reduce, alpha_reduce


class TestLambdaAst(unittest.TestCase): 
    def test_AndOpr_Flatten(self):
        expr = AndOpr(
            Var('x'), 
            AndOpr(
                Var('y'),
                Var('z'), 
                AndOpr(
                    Var('u'), 
                    AndOpr(Var('v'), Var('w'))
                )
            )
        )
        expected = AndOpr(Var('x'), Var('y'), Var('z'), Var('u'), Var('v'), Var('w'))
        actual = expr.flatten()
        self.assertEqual(actual, expected)
    def test_AndOpr_constructor(self):
        self.assertRaises(Exception, AndOpr, Var('x'))

class TestAlphaReduce(unittest.TestCase):
    def test_1(self):
        expr = Abstr(
            [Var('x')],
            Abstr(
                [Var('y')], 
                AndOpr(Var('x'), Var('y'))
        ))

        actual = alpha_reduce(expr, 'x', 'z')
        expected =  Abstr(
            [Var('z')],
            Abstr(
                [Var('y')],
                AndOpr(Var('z'), Var('y'))
        ))
        
        self.assertEqual(actual, expected, 
                         msg="\nExpr: {}.\nActual: {}. \nExpected: {}".format(str(expr), str(actual), str(expected)))
        
    def test_2(self):
        expr = Abstr(
                [Var('f'), Var('x')],
                Apply(
                    Var('f'), 
                    Apply(Var('f'), Var('x'))
                )
            )
        expected = Abstr(
            [Var('f'), Var('y')],
            Apply(Var('f'), Apply(Var('f'),Var('y')))
        )
        actual = alpha_reduce(expr, 'x', 'y')
        self.assertEqual(actual, expected)

class TestBetaReduce(unittest.TestCase):
    def test_1(self):
        expr = Apply(
            Abstr([Var('z')], Var('z')), 
            Abstr([Var('y')], Apply(Var('y'), Var('y'))),
            Abstr([Var('x')], Apply(Var('x'), Var('a'))),
        )
        expected = Apply(Var('a'), Var('a'))
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)
    
    def test_2(self):
        expr = Apply(
            Abstr([Var('z')], Var('z')),
            Abstr([Var('z')], Apply(Var('z'), Var('z'))),
            Abstr([Var('z')], Apply(Var('z'), Var('y')))
        )
        expected = Apply(Var('y'), Var('y'))
        actual = beta_reduce(expr)
        self.assertEqual(actual ,expected)
    def test_3(self):
        expr = Apply(
            Abstr([Var('x'), Var('y')], Apply(Var('x'), Var('y'), Var('y'))),
            Abstr([Var('y')], Var('y')),
            Var('y')
        )
        expected = Apply(Var('y'), Var('y'))
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)
    
    def test_4(self):
        expr = Apply(
            Abstr([Var('x'), Var('y')], Var('x')),
            Var('y'),
            Var('z')
        )
        expected = Var('y')
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)
    def test_infinite_looping(self):
        expr = Apply(
            Abstr([Var('x')], Apply(Var('x'), Var('x'))), 
            Abstr([Var('x')], Apply(Var('x'), Var('x')))
        )
        self.assertRaises(Exception, beta_reduce, expr)
    def test_leftmost_outermost(self):
        """Leftmost_outermost_order does not result in infinite looping"""
        expr = Apply(
            Abstr([Var('x'), Var('y')], Var('y')),
            Apply(
                Abstr([Var('z')], Apply(Var('z'), Var('z'))),
                Abstr([Var('z')], Apply(Var('z'), Var('z')))
            )
        )
        actual = beta_reduce(expr)
        expected = Abstr([Var('y')], Var('y'))
        self.assertEqual(actual, expected)
    def test_7(self):
        expr = Apply(
            Apply(
                Abstr([Var('x'), Var('y')], Apply(Var('x'), Var('y'))), 
                Abstr([Var('y')], Var('y'))
            ), 
            Var('w')
        )
        expected = Var('w')
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)
    def test_with_multiple_alpha_conversion(self):
        expr = Apply(
            Abstr([Var('x'), Var('y'), Var('z')], Apply(Var('x'), Var('y'), Var('z'))),
            Abstr([Var('x')], Apply(Var('x'), Var('x'))),
            Abstr([Var('x')], Var('x')),
            Var('x')
        )
        expected = Var('x')
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)

    def test_and_opr(self):
        expr = Apply(
            Abstr([Var('f'), Var('g'), Var('z')], 
                  AndOpr(Apply(Var('f'), Var('x')), Apply(Var('g'), Var('x')))), 
            Const('P1'), 
            Const('P2')
        )
        expected = Abstr([Var('z')], 
                AndOpr(Apply(Const('P1'), Var('x')), Apply(Const('P2'), Var('x')))
        )
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()