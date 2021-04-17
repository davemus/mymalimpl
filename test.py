#!/bin/python3

import unittest
import subprocess
from step2 import rep as rep2
from step3 import rep as rep3
from step4 import rep as rep4
from step5 import rep as rep5
from step6 import rep as rep6, setup_fns as set6
from step7 import rep as rep7, setup_fns as set7
from step8 import rep as rep8, setup_fns as set8
from step9 import rep as rep9, setup_fns as set9
from mal_types import MalType
from errors import MalTypeError, NotFound


SKIP_TCO_TEST = True


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
        with self.assertRaises(MalType):
            self.rep('(def! a)')

    def test_wrong_called_let(self):
        with self.assertRaises(MalType):
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
        with self.assertRaises((MalType, ValueError)):
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

    @unittest.skipIf(SKIP_TCO_TEST, 'This test is disabled due to performance issues')
    def test_tco(self):
        self.rep('(def! sum2 (fn* (n acc) (if (= n 0) acc (sum2 (- n 1) (+ n acc)))))')  # noqa
        self.myTest('(sum2 10 0)', '55')
        self.myTest('(sum2 10000 0)', '50005000')

    @unittest.skipIf(SKIP_TCO_TEST, 'This test is disabled due to performance issues')
    def test_tco_2(self):
        self.rep('(def! foo (fn* (n) (if (= n 0) 0 (bar (- n 1)))))')
        self.rep('(def! bar (fn* (n) (if (= n 0) 0 (foo (- n 1)))))')
        self.myTest('(foo 10000)', '0')


class TestFile:
    def __init__(self, file_name, data):
        self.file_name = file_name
        self.data = data

    def __enter__(self):
        with open(self.file_name, 'w') as f:
            f.write(self.data)
        return None

    def __exit__(self, type, value, traceback):
        subprocess.run(['rm', self.file_name])


class Step6Test(Step5Test):
    rep = staticmethod(rep6)
    setup = staticmethod(set6)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setup()

    def assertCLI(self, commands, expected_in_stdout):
        proc_result = subprocess.run(commands, capture_output=True)
        self.assertIn(expected_in_stdout, proc_result.stdout.decode('unicode-escape'))

    def test_eval(self):
        self.myTest('(eval (list + 2 5))', '7')

    def test_load_file(self):
        with TestFile('test.mal', '(def! variable-from-file 42)'):
            self.rep('(load-file "test.mal")')
            self.myTest('variable-from-file', '42')

    def test_atom(self):
        self.myTest('(atom? (atom 42))', 'true')

    def test_deref(self):
        self.myTest('(deref (atom "str"))', 'str')

    def test_reset(self):
        self.rep('(def! atom42 (atom 42))')
        self.myTest('(deref atom42)', '42')
        self.myTest('(reset! atom42 43)', '43')
        self.myTest('(deref atom42)', '43')

    def test_swap(self):
        self.rep('(def! atom42 (atom 42))')
        self.rep('(def! add-1 (fn* (arg) (+ arg 1)))')
        self.myTest('(swap! atom42 add-1)', '43')

    def test_short_defer(self):
        self.rep('(def! atom42 (atom 42))')
        self.myTest('@atom42', '42')

    def test_run_program_from_cli(self):
        with TestFile('test.mal', '(def! variable-from-file2 44)\nvariable-from-file2'):
            self.assertCLI(['./step6.py', 'test.mal'], '44')


