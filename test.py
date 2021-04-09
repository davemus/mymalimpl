#!/bin/python3

import unittest
from step2 import rep as rep2
from errors import MalTypeError


class Step2TestCase(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(rep2('(+ 1 1 1)'), '3')

    def test_substraction(self):
        self.assertEqual(rep2('(- 1 1 1)'), '-1')

    def test_multiplication(self):
        self.assertEqual(rep2('(* 2 2 2)'), '8')

    def test_division(self):
        self.assertEqual(rep2('(/ 2 2)'), '1')

    def test_compounds_expression(self):
        self.assertEqual(rep2('(* 2 (+ 2 2))'), '8')

    def test_vector(self):
        self.assertEqual(rep2('[1 2 (+ 1 2)]'), '[1 2 3]')

    def test_hashmap(self):
        self.assertEqual(rep2('{:a 1, :b (+ 1 1)}'), '{:a 1, :b 2}')

    def test_call_with_wrong_arg_type(self):
        with self.assertRaises(MalTypeError):
            rep2('(+ "1" 1)')

    def test_call_not_function(self):
        with self.assertRaises(MalTypeError):
            rep2('(1 1 1')


if __name__ == '__main__':
    unittest.main()
