from nfa import *
from tokenizer import *

class State:
    def __init__(self, id):
        self.id = id
        self.transitions = {}  # Dictionary to store transitions
        self.epsilon_transitions = set()

    # def add_transition(self, symbol, state):
    #     if symbol == "ε":
    #         self.epsilon_transitions.add(state)
    #     else:
    #         if symbol not in self.transitions:
    #             self.transitions[symbol] = set()
    #         self.transitions[symbol].add(state)
    def add_transition(self, from_state, to_state, symbol):
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = set()
        if to_state not in self.transitions[from_state][symbol]:  # Avoid duplicates
            self.transitions[from_state][symbol].add(to_state)

            print(f"Transition being added: {from_state} --{symbol}--> {to_state}")
    def add_epsilon_transition(self, state):
        self.add_transition("ε", state)

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return f"State {self.id}"





class NFA:
    def __init__(self):
        self.states = set()
        self.transitions = {}
        self.start_state = None
        self.accept_states = set()
        self.state_counter = 0

    def add_state(self, is_final=False):
        state = State(self.state_counter)
        self.state_counter += 1
        self.states.add(state)
        if is_final:
            self.accept_states.add(state)
        return state

    def add_transition(self, from_state, to_state, symbol):
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
        if symbol not in self.transitions[from_state]:
            self.transitions[from_state][symbol] = set()
        if to_state not in self.transitions[from_state][symbol]:  # Avoid duplicates
            self.transitions[from_state][symbol].add(to_state)
            print(f"Transition added: {from_state} --{symbol}--> {to_state}")

    def handle_alternation(self, nfa1, nfa2):
        # Validation to ensure both NFAs have valid start and accept states
        if not nfa1.start_state or not nfa2.start_state:
            raise ValueError("Both NFAs must have a valid start state.")
        if not nfa1.accept_states or not nfa2.accept_states:
            raise ValueError("Both NFAs must have at least one accept state.")

        # Create a new start state for the alternation
        start_state = self.add_state()

        # Create a new accept state for the alternation
        accept_state = self.add_state()

        # Add epsilon transitions from the new start state to the start states of nfa1 and nfa2
        self.add_transition(start_state, nfa1.start_state, 'ε')
        self.add_transition(start_state, nfa2.start_state, 'ε')

        # Add epsilon transitions from the accept states of nfa1 and nfa2 to the new accept state
        for state in nfa1.accept_states:
            self.add_transition(state, accept_state, 'ε')
        for state in nfa2.accept_states:
            self.add_transition(state, accept_state, 'ε')

        # Check for redundant transitions and states
        self._remove_redundant_transitions()

        # Set the new start and accept states for the combined NFA
        self.start_state = start_state
        self.accept_states = {accept_state}

        return self

    def _remove_redundant_transitions(self):
        """Private method to remove any redundant epsilon transitions."""
        for state, transitions in self.transitions.items():
            if 'ε' in transitions:
                reachable_states = transitions['ε']
                # If a state has epsilon transitions to multiple states, ensure they are necessary
                for next_state in list(reachable_states):
                    if next_state == state:
                        # Remove self-loops on epsilon transitions as they are unnecessary
                        reachable_states.remove(next_state)
                    elif next_state in reachable_states:
                        # Ensure no circular epsilon transitions exist
                        if next_state in self.transitions and 'ε' in self.transitions[next_state]:
                            reachable_states.remove(next_state)

    def merge_nfa(self, other_nfa):
        """Method to merge another NFA into the current one."""
        state_mapping = {}
        for state in other_nfa.states:
            new_state = self.add_state()
            state_mapping[state] = new_state

        for state, transitions in other_nfa.transitions.items():
            mapped_state = state_mapping[state]
            for symbol, next_states in transitions.items():
                for next_state in next_states:
                    self.add_transition(mapped_state, state_mapping[next_state], symbol)

        return state_mapping


class RegexParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0
        self.state_count = 0

    def new_state(self):
        state = State(self.state_count)  # Create a State object instead of a string
        self.state_count += 1
        return state

    def parse(self):
        nfa = self.expression()
        if self.index < len(self.tokens):
            raise Exception(f"Unexpected token at end: {self.tokens[self.index]}")
        return nfa

    def expression(self):
        nfa = self.term()
        while self.index < len(self.tokens) and self.tokens[self.index].type == "UNION":
            self.index += 1
            term_nfa = self.term()
            nfa = self.union(nfa, term_nfa)
        return nfa

    def term(self):
        nfa = self.factor()
        while self.index < len(self.tokens) and self.tokens[self.index].type not in ["UNION", "RPAREN"]:
            factor_nfa = self.factor()
            nfa = self.concatenate(nfa, factor_nfa)
        return nfa

    def factor(self):
        nfa = self.base()
        while self.index < len(self.tokens):
            token = self.tokens[self.index]
            if token.type == "KLEENE":
                self.index += 1
                nfa = self.kleene_star(nfa)
            else:
                break
        return nfa

    def create_accept_state(self):
        nfa = NFA()  # Assuming you're working with the NFA class
        accept_state = nfa.add_state(is_final=True)
        return accept_state

    def base(self):
        token = self.tokens[self.index]
        if token.type == "LPAREN":
            self.index += 1
            nfa = self.expression()
            if self.tokens[self.index].type != "RPAREN":
                raise Exception("Mismatched parentheses")
            self.index += 1
        else:
            self.index += 1
            nfa = self.character_nfa(token.value)
        return nfa

    def union(self, nfa1, nfa2):
        nfa = NFA()
        start_state = nfa.add_state()  # New start state for the union
        accept_state = nfa.add_state(is_final=True)  # New final state for the union

        # Create epsilon transitions from the new start state to the start states of nfa1 and nfa2
        nfa.add_transition(start_state, nfa1.start_state, 'ε')
        nfa.add_transition(start_state, nfa2.start_state, 'ε')

        # Transition from all final states of nfa1 and nfa2 to the new final state
        for state in nfa1.accept_states:
            nfa.add_transition(state, accept_state, 'ε')

        for state in nfa2.accept_states:
            nfa.add_transition(state, accept_state, 'ε')

        # Merge states and transitions from both NFAs into the new NFA
        nfa.states.update(nfa1.states)
        nfa.states.update(nfa2.states)
        nfa.transitions.update(nfa1.transitions)
        nfa.transitions.update(nfa2.transitions)

        # Set the new start state and the set of accept states
        nfa.start_state = start_state
        nfa.accept_states = {accept_state}

        return nfa

    @staticmethod
    def concatenate(nfa1, nfa2):
        accept_state1 = nfa1.add_state(is_final=True)
        accept_state2 = nfa2.add_state(is_final=True)
        # Initialize state mapping and index tracker
        state_mapping = {}
        index = max(state.id for state in nfa1.states) + 1

        # Link final states of nfa1 to the start state of nfa2 directly
        for accept_state1 in nfa1.accept_states:
            if 'ε' not in nfa1.transitions.get(accept_state1, {}):
                nfa1.add_transition(accept_state1, nfa2.start_state, 'ε')

        # Map states from nfa2 to new states in nfa1, excluding the start state of nfa2
        for state in nfa2.states:
            if state != nfa2.start_state:
                new_state = State(index)
                state_mapping[state] = new_state
                nfa1.add_state(new_state)
                index += 1
        # Remap transitions from nfa2 to nfa1 using the state mapping
        for state, transitions in nfa2.transitions.items():
            mapped_state = state_mapping.get(state, nfa2.start_state)
            for symbol, next_states in transitions.items():
                for next_state in next_states:
                    mapped_next_state = state_mapping.get(next_state, nfa2.start_state)
                    if symbol not in nfa1.transitions.get(mapped_state, {}):
                        nfa1.add_transition(mapped_state, mapped_next_state, symbol)
                    elif mapped_next_state not in nfa1.transitions[mapped_state][symbol]:
                        nfa1.add_transition(mapped_state, mapped_next_state, symbol)
        # Accumulate all accept states from nfa2
        nfa1.accept_states.update(state_mapping.get(state, nfa2.start_state) for state in nfa2.accept_states)
        print(f"Creating transition from {state} to {accept_state1} on ε")
        return nfa1

    def kleene_star(self, nfa):
        new_nfa = NFA()
        start_state = new_nfa.add_state()
        accept_state = new_nfa.add_state(is_final=True)  # Set as final state

        new_nfa.set_start_state(start_state)

        # ε-transition from new start to the original start and to the new final
        new_nfa.add_transition(start_state, nfa.start_state, 'ε')
        new_nfa.add_transition(start_state, accept_state, 'ε')

        # Add all states and transitions of the original NFA
        new_nfa.states.update(nfa.states)
        new_nfa.transitions.update(nfa.transitions)

        # ε-transition from original final states back to the original start state
        # and to the new final state
        for final in nfa.accept_states:
            new_nfa.add_transition(final, nfa.start_state, 'ε')
            new_nfa.add_transition(final, accept_state, 'ε')
        new_nfa.accept_states = {accept_state}
        print(f"Creating transition from {final} to {accept_state} on ε")
        return new_nfa

    def character_nfa(self, char):
        nfa = NFA()

        # Create new states within the NFA context
        start_state = nfa.add_state()  # Start state
        accept_state = nfa.add_state(is_final=True)  # Final state

        # Set the start state of the NFA
        nfa.start_state = start_state  # Directly set the start_state attribute

        # Add the transition between the start state and the final state
        nfa.add_transition(start_state, accept_state, char)

        # Explicitly set the final states (optional, since it's done in add_state)
        nfa.accept_states = {accept_state}

        return nfa





