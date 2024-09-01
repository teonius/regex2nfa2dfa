from dfa import DFAfromNFA
from parser import NFAfromRegex
import sys

def main():
    # Test regular expression (change this for testing)
    inp = "a{2,4}b"
    alphabet = ["a", "b", "c", "d", "e", "f"]  # Define the alphabet used in the DFA

    print("\n========== Regular Expression to Automata Conversion ==========")  
    print(f"Input Regular Expression: {inp}")

    try:
        print("\n[Step 1] Converting Regular Expression to NFA...")
        nfaObj = NFAfromRegex(inp, alphabet=alphabet)  # Pass alphabet to NFA
        nfa = nfaObj.getNFA()

        print("\n[Step 2] Displaying the NFA (Non-deterministic Finite Automaton):")
        nfaObj.displayNFA()

        print("\n[Step 3] Converting NFA to DFA...")
        dfaObj = DFAfromNFA(nfa, alphabet)  # Pass alphabet to DFA
        dfa = dfaObj.getDFA()

        print("\n[Step 4] Displaying the DFA (Deterministic Finite Automaton):")
        dfaObj.displayDFA()

        print("\n[Step 5] Minimizing the DFA...")
        minDFA = dfaObj.getMinimisedDFA()

        print("\n[Step 6] Displaying the Minimized DFA:")
        dfaObj.displayMinimisedDFA()

        print("\n========== Transition Table for the DFA ========== ")
        printDFAtransitionTable(minDFA)
    
    except Exception as e:
        print("\nFailure:", e)

def printDFAtransitionTable(dfa):
    print("\nDFA Transition Table:")
    print(f"{'State':<10}{'Input':<10}{'Next State'}")
    print("-" * 30)
    for from_state, to_states in dfa.transitions.items():
        for to_state, chars in to_states.items():
            for char in chars:
                print(f"{from_state:<10}{char:<10}{to_state}")
    print("-" * 30)

if __name__ == '__main__':
    main()
