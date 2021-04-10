#!/bin/python3

import unittest
from step2 import rep as rep2
from step3 import rep as rep3
from errors import MalTypeError, SpecialFormError, NotFound


class Step2Test(unittest.TestCase):
    rep = staticmethod(rep2)

    def myTest(self, mal_expression, evaluated_expression):
        self.assertEqual(
            self.rep(mal_expression),
            evaluated_expression
        )

    def test_addition(self):
        self.myTest('(+ 1 1 1)', '3')

    def test_substraction(self):
        self.myTest('(- 1 1 1)', '-1')

    def test_multiplication(self):
        self.myTest('(* 2 2 2)', '8')

    def test_division(self):
        self.myTest('(/ 2 2)', '1')

    def test_compounds_expression(self):
        self.myTest('(* 2 (+ 2 2))', '8')

    def test_vector(self):
        self.myTest('[1 2 (+ 1 2)]', '[1 2 3]')

    def test_hashmap(self):
        self.myTest('{:a 1, :b (+ 1 1)}', '{:a 1, :b 2}')

    def test_call_with_wrong_arg_type(self):
        with self.assertRaises(MalTypeError):
            self.rep('(+ "1" 1)')

    def test_call_not_function(self):
        with self.assertRaises(MalTypeError):
            self.rep('(1 1 1')


class Step3Test(Step2Test):
    rep = staticmethod(rep3)

    def test_def(self):
        self.rep('(def! a 1)')
        self.myTest('a', '1')

    def test_let(self):
        self.myTest('(let* (c 2) c)', '2')

    def test_wrong_called_def(self):
        with self.assertRaises(SpecialFormError):
            self.rep('(def! a)')

    def test_wrong_called_let(self):
        with self.assertRaises(SpecialFormError):
            self.rep('(let* (a) a)')

    def test_access_not_bound_symbol(self):
        with self.assertRaises(NotFound):
            self.rep('(+ a 2)')


if __name__ == '__main__':
    unittest.main()
