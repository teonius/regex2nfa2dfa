from parser import *
from tokenizer import *


def validate_regex(alphabet, regex):
    for char in regex:
        if char not in alphabet and char not in {'*', '|', '(', ')', '+', '?', '.'}:
            raise ValueError(f"Invalid character in regex: {char}")
    print(f"Validation successful for regex: {regex}")


def log_nfa(nfa):
    print("NFA Construction:")
    print(f"Start State: {nfa.start_state}")

    # Updated to print the IDs of all final states
    accept_states_ids = [state.id for state in nfa.accept_states]
    print(f"Accept States: {accept_states_ids}")

    for state, transitions in nfa.transitions.items():
        for symbol, next_states in transitions.items():
            for next_state in next_states:
                print(f"Transition: {state} --{symbol}--> {next_state}")


# def log_dfa(dfa, alphabet):
#     print("\nDFA Construction:")
#     print(f"Start State: {dfa.start_state}")
#     print(f"Accept States: {dfa.final_states}")
#     for state, transitions in dfa.transitions.items():
#         for symbol in alphabet:
#             next_state = transitions.get(symbol, None)
#             if next_state:
#                 print(f"Transition: {state} --{symbol}--> {next_state}")
#             else:
#                 print(f"Transition: {state} --{symbol}--> DEAD")


def main():
    # User-defined alphabet and regex
    alphabet = {'a', 'b', 'c'}
    regex = "aaa|bcabb"

    # Validate the regex against the alphabet
    validate_regex(alphabet, regex)

    # Tokenize the regex
    tokenizer = RegexTokenizer(regex, alphabet)
    tokens_combinations = tokenizer.get_tokens_combinations()

    # Assume there's only one valid token combination (no ambiguity)
    tokens = tokens_combinations[0]

    # Parse the tokens into an NFA
    parser = RegexParser(tokens)
    nfa = parser.parse()

    # Log NFA construction details
    log_nfa(nfa)

    # Convert the NFA to a DFA
    #dfa = DFA.from_nfa(nfa)

    # Log DFA construction details including dead states
    #log_dfa(dfa, alphabet)


if __name__ == "__main__":
    main()