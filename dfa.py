class State:
    def __init__(self, id):
        self.id = id
        self.transitions = {}  # Dictionary to store transitions
        self.epsilon_transitions = set()  # Set to store epsilon transitions

    def add_transition(self, symbol, state):
        if symbol == "ε":
            self.epsilon_transitions.add(state)
        else:
            if symbol not in self.transitions:
                self.transitions[symbol] = set()
            self.transitions[symbol].add(state)

    def add_epsilon_transition(self, state):
        self.add_transition("ε", state)

    def __str__(self):
        return f"State {self.id}"

class DFAState:
    def __init__(self, id, nfa_states):
        self.id = id
        self.nfa_states = nfa_states  # The set of NFA states this DFA state represents
        self.transitions = {}  # Dictionary to store transitions

    def add_transition(self, from_state, to_state, symbol):
        if from_state != to_state or symbol != 'ε':
            if from_state not in self.transitions:
                self.transitions[from_state] = {}
            if symbol not in self.transitions[from_state]:
                self.transitions[from_state][symbol] = set()
            self.transitions[from_state][symbol].add(to_state)

    def __str__(self):
        return f"DFAState {self.id}"

class DFA:
    state_counter = 0

    def __init__(self, start_state, accept_states):
        self.start_state = start_state
        self.accept_states = accept_states
        self.states = set()

    @staticmethod
    def from_nfa(nfa):
        # Create initial DFA state from epsilon closure of NFA start state
        start_nfa_states = DFA.epsilon_closure({nfa.start_state})
        start_dfa_state = DFAState(DFA.state_counter, start_nfa_states)
        DFA.state_counter += 1
        dfa_state_map = {frozenset(start_nfa_states): start_dfa_state}
        accept_states = set()
        if DFA.contains_accept_state(start_nfa_states, nfa.accept_states):
            accept_states.add(start_dfa_state)

        # Worklist for unprocessed DFA states
        worklist = [start_dfa_state]

        dfa = DFA(start_dfa_state, accept_states)

        while worklist:
            dfa_state = worklist.pop(0)
            dfa.states.add(dfa_state)

            # Get all symbols from NFA transitions
            symbols = set()
            for nfa_state in dfa_state.nfa_states:
                symbols.update(nfa_state.transitions.keys())

            # Process each symbol to create new DFA states
            for symbol in symbols:
                # Perform epsilon closure on the set of next NFA states
                next_nfa_states = set()
                for nfa_state in dfa_state.nfa_states:
                    if symbol in nfa_state.transitions:
                        next_nfa_states.update(nfa_state.transitions[symbol])

                next_nfa_states = DFA.epsilon_closure(next_nfa_states)

                if frozenset(next_nfa_states) not in dfa_state_map:
                    next_dfa_state = DFAState(DFA.state_counter, next_nfa_states)
                    DFA.state_counter += 1
                    dfa_state_map[frozenset(next_nfa_states)] = next_dfa_state
                    worklist.append(next_dfa_state)

                    if DFA.contains_accept_state(next_nfa_states, nfa.accept_states):
                        dfa.accept_states.add(next_dfa_state)
                else:
                    next_dfa_state = dfa_state_map[frozenset(next_nfa_states)]

                dfa_state.add_transition(symbol, next_dfa_state)

        return dfa

    @staticmethod
    def epsilon_closure(states):
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            for next_state in state.epsilon_transitions:
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return closure

    @staticmethod
    def contains_accept_state(nfa_states, accept_states):
        # Check if any state in nfa_states is also in accept_states
        for state in nfa_states:
            if state in accept_states:
                return True
        return False