class Step7Test(Step6Test):
    rep = staticmethod(rep7)
    setup = staticmethod(set7)

    def test_cons(self):
        self.myTest('(cons 1 (list 2 3))', '(1 2 3)')

    def test_concat(self):
        self.myTest('(concat (list 1) (list 2) (list 3 4))', '(1 2 3 4)')

    def test_quote(self):
        self.myTest('(quote (1 2 3))', '(1 2 3)')
        self.myTest('(quote undefined)', '\'undefined')

    def test_quasiquote(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('(quasiquote (1 nested 4))', '(1 \'nested 4)')

    def test_quasiquote_unquote(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('(quasiquote (1 (unquote nested) 4))', '(1 (2 3) 4)')

    def test_quasiquote_splice_unquote(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('(quasiquote (1 (splice-unquote nested) 4))', '(1 2 3 4)')

    def test_shortcut_quote(self):
        self.myTest('\'(1 2 3))', '(1 2 3)')
        self.myTest('\'undefined', '\'undefined')

    def test_shortcut_quasiquote(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('`(1 nested 4)', '(1 \'nested 4)')

    def test_shortcut_quasiquote_unquote(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('`(1 ~nested 4)', '(1 (2 3) 4)')

    def test_shortcut_quasiquote_splice_unquote(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('`(1 ~@nested 4)', '(1 2 3 4)')

    def test_quote_vectors(self):
        self.rep('(def! nested (list 2 3))')
        self.myTest('(quote [1 nested 4])', '[1 \'nested 4]')

    def test_vec(self):
        self.myTest('(vec 1 2 3)', '[1 2 3]')

    def test_concat_list_and_vector(self):
        self.myTest('(concat [1] (list 2) [3])', '(1 2 3)')

    def test_cons_vector(self):
        self.myTest('(cons 1 [2 3])', '(1 2 3)')

    def test_run_program_with_arguments_different_types(self):
        with TestFile('test.mal', '(prn *ARGS*)'):
            self.assertCLI(['./step7.py', 'test.mal', '1', '2', '3', "string"], '(1 2 3 string)')


class Step8Test(Step7Test):
    rep = staticmethod(rep8)
    setup = staticmethod(set8)

    def test_and(self):
        self.myTest('(and true false)', 'false')
        self.myTest('(and true true)', 'true')
        self.myTest('(and true true true false)', 'false')

    def test_or(self):
        self.myTest('(or true false)', 'true')
        self.myTest('(or false false)', 'false')
        self.myTest('(or false false false true)', 'true')

    def test_very_simple_macros(self):
        self.rep('(defmacro! remove-code (fn* (& args) nil))')
        self.myTest('(remove-code (+ undefined undefined))', 'nil')

    def test_unless_macros(self):
        self.rep('(defmacro! unless (fn* (pred a b) `(if ~pred ~b ~a)))')
        self.myTest('(unless false 7 8)', '7')

    def test_unless2_macros(self):
        self.rep('(defmacro! unless2 (fn* (pred a b) (list \'if (list \'not pred) a b)))')
        self.myTest('(unless2 false 7 8)', '7')
        self.myTest('(unless2 true 7 8)', '8')

    def test_first_rest_with_empty_list(self):
        self.myTest('(first ())', 'nil')
        self.myTest('(rest ())', '()')

    def test_nth(self):
        self.myTest('(nth (list 1 2 3) 2)', '3')
        self.myTest('(nth (list 1 2 3) 1)', '2')
        self.myTest('(nth (list 1 2 3) 0)', '1')

    def test_nth_with_invalid_index(self):
        self.myTest('(nth (list 1 2 3) 4)', 'nil')


class Step9Test(Step8Test):
    rep = staticmethod(rep9)
    setup = staticmethod(set9)

    def test_throw_try_catch(self):
        self.myTest('(try* (do (throw "2") "1") (catch* excepted excepted))', "2")

    def test_map(self):
        self.myTest('(map (fn* [arg] (+ arg 1)) (list 1 2 3))', '(2 3 4)')
        self.myTest('(map (fn* [arg] (* arg 2)) [1 2 3])', '(2 4 6)')

    def test_apply(self):
        self.myTest('(apply pr-str 1 2 \'(3 4) 5)', '1 2 3 4 5')

    def test_symbol(self):
        self.myTest('(symbol? (symbol "spam"))', 'true')
        self.myTest('(symbol? \'spam)', 'true')
        self.myTest('(symbol? "spam")', 'false')

    def test_vector(self):
        self.myTest('(vector? (vector 1 2 3))', 'true')
        self.myTest('(vector? [1 2 3])', 'true')
        self.myTest('(vector? \'(1 2 3)', 'false')

    def test_hash_map(self):
        self.myTest('(map? (hash-map "1" 2))', 'true')
        self.myTest('(map? {"1" 2})', 'true')
        self.myTest('(map? [1 2])', 'false')

    def test_keys_values(self):
        self.rep('(def! mymap {"1" 2 "3" 4})')
        self.myTest('(keys mymap)', '(1 3)')
        self.myTest('(values mymap)', '(2 4)')

    def test_get_contains(self):
        self.rep('(def! mymap {"1" 2 "3" 4})')
        self.myTest('(contains? mymap "1")', 'true')
        self.myTest('(contains? mymap "2")', 'false')
        self.myTest('(get mymap "1")', '2')
        self.myTest('(get mymap "2")', 'nil')

    def test_assoc_dissoc(self):
        self.rep('(def! mymap {"1" 2 "3" 4})')
        self.rep('(def! shortmap (dissoc mymap "3"))')
        self.rep('(def! longmap (assoc mymap "5" 6))')
        self.myTest('mymap', '{1 2, 3 4}')
        self.myTest('shortmap', '{1 2}')
        self.myTest('longmap', '{1 2, 3 4, 5 6}')

    def test_keyword(self):
        self.myTest('(keyword? (keyword "a"))', 'true')
        self.myTest('(keyword? :a)', 'true')
        self.myTest('(keyword? "a")', 'false')


if __name__ == '__main__':
    unittest.main()
