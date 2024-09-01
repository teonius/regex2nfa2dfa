import unittest
from dfa import DFAfromNFA
from parser import NFAfromRegex


class TestRegexToDFA(unittest.TestCase):

    def repeat_test(self, test_func, repeat=10):
        failures = 0
        for _ in range(repeat):
            try:
                test_func()
            except AssertionError as e:
                failures += 1
                last_error = e
        if failures == repeat:
            raise last_error

    def assertDFAProperties(self, dfa, expected_states, expected_transitions, expected_start_state,
                            expected_final_states):
        # Check if the start state is as expected
        self.assertEqual(dfa.startstate, expected_start_state,
                         f"Start state mismatch: Expected {expected_start_state}, got {dfa.startstate}")

        # Check if all final states are as expected
        self.assertEqual(set(dfa.finalstates), set(expected_final_states),
                         f"Final states mismatch: Expected {expected_final_states}, got {dfa.finalstates}")

        # Check if transitions match the expected transitions
        for from_state, char_to_state in expected_transitions.items():
            for char, to_state in char_to_state.items():
                actual_transitions = dfa.gettransitions(from_state, char)
                self.assertIn(to_state, actual_transitions,
                              f"Transition mismatch on '{char}': Expected {to_state} from {from_state}, got {actual_transitions}")

        # Check if states match the expected states
        self.assertEqual(set(dfa.states), set(expected_states),
                         f"States mismatch: Expected {expected_states}, got {dfa.states}")


    def test_simple_string(self):
        def inner_test():
            regex = "abcdab"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2, 3, 4, 5, 6, 7}
            expected_transitions = {
                1: {"a": 2},
                2: {"b": 3},
                3: {"c": 4},
                4: {"d": 5},
                5: {"a": 6},
                6: {"b": 7},
            }
            expected_start_state = 1
            expected_final_states = [7]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)
            self.repeat_test(inner_test)

    def test_alteration_operator(self):
        def inner_test():
            regex = "ab+cd"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2, 3, 4}
            expected_transitions = {
                1: {"a": 2},
                2: {"b": 4},
                1: {"c": 3},
                3: {"d": 4},
            }
            expected_start_state = 1
            expected_final_states = [4]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)
        self.repeat_test(inner_test)

    def test_kleene_star(self):
        def inner_test():
            regex = "aa*bb"
            alphabet = ["a", "b"]
            expected_states = {1, 2, 3, 4}
            expected_transitions = {
                1: {"a": 2},
                2: {"a": 2, "b": 3},
                3: {"b": 4},
            }
            expected_start_state = 1
            expected_final_states = [4]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)
        self.repeat_test(inner_test)

    def test_kleene_star_and_alteration(self):
        def inner_test():
            regex = "ab*+cd"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2, 3, 4}
            expected_transitions = {
                1: {"a": 2},
                2: {"b": 2},
                1: {"c": 3},
                3: {"d": 4},
            }
            expected_start_state = 1
            expected_final_states = [2, 4]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)
        self.repeat_test(inner_test)

    def test_repetition_single(self):
        def inner_test():
            regex = "a{3}b"
            alphabet = ["a", "b"]
            expected_states = {1, 2, 3, 4, 5}
            expected_transitions = {
                1: {"a": 2},
                2: {"a": 3},
                3: {"a": 4},
                4: {"b": 5},
            }
            expected_start_state = 1
            expected_final_states = [5]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_repetition_from_to(self):
        def inner_test():
            regex = "a{2,4}b"
            alphabet = ["a", "b"]
            expected_states = {1, 2, 3, 4, 5, 6}
            expected_transitions = {
                1: {"a": 2},
                2: {"a": 3},
                3: {"a": 5, "b": 4},
                4: {"b": 5},
                5: {"a": 6, "b": 4},
                6: {"b": 4},
            }
            expected_start_state = 1
            expected_final_states = [4]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_repetition_infinite(self):
        def inner_test():
            regex = "a{2,}b"
            alphabet = ["a", "b"]
            expected_states = {1, 2, 3}
            expected_transitions = {
                1: {"a": 2},
                2: {"a": 2},
                2: {"b": 3},
            }
            expected_start_state = 1
            expected_final_states = [3]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_parentheses(self):
        def inner_test():
            regex = "(ab(cd))"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2, 3, 4, 5}
            expected_transitions = {
                1: {"a": 2},
                2: {"b": 3},
                3: {"c": 4},
                4: {"d": 5},
            }
            expected_start_state = 1
            expected_final_states = [5]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_nested_parentheses(self):
        def inner_test():
            regex = "a(b(cd)e)f"
            alphabet = ["a", "b", "c", "d", "e", "f"]
            expected_states = {1, 2, 3, 4, 5, 6, 7}
            expected_transitions = {
                1: {"a": 2},
                2: {"b": 3},
                3: {"c": 4},
                4: {"d": 5},
                5: {"e": 6},
                6: {"f": 7},
            }
            expected_start_state = 1
            expected_final_states = [7]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_combination_complex(self):
        def inner_test():
            regex = "(ab+c)*d"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2, 3}
            expected_transitions = {
                1: {"a": 2, "c": 1, "d": 3},
                2: {"b": 1},
            }
            expected_start_state = 1
            expected_final_states = [3]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_alteration_with_kleene_star(self):
        def inner_test():
            regex = "a+b*"
            alphabet = ["a", "b"]
            expected_states = {1, 2, 3}
            expected_transitions = {
                1: {"a": 2, "b": 3},
                3: {"b": 3}
            }
            expected_start_state = 1
            expected_final_states = [1, 2, 3]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_alteration_with_concatenation(self):
        def inner_test():
            regex = "a+bc"
            alphabet = ["a", "b", "c"]
            expected_states = {1, 2, 3}
            expected_transitions = {
                1: {"a": 2},
                1: {"b": 3},
                3: {"c": 2}
            }
            expected_start_state = 1
            expected_final_states = [2]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_multiple_alteration(self):
        def inner_test():
            regex = "a+b+c+d"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2}
            expected_transitions = {
                1: {"a": 2, "b": 2, "c": 2, "d": 2},
            }
            expected_start_state = 1
            expected_final_states = [2]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_nested_alteration(self):
        def inner_test():
            regex = "(a+b)+(c+d)"
            alphabet = ["a", "b", "c", "d"]
            expected_states = {1, 2}
            expected_transitions = {
                1: {"a": 2, "b": 2, "c": 2, "d": 2},
            }
            expected_start_state = 1
            expected_final_states = [2]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)

    def test_complex_alteration_with_kleene_and_concat(self):
        def inner_test():
            regex = "a+(b*c)+de"
            alphabet = ["a", "b", "c", "d", "e"]
            expected_states = {1, 2, 3, 4}
            expected_transitions = {
                1: {"a": 2, "b": 3, "c": 2, "d": 4},
                3: {"b": 3, "c": 2},
                4: {"e": 2}
            }
            expected_start_state = 1
            expected_final_states = [2]

            nfa = NFAfromRegex(regex, alphabet).getNFA()
            dfa = DFAfromNFA(nfa, alphabet).getMinimisedDFA()
            self.assertDFAProperties(dfa, expected_states, expected_transitions, expected_start_state,
                                     expected_final_states)

        self.repeat_test(inner_test)
if __name__ == '__main__':
    unittest.main()
