import unittest
from src.lambda_calculus.lambda_ast import Abstr, Var, AndOpr, Const, Apply, Exists, ImpliesOpr,ForAll, Neg
from src.lambda_calculus.lambda_processor import beta_reduce, alpha_reduce, free_vars, flatten, bound_vars


class TestLambdaAst(unittest.TestCase): 
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

    def test_logic_opr_1(self):
        # TODO: separation out into logical opers test
        and_expr = Abstr([Var('p'), Var('q')],Apply(Var('p'), Var('q'), Var('p')))
        true_expr= Abstr([Var('x'), Var('y')],Var('x'))
        false_expr = Abstr([Var('x'), Var('y')],Var('y'))
        actual = beta_reduce(Apply(and_expr, true_expr, false_expr))
        self.assertEqual(actual, false_expr)
    
    def test_neg(self):
        expr = Apply(
            Abstr([Var('f'), Var('x')], Neg(Apply(Var('f'), Var('x')))),
            Abstr([Var('x')], Apply(Const("pred"), Var('x')))
        )
        expected = Abstr([Var('x')], Neg(Apply(Const('pred'), Var('x'))))
        actual = beta_reduce(expr)
        self.assertEqual(actual, expected)

class TestFreeBoundVars(unittest.TestCase):
    def test_free_vars(self):
        expr = Exists(
            [Var('x')], 
            Apply(Const("father"), Var('x'))
        )
        self.assertEqual(len(free_vars(expr)), 0)
        expr = ForAll(
            [Var('x'), Var('y')], 
            Apply(Var('f'), Var('y'), Var('x'))
        )
        free = free_vars(expr)
        self.assertTrue("f" in free)
        self.assertFalse("x" in free or "y" in free)
        expr = Abstr(
            [Var('x')], 
            Exists(
                [Var('y')], 
                Apply(Const("is"), Var('x'), Var('y'))
            )
        )
        free = free_vars(expr)
        self.assertTrue(len(free) == 0)

    def test_bound_vars(self):
        expr = Abstr([Var('x')], Neg(Var('x')))
        self.assertTrue('x' in bound_vars(expr))
        self.assertTrue('x' not in bound_vars(expr.body))


class TestFlatten(unittest.TestCase):
    def test_1(self):
        expr = Abstr(
            [Var('x'), Var('y')],
            Exists(
                [Var('z')], 
                AndOpr(
                    Apply(Const('A'), Var('x')), 
                    AndOpr(
                        Apply(Const("B"), Var('y')), 
                        Apply(Const("C"), Var('z')),
                        AndOpr(
                            Apply(Const("C"), Var('x')),
                            Abstr([Var('t')], AndOpr(Var('t'), Var('y')))
                        ),
                    )
                )
            )
        )
        expected = Abstr(
            [Var('x'), Var('y')],
            Exists([Var('z')], AndOpr(
                Apply(Const('A'), Var('x')),
                Apply(Const("B"), Var('y')),
                Apply(Const("C"), Var('z')),
                Apply(Const("C"), Var('x')),
                Abstr([Var('t')], AndOpr(Var('t'), Var('y')))
            ))
        )
        self.assertEqual(flatten(expr), expected)
    def test_2(self):
        expr = AndOpr(
            Exists([Var('x')], Apply(Const('F'), Var('x'))),
            Abstr(
                [Var('y'), Var('z')], 
                Exists([Var('t')], Apply(Var('y'), Var('t')))
            )
        )
        expected = Exists(
            [Var('x')], 
            AndOpr(
                Apply(Const('F'), Var('x')),
                Abstr(
                [Var('y'), Var('z')], 
                Exists([Var('t')], Apply(Var('y'), Var('t')))
            )
            )
        )
        actual = flatten(expr)
        self.assertEqual(actual, expected)
    def test_3(self):
        expr = AndOpr(Exists(
            [Var('x'), Var('y')], 
            ForAll([Var('z')], Apply(Const('P'), Var('x'))),  
        ), Apply(Const("P"), Var('y')))
        expected = ForAll([Var('z')], 
                          Exists([Var('x'), Var('y')],
                                 AndOpr(Apply(Const('P'), Var('x')), Apply(Const("P"), Var('y'))) 
        ))
        actual = flatten(expr)
        self.assertEqual(actual, expected)
    def test_AND_Opr(self):
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
        actual = flatten(expr)
        self.assertEqual(actual, expected)
    
    def test_implies(self):
        expr = ImpliesOpr(
            ForAll([Var('x')], Apply(Const("P"), Var('x'))), 
            Exists([Var('y')], Apply(Const("P"), Var("y")))
        )
        actual =  flatten(expr)
        self.assertEqual(actual, expr, msg="Should not change. B/c this has not been implemented.")
    


if __name__ == "__main__":
    unittest.main()