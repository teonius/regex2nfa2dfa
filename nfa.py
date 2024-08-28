from dfa import *

class NFA:
    state_counter = 0
    def __init__(self, start_state=None, accept_states=None):
        self.start_state = start_state
        self.accept_states = accept_states if accept_states is not None else set()

    @staticmethod
    def create_state():
        state = State(NFA.state_counter)
        NFA.state_counter += 1
        return state

    @staticmethod
    def single_symbol_nfa(symbol):
        start = NFA.create_state()
        accept = NFA.create_state()
        start.add_transition(symbol, accept)
        accept_states = {accept}
        return NFA(start, accept_states)

    @staticmethod
    def concatenate(nfa1, nfa2):
        for accept_state in nfa1.accept_states:
            accept_state.add_epsilon_transition(nfa2.start_state)
        return NFA(nfa1.start_state, nfa2.accept_states)

    @staticmethod
    def union(nfa1, nfa2):
        new_start = NFA.create_state()
        new_start.add_epsilon_transition(nfa1.start_state)
        new_start.add_epsilon_transition(nfa2.start_state)
        new_accept_states = nfa1.accept_states.union(nfa2.accept_states)
        return NFA(new_start, new_accept_states)

    @staticmethod
    def kleene_star(nfa):
        new_start = NFA.create_state()
        new_accept = NFA.create_state()
        new_start.add_epsilon_transition(nfa.start_state)
        new_start.add_epsilon_transition(new_accept)
        for accept_state in nfa.accept_states:
            accept_state.add_epsilon_transition(nfa.start_state)
            accept_state.add_epsilon_transition(new_accept)
        return NFA(new_start, {new_accept})