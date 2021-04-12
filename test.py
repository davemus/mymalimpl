#!/bin/python3

import unittest
from step2 import rep as rep2
from step3 import rep as rep3
from step4 import rep as rep4
from step5 import rep as rep5
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


class Step4Test(Step3Test):
    rep = staticmethod(rep4)

    def test_function_repr(self):
        self.myTest('(fn* (a) a)', '#function')

    def test_call_function(self):
        self.myTest('( (fn* (a) (* a a)) 2', '4')

    def test_call_function_many_args(self):
        self.myTest('( (fn* (a b) (/ (+ a b) 2)) 2 4 )', '3')

    def test_call_function_wrong_number_of_args(self):
        with self.assertRaises((SpecialFormError, ValueError)):
            self.rep('( (fn* (a b) (+ a b)) 4 )')

    def test_function_can_be_stored_in_env(self):
        self.rep('(def! add-one (fn* (a) (+ a 1)))')
        self.myTest('add-one', '#function')
        self.myTest('(add-one 1)', '2')

    def test_do_works(self):
        self.myTest('(do 1 2)', '2')

    def test_difficult_do_works(self):
        self.myTest('(do (def! a 2) (+ a a))', '4')

    def test_if_works(self):
        self.myTest('(if true 1 2)', '1')
        self.myTest('(if false 1 2)', '2')

    def test_access_not_bound_symbol(self):
        with self.assertRaises(NotFound):
            self.rep('(+ not-defined 1)')

    def test_check_list(self):
        self.myTest('(list? (list 1 2))', 'true')
        self.myTest('(list? 1)', 'false')

    def test_create_list(self):
        self.myTest('(list 1 2)', '(1 2)')

    def test_count(self):
        self.myTest('(count (list 1 2 5))', '3')
        self.myTest('(count ())', '0')

    def test_equal(self):
        self.myTest('(= 1 1)', 'true')
        self.myTest('(= 1 2)', 'false')

    def test_equality_lists(self):
        self.myTest('(= (list 1 2 3) (list 1 2 3))', 'true')
        self.myTest('(= (list 1 2 3) (list 3 2 1))', 'false')

    def test_empty(self):
        self.myTest('(empty? (list 1))', 'false')
        self.myTest('(empty? ())', 'true')

    def test_lt(self):
        self.myTest('(< 1 2)', 'true')
        self.myTest('(< 2 1)', 'false')
        with self.assertRaises(MalTypeError):
            self.rep('(< 1 "2")')

    def test_le(self):
        self.myTest('(<= 1 2)', 'true')
        self.myTest('(<= 1 1)', 'true')
        self.myTest('(<= 2 1)', 'false')
        with self.assertRaises(MalTypeError):
            self.rep('(<= 1 "2")')

    def test_gt(self):
        self.myTest('(> 1 2)', 'false')
        self.myTest('(> 2 1)', 'true')
        with self.assertRaises(MalTypeError):
            self.rep('(> 1 "2")')

    def test_ge(self):
        self.myTest('(>= 1 2)', 'false')
        self.myTest('(>= 1 1)', 'true')
        self.myTest('(>= 2 1)', 'true')
        with self.assertRaises(MalTypeError):
            self.rep('(>= 1 "2")')

    def test_not(self):
        self.myTest('(not false)', 'true')
        self.myTest('(not true)', 'false')

    def test_first_rest_list(self):
        self.myTest('(first (list 1 2))', '1')
        self.myTest('(rest (list 1 2))', '(2)')

    def test_first_rest_vector(self):
        self.myTest('(first [1 2])', '1')
        self.myTest('(rest [1 2])', '[2]')

    def test_variadic_parameters(self):
        self.rep('(def! list_alias (fn* (& args) args))')
        self.myTest('(list_alias 1 2 3)', '(1 2 3)')


class Step5Test(Step4Test):
    rep = staticmethod(rep5)

    def test_tco(self):
        self.rep('(def! sum2 (fn* (n acc) (if (= n 0) acc (sum2 (- n 1) (+ n acc)))))')  # noqa
        self.myTest('(sum2 10 0)', '55')
        self.myTest('(sum2 10000 0)', '50005000')

    def test_tco_2(self):
        self.rep('(def! foo (fn* (n) (if (= n 0) 0 (bar (- n 1)))))')
        self.rep('(def! bar (fn* (n) (if (= n 0) 0 (foo (- n 1)))))')
        self.myTest('(foo 10000)', '0')


if __name__ == '__main__':
    unittest.main()
